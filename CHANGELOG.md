# Changelog

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
