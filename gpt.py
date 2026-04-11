#!/usr/bin/env python3
"""Interactive CLI wrapper around OpenAI's Responses API."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import secrets
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List

from openai import OpenAI

COMMAND_MARKER_PREFIX = "[[RUN:"
COMMAND_MARKER_SUFFIX = "]]"
COMMAND_TIMEOUT_SECONDS = 120
MAX_MODEL_OUTPUT_CHARS = 12000
MODEL_OUTPUT_HEAD_CHARS = 5000
MODEL_OUTPUT_TAIL_CHARS = 5000
VERSION = "gpt.py SNAPSHOT 0410261708"
SPINNER_FRAMES = ("/", "-", "\\", "|")
SPINNER_INTERVAL_SECONDS = 0.1


def get_platform_name() -> str:
    """Return a user-friendly platform label for prompt construction."""
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    if system == "Windows":
        return "Windows"
    if system == "Linux":
        return "Linux"
    return system or "unknown platform"


def get_command_shell_profile() -> Dict[str, object]:
    """Return shell execution details for the current operating system."""
    if os.name == "nt":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell:
            shell_name = Path(powershell).name
            return {
                "name": shell_name,
                "example": "Get-ChildItem",
                "admin_hint": (
                    "If administrator privileges are required, prefer a PowerShell "
                    "command that clearly indicates elevation is needed instead of using sudo."
                ),
                "runner": [powershell, "-NoProfile", "-Command"],
            }
        comspec = os.environ.get("COMSPEC") or "cmd.exe"
        return {
            "name": Path(comspec).name,
            "example": "dir",
            "admin_hint": (
                "If administrator privileges are required, describe the need clearly "
                "because Windows does not use sudo."
            ),
            "runner": [comspec, "/c"],
        }

    shell_path = os.environ.get("SHELL") or shutil.which("bash") or "/bin/sh"
    shell_name = Path(shell_path).name
    return {
        "name": shell_name,
        "example": "ls -la",
        "admin_hint": (
            "Include 'sudo' directly in the command whenever elevated privileges are required."
        ),
        "runner": [shell_path, "-lc"],
    }


def build_shell_instructions() -> str:
    """Describe how the model should emit commands for the active shell."""
    shell_profile = get_command_shell_profile()
    platform_name = get_platform_name()
    return (
        "If you need me to execute a local shell command, output one line per command "
        "prefixed with the provided marker. "
        f"Target the current platform: {platform_name}. "
        f"Use commands compatible with the current shell: {shell_profile['name']}. "
        f"Example: '<MARKER> {shell_profile['example']}'. "
        f"{shell_profile['admin_hint']} "
        "All commands will be confirmed interactively before execution. Avoid destructive "
        "commands unless the user explicitly insists."
    )


def get_default_system_prompt() -> str:
    """Build the default system prompt with platform-specific shell guidance."""
    platform_name = get_platform_name()
    shell_name = str(get_command_shell_profile()["name"])
    return (
        "You are a senior systems engineering assistant. "
        f"The user is working on {platform_name} and local commands should target the "
        f"{shell_name} shell. Prefer concise explanations, point out pitfalls, and do not "
        "assume Linux-specific tools unless they are confirmed to exist."
    )


def is_privileged_command(command: str) -> bool:
    """Return True when a command appears to request elevated privileges."""
    stripped = command.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if lowered.startswith("sudo ") or lowered == "sudo":
        return True
    if lowered.startswith("doas ") or lowered == "doas":
        return True
    if lowered.startswith("runas ") or lowered == "runas":
        return True
    return "runas" in lowered and "start-process" in lowered


def confirm_command(command: str) -> bool:
    """Prompt the user before running any model-requested shell command."""
    privileged = is_privileged_command(command)
    while True:
        if privileged:
            answer = input(
                "\n\033[1;91mWARNING\033[0m: the following command may require elevated "
                "credentials, such as a sudo password, administrator approval, or running "
                "PowerShell as Administrator.\n"
                f"{command}\nProceed? [y/N]: "
            ).strip().lower()
        else:
            answer = input(
                f"\n\033[93mShell runner\033[0m: run command:\n{command}\nProceed? [y/N]: "
            ).strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"", "n", "no"}:
            return False
        print("Please respond with 'y' or 'n'.")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for interactive and one-shot usage."""
    parser = argparse.ArgumentParser(
        description=(
            "Minimal GPT-style chat client with user controlled direct "
            "command execution"
        )
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=VERSION,
        help="Show the program version and exit.",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.4",
        help="Model to use when dispatching chat completions.",
    )
    parser.add_argument(
        "--system-prompt",
        default=get_default_system_prompt(),
        help="System prompt injected at the start of the conversation.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to write rolling log files (defaults to CWD).",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Optional prompt to run once without entering the interactive loop.",
    )
    parser.add_argument(
        "--hide-reasoning",
        action="store_true",
        help="Do not request or print reasoning summaries.",
    )
    return parser.parse_args()


def resolve_api_key(explicit_key: str | None) -> str:
    """Resolve the API key from the CLI flag or environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        sys.exit("OpenAI API key missing. Set the OPENAI_API_KEY environment variable.")
    return key


def build_log_file(log_dir: Path) -> Path:
    """Create the daily log file path under the configured directory."""
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%m%d%y")
    return log_dir / f"openaigpt-{timestamp}.log"


def build_command_marker() -> str:
    """Generate a per-session marker so old logs cannot trigger new commands."""
    token = secrets.token_hex(4)
    return f"{COMMAND_MARKER_PREFIX}{token}{COMMAND_MARKER_SUFFIX}"


def sanitize_command_marker(text: str, command_marker: str) -> str:
    """Prevent the model from re-ingesting the active marker from user-provided logs."""
    if command_marker not in text:
        return text
    return text.replace(command_marker, "[[RUN:REDACTED]]")


def augment_system_prompt(system_prompt: str, command_marker: str) -> str:
    """Inject instructions that teach the model how to request shell commands."""
    base = system_prompt.rstrip()
    return f"{base}\n\nCommand marker: {command_marker}\n{build_shell_instructions()}"


def log_interaction(
    log_file: Path,
    prompt: str,
    reply: str,
    reasoning_logs: List[str] | None = None,
    command_logs: List[str] | None = None,
) -> None:
    """Append a prompt, reply, reasoning, and command activity to the session log."""
    timestamp = dt.datetime.now().strftime("[%m-%d-%Y %H:%M:%S]")
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp}\n\n")
        handle.write(f"Prompt: {prompt}\n")
        handle.write(f"Response: {reply}\n\n")
        if reasoning_logs:
            handle.write("Reasoning summaries:\n")
            for entry in reasoning_logs:
                handle.write(entry + "\n\n")
        if command_logs:
            handle.write("Executed shell commands:\n")
            for entry in command_logs:
                handle.write(entry + "\n\n")
        handle.write("-" * 60 + "\n\n")


def extract_shell_commands(reply: str, command_marker: str) -> List[str]:
    """Return every shell command requested by the assistant."""
    commands: List[str] = []
    for line in reply.splitlines():
        stripped = line.strip()
        if stripped.startswith(command_marker):
            command = stripped[len(command_marker) :].strip()
            if command:
                commands.append(command)
    return commands


def summarize_output_for_model(stream_name: str, output: str) -> str:
    """Keep normal output intact while compressing pathological output for the model."""
    if not output:
        return f"{stream_name}:\n<no {stream_name.lower()}>"
    if len(output) <= MAX_MODEL_OUTPUT_CHARS:
        return f"{stream_name}:\n{output}"

    head = output[:MODEL_OUTPUT_HEAD_CHARS].rstrip()
    tail = output[-MODEL_OUTPUT_TAIL_CHARS:].lstrip()
    omitted_chars = len(output) - len(head) - len(tail)
    line_count = output.count("\n") + 1
    return (
        f"{stream_name} (truncated for model, {len(output)} chars across {line_count} lines):\n"
        f"{head}\n\n"
        f"... [{omitted_chars} chars omitted] ...\n\n"
        f"{tail}"
    )


def run_shell_commands(commands: List[str]) -> tuple[List[str], List[str]]:
    """Execute commands sequentially and return full and model-sized logs."""
    command_logs: List[str] = []
    model_command_logs: List[str] = []
    command_runner = list(get_command_shell_profile()["runner"])
    for command in commands:
        if not confirm_command(command):
            log_entry = (
                f"Command: {command}\n"
                "Skipped: user denied execution confirmation."
            )
            command_logs.append(log_entry)
            model_command_logs.append(log_entry)
            print(
                "\033[93mShell runner\033[0m: skipped command (user denied confirmation)."
            )
            continue
        print(f"\033[93mShell runner\033[0m: executing `{command}`")
        timed_out = False
        exit_code_label = ""
        try:
            completed = subprocess.run(
                [*command_runner, command],
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
            raw_stdout = completed.stdout.strip()
            raw_stderr = completed.stderr.strip()
            exit_code_label = str(completed.returncode)
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            raw_stdout = (exc.stdout or "").strip()
            raw_stderr = (exc.stderr or "").strip()
            exit_code_label = f"timed out after {COMMAND_TIMEOUT_SECONDS} seconds"
            print(
                "\033[91mShell runner\033[0m: command timed out after "
                f"{COMMAND_TIMEOUT_SECONDS} seconds."
            )

        stdout = raw_stdout or "<no stdout>"
        stderr = raw_stderr or "<no stderr>"
        log_entry = (
            f"Command: {command}\n"
            f"Exit code: {exit_code_label}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )
        model_log_entry = (
            f"Command: {command}\n"
            f"Exit code: {exit_code_label}\n"
            f"{summarize_output_for_model('STDOUT', raw_stdout)}\n"
            f"{summarize_output_for_model('STDERR', raw_stderr)}"
        )
        command_logs.append(log_entry)
        model_command_logs.append(model_log_entry)
        if raw_stdout:
            print(f"\033[96mstdout\033[0m:\n{raw_stdout}")
        if raw_stderr:
            print(f"\033[91mstderr\033[0m:\n{raw_stderr}")
        if timed_out and not raw_stdout and not raw_stderr:
            print("(command timed out without producing output)")
        elif not raw_stdout and not raw_stderr:
            print("(command produced no output)")
    return command_logs, model_command_logs


def prompt_loop(
    client: OpenAI,
    model: str,
    log_file: Path,
    system_prompt: str,
    command_marker: str,
    show_reasoning: bool,
) -> None:
    """Run the interactive prompt loop until the user submits an empty prompt."""
    messages = build_initial_messages(system_prompt, command_marker)
    print(
        "\n:::\033[97mWelcome to OpenAI GPT\033[0m:::\n\n"
        "Enter an empty prompt to exit.\n"
    )
    while True:
        user_input = input("\033[94mPrompt\033[0m: ").strip()
        if not user_input:
            print("\n\033[91mPrompt not defined. Exiting.\033[0m\n")
            break
        handled = handle_prompt(
            client, model, log_file, messages, user_input, command_marker, show_reasoning
        )
        if not handled:
            continue


def build_initial_messages(
    system_prompt: str, command_marker: str
) -> List[Dict[str, str]]:
    """Create the initial message list with the augmented system prompt."""
    injected_prompt = augment_system_prompt(system_prompt, command_marker)
    return [{"role": "system", "content": injected_prompt}]


def get_response_item_type(item: object) -> str | None:
    """Read a response item type from either an SDK object or plain mapping."""
    if isinstance(item, dict):
        value = item.get("type")
    else:
        value = getattr(item, "type", None)
    return value if isinstance(value, str) else None


def iter_reasoning_summary_texts(response: object) -> List[str]:
    """Extract reasoning summary text from a Responses API object."""
    summaries: List[str] = []
    for item in getattr(response, "output", []) or []:
        if get_response_item_type(item) != "reasoning":
            continue
        if isinstance(item, dict):
            summary_items = item.get("summary", []) or []
        else:
            summary_items = getattr(item, "summary", []) or []
        for summary_item in summary_items:
            if isinstance(summary_item, dict):
                summary_type = summary_item.get("type")
                text = summary_item.get("text")
            else:
                summary_type = getattr(summary_item, "type", None)
                text = getattr(summary_item, "text", None)
            if summary_type == "summary_text" and isinstance(text, str) and text.strip():
                summaries.append(text.strip())
    return summaries


def run_with_spinner(callable_):
    """Show a single-cell spinner while waiting for a blocking operation."""
    stop_event = threading.Event()

    def spin() -> None:
        index = 0
        while not stop_event.is_set():
            frame = SPINNER_FRAMES[index % len(SPINNER_FRAMES)]
            print(f"\r\033[93mThinking\033[0m: {frame}", end="", flush=True)
            index += 1
            time.sleep(SPINNER_INTERVAL_SECONDS)
        print("\r\033[K", end="", flush=True)

    spinner = threading.Thread(target=spin, daemon=True)
    spinner.start()
    try:
        return callable_()
    finally:
        stop_event.set()
        spinner.join()


def create_response(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    show_reasoning: bool,
):
    """Create a Responses API request, optionally asking for reasoning summaries."""
    request_args = {
        "model": model,
        "input": messages,
    }
    if show_reasoning:
        request_args["reasoning"] = {
            "effort": "medium",
            "summary": "auto",
        }
    return run_with_spinner(lambda: client.responses.create(**request_args))


def handle_prompt(
    client: OpenAI,
    model: str,
    log_file: Path,
    messages: List[Dict[str, str]],
    user_input: str,
    command_marker: str,
    show_reasoning: bool,
) -> bool:
    """Handle one user prompt, including optional shell execution follow-ups."""
    if user_input.casefold() == "lucky":
        special_reply = "Lucky eats ass from behind"
        print(f"\n\033[92mOpenAI GPT\033[0m: {special_reply}\n")
        log_interaction(log_file, user_input, special_reply)
        return True

    sanitized_input = sanitize_command_marker(user_input, command_marker)
    original_question = sanitized_input
    initial_length = len(messages)
    messages.append({"role": "user", "content": sanitized_input})
    replies: List[str] = []
    all_reasoning_logs: List[str] = []
    all_command_logs: List[str] = []
    try:
        while True:
            response = create_response(client, model, messages, show_reasoning)
            reply = getattr(response, "output_text", "") or ""
            reasoning_summaries = iter_reasoning_summary_texts(response)
            replies.append(reply)
            print(f"\n\033[92mOpenAI GPT\033[0m: {reply}\n")
            if reasoning_summaries:
                all_reasoning_logs.extend(reasoning_summaries)
                print("\033[95mReasoning summary\033[0m:")
                for summary in reasoning_summaries:
                    print(summary)
                print()
            messages.append({"role": "assistant", "content": reply})
            shell_commands = extract_shell_commands(reply, command_marker)
            if not shell_commands:
                break
            command_logs, model_command_logs = run_shell_commands(shell_commands)
            if command_logs:
                all_command_logs.extend(command_logs)
                summary = (
                    "Shell command results to help answer the original question below.\n\n"
                    f"Original question:\n{original_question}\n\n"
                    + "\n\n".join(
                        sanitize_command_marker(entry, command_marker)
                        for entry in model_command_logs
                    )
                    + "\n\nUse these results to address the original question. "
                    "Only request more commands if new data is required."
                )
                messages.append({"role": "user", "content": summary})
    except Exception as exc:
        print(f"\n\033[91mOpenAI GPT\033[0m: Error - {exc}\n")
        del messages[initial_length:]
        return False
    combined_reply = "\n\n".join(replies)
    log_interaction(
        log_file,
        user_input,
        combined_reply,
        all_reasoning_logs if all_reasoning_logs else None,
        all_command_logs if all_command_logs else None,
    )
    return True


def run_single_prompt(
    client: OpenAI,
    model: str,
    log_file: Path,
    system_prompt: str,
    user_prompt: str,
    command_marker: str,
    show_reasoning: bool,
) -> None:
    """Run a single prompt without entering the interactive loop."""
    prompt = user_prompt.strip()
    if not prompt:
        sys.exit("Cannot run empty prompt in non-interactive mode.")
    messages = build_initial_messages(system_prompt, command_marker)
    success = handle_prompt(
        client, model, log_file, messages, prompt, command_marker, show_reasoning
    )
    if not success:
        sys.exit(1)


def main() -> None:
    """Initialize the client and dispatch interactive or one-shot execution."""
    args = parse_args()
    api_key = resolve_api_key(None)
    client = OpenAI(api_key=api_key)
    log_file = build_log_file(args.log_dir)
    command_marker = build_command_marker()
    if args.prompt:
        run_single_prompt(
            client,
            args.model,
            log_file,
            args.system_prompt,
            args.prompt,
            command_marker,
            not args.hide_reasoning,
        )
    else:
        prompt_loop(
            client,
            args.model,
            log_file,
            args.system_prompt,
            command_marker,
            not args.hide_reasoning,
        )


if __name__ == "__main__":
    main()
