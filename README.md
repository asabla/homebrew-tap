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

## Pond: first release prepared

Pond is a local data lake per directory, with a web UI and MCP endpoints. Its binary cask is staged as `Casks/pond.rb.in`. The `.in` file is a preview with placeholders and is not advertised to Homebrew. Pond has no published stable release yet; do not rename the preview to `.rb` or insert snapshot hashes.

After Pond publishes a stable release with its generated cask, checksum file and four platform archives:

```sh
python3 scripts/update_pond.py v0.1.0
python3 -m unittest discover -s tests -v
brew style Casks/pond.rb
git diff -- Casks/pond.rb
```

The helper downloads the release assets from `asabla/pond`, verifies every archive against both `checksums.txt` and the generated cask, normalizes Homebrew formatting, then writes `Casks/pond.rb` atomically. A validation failure leaves the existing cask unchanged. The release tag above is an example; pass the actual published version. Review and commit the cask, then push this tap before announcing installation.

Once the release and tap update are published:

```sh
brew install --cask asabla/tap/pond
pond version
cp -R "$(brew --caskroom pond)/0.1.0/examples" ./pond-examples
pond ./pond-examples/social
```

Use the installed release version in the copy path; Homebrew prints the correct command at install time. Start `pond ./pond-examples/shop` in a second terminal. The bundled examples each include two saved queries and two graphs. Docker Desktop, OrbStack or colima must be running.

For offline verification of already downloaded release assets, use `--assets-dir PATH`. `--output PATH` writes a review copy elsewhere. Neither option publishes a release or pushes this tap.
