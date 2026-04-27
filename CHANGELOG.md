# Changelog

## 2026-04-27

### Snapshot `0427260836`

- Changed the default model from `gpt-5.4` to `gpt-5.5`.

## 2026-04-21

### Snapshot `0421260757`

- Moved the snapshot version string above the interactive `Welcome to OpenAI GPT` banner.
- Added a blank line between the version string and the welcome banner at startup.

## 2026-04-19

### Snapshot `0419261119`

- Changed the Docker image to use an entrypoint so `docker run ... --flags` passes CLI options directly to `gpt.py`.
- Updated `README.DOCKERHUB.md` examples to show the bare-flag Docker invocation supported by the image.

### Snapshot `0419261052`

- Added the snapshot version string to the interactive CLI welcome banner shown at startup.

### Snapshot `0419261034`

- Removed the unused `explicit_key` parameter from `resolve_api_key()` so the function signature now matches its environment-only behavior.

## 2026-04-15

### Snapshot `0415260842`

- Added the full MIT license text from `LICENSE` to the top of `gpt.py` as a comment header while preserving the shebang.

### Snapshot `0415260805`

- Changed Windows elevation handling so `gpt.py` no longer attempts to self-elevate by opening a new PowerShell window.
- Added a guard that skips `Start-Process -Verb RunAs` and similar `runas`-style commands and tells the user to rerun `gpt.py` from PowerShell opened as Administrator for admin tasks.
- Updated `README.md` to document that Windows administrative commands should be run from an Administrator PowerShell session started before launching `gpt.py`.

## 2026-04-11

### Snapshot `0411261831`

- Expanded `gpt.py --help` text to include clearer option descriptions plus model and reasoning-level guidance from `README.md`.

### Snapshot `0411261809`

- Added `--reasoning-level` to configure the requested reasoning effort from the CLI with supported levels `minimal`, `low`, `medium`, and `high`; the default is `medium`.

### Snapshot `0410261708`

- Added platform-aware shell execution guidance so model-requested commands target the active OS and shell.
- Added a per-session command marker token and marker sanitization to prevent stale or user-supplied markers from triggering command execution.
- Added truncation for large command output before feeding results back to the model while keeping full stdout and stderr in the log file.
- Added `--log-dir` to choose where session log files are written.
- Added `--prompt` for one-shot non-interactive execution.
- Added `--hide-reasoning` to disable reasoning summary requests and printing.
- Added reasoning summary extraction from Responses API output when reasoning is enabled.
- Expanded `README.md` to include installation instructions plus the project license and notice text.
- Added `.gitignore` entries for Python bytecode caches and `.log` files.
- Removed tracked `__pycache__` and `.log` artifacts from the repository.

## 2026-04-10

### Snapshot `0410261005`

- Corrected the snapshot string.

### Snapshot `0410260904`

- Added `-v` and `--version` CLI flags to print the program snapshot string and exit.
- Added a single-line response spinner that rotates `/`, `-`, `\`, and `|` while the model request is in flight.

### Snapshot `0410260950`

- Removed the `--api-key` CLI option.
- Changed API key loading to require `OPENAI_API_KEY`.
- Changed shell command confirmation to default to `No` on Enter by using `Proceed? [y/N]:`.
- Upgraded privileged-command confirmation to show a bold warning that elevated credentials may be required, such as a `sudo` password, administrator approval, or PowerShell running as Administrator.
