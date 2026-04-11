# avc-openai-gpt-cli

## Installation

Install requirements for `gpt.py`

Python modules used by `gpt.py`:
- Standard library: `argparse`, `datetime`, `os`, `platform`, `secrets`, `shutil`, `subprocess`, `sys`, `pathlib`, `typing`
- External package to install: `openai`

1. Confirm Python is installed.

macOS / Linux:
`python3 --version`

Windows:
`py --version`
or
`python --version`

2. Confirm pip is available for the same Python installation.

macOS / Linux:
`python3 -m pip --version`

Windows:
`py -m pip --version`
or
`python -m pip --version`

If pip is missing, install or enable pip for that Python installation first.

3. Install the OpenAI Python package with pip.

macOS / Linux:
`python3 -m pip install --upgrade openai`

Windows:
`py -m pip install --upgrade openai`
or
`python -m pip install --upgrade openai`

4. Set your OpenAI API key in the `OPENAI_API_KEY` environment variable.
Do not hardcode the key in the `gpt.py` script.

macOS / Linux, current shell session:
`export OPENAI_API_KEY="your_api_key_here"`

Windows Command Prompt, current session:
`set OPENAI_API_KEY=your_api_key_here`

Windows PowerShell, current session:
`$env:OPENAI_API_KEY="your_api_key_here"`

To make the variable persistent, add it in your shell profile or Windows user environment settings.

5. Run the script.

macOS / Linux:
`python3 gpt.py`
`python3 gpt.py -h`
`python3 gpt.py --help`
`python3 gpt.py --reasoning-level high`

Windows:
`py gpt.py`
`py gpt.py -h`
`py gpt.py --reasoning-level high`
or
`python gpt.py`
`python gpt.py -h`
`python gpt.py --reasoning-level high`

Available reasoning levels:
`minimal`, `low`, `medium`, `high`

Use `--hide-reasoning` to disable reasoning summaries entirely. When reasoning is
enabled, `--reasoning-level` controls the requested effort level. The default is
`medium`.

Optional checks:
`python3 -m pip show openai`
`py -m pip show openai`

## License

MIT License

Copyright (c) 2026 Jerry G. Langley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Notice

User Input Responsibility Notice

This software is a general-purpose interface for interacting with a language model.
Users are solely responsible for any prompts, files, commands, data, credentials,
personal information, or other content they choose to provide to the software or
to any connected model or service.

The author does not review, control, endorse, or assume responsibility for user-
supplied content, for decisions to disclose sensitive information, or for outputs
or downstream consequences arising from materials submitted by the user.

Use of this software is at the user's own discretion and risk.
