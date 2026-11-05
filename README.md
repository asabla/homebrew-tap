# Homebrew Tap

Custom Homebrew tap for macOS applications.

## Usage

```bash
brew tap asabla/tap
```

## Available Casks

| Cask | Description |
|------|-------------|
| `parakatt` | Voice-to-text transcription for the macOS menu bar |
| `pond` | Local data lake per directory with a web UI and MCP endpoints |

### Install

```bash
brew install --cask asabla/tap/parakatt
```

### Update

```bash
brew upgrade asabla/tap/parakatt
```

### Uninstall

```bash
brew uninstall --cask parakatt
```

## Pond

Pond is a local data lake per directory, with a web UI and MCP endpoints. `Casks/pond.rb` installs the published binary release for Apple Silicon and Intel Macs.

To update the cask after a new stable Pond release:

```sh
python3 scripts/update_pond.py v0.2.0
python3 -m unittest discover -s tests -v
brew style Casks/pond.rb
git diff -- Casks/pond.rb
```

The helper downloads the release assets from `asabla/pond`, verifies every archive against both `checksums.txt` and the generated cask, normalizes Homebrew formatting, then writes `Casks/pond.rb` atomically. A validation failure leaves the existing cask unchanged. The release tag above is an example; pass the actual published version. Review and commit the cask, then push this tap before announcing installation.

Install Pond and copy its bundled examples into a writable directory:

```sh
brew install --cask asabla/tap/pond
pond version
cp -R "$(brew --caskroom pond)/0.2.0/examples" ./pond-examples
pond ./pond-examples/social
```

Use the installed release version in the copy path; Homebrew prints the correct command at install time. Start `pond ./pond-examples/shop` in a second terminal. The bundled examples each include two saved queries and two graphs. Managed mode needs the selected engine running. Use `--runtime` to select Docker, Colima, OrbStack, Rancher Desktop in Moby mode, or Podman; run `pond doctor` to check the connection. `--minilake URL` attaches to an existing service without a local container CLI. See Pond's README for the current provider verification limits.

`Casks/pond.rb.in` remains a template for the helper tests. Homebrew uses `Casks/pond.rb`.

For offline verification of already downloaded release assets, use `--assets-dir PATH`. `--output PATH` writes a review copy elsewhere. Neither option publishes a release or pushes this tap.
