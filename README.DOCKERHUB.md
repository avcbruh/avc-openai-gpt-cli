# avc-openai-gpt-cli

`avc-openai-gpt-cli` is a Python command-line interface for interacting with
OpenAI models through the Responses API.

This image runs `gpt.py` inside a container and expects your OpenAI API key at
runtime through the `OPENAI_API_KEY` environment variable.

## Image

Docker Hub repository:
`jelangley/avc-openai-gpt-cli`

GitHub repository:
`https://github.com/avcbruh/avc-openai-gpt-cli`

Example tags:
- `latest`
- `0419261034`

## Pull

`docker pull jelangley/avc-openai-gpt-cli:latest`

or

`docker pull jelangley/avc-openai-gpt-cli:0419261034`

## Run

`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest`

To run a specific snapshot:

`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:0419261034`

## CLI Parameters

The image starts with:

`python gpt.py`

You can append any supported `gpt.py` arguments after the image name in
`docker run`.

Supported parameters:
- `--model MODEL`
- `--system-prompt TEXT`
- `--log-dir PATH`
- `--prompt TEXT`
- `--hide-reasoning`
- `--reasoning-level {minimal,low,medium,high}`

Examples:

Run a one-shot prompt:
`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest --prompt "What is the meaning of life?"`

Select a model:
`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest --model gpt-5.4-mini`

Hide reasoning summaries:
`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest --hide-reasoning`

Set the reasoning level:
`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest --reasoning-level high`

Override the system prompt:
`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" jelangley/avc-openai-gpt-cli:latest --system-prompt "You are a concise assistant."`

## Persist Logs

By default, log files written inside the container are ephemeral. To keep them
on the host, mount a local directory and pass `--log-dir`.

`mkdir -p logs`

`docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" -v "$(pwd)/logs:/logs" jelangley/avc-openai-gpt-cli:latest python gpt.py --log-dir /logs`

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
