#!/usr/bin/env python3
"""Prepare Pond's cask from a published release and verified archives."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

REPOSITORY = "asabla/pond"
TARGETS = ("darwin_arm64", "darwin_amd64", "linux_arm64", "linux_amd64")


def validate_assets(directory, version, tag):
    """Check every cask URL and archive checksum before changing the tap."""
    directory = Path(directory)
    cask = (directory / "pond.rb").read_text()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Only stable release versions are accepted")
    if tag != "v" + version:
        raise ValueError("The release tag must be v followed by its version")
    if not re.search(r'^cask "pond" do$', cask, re.MULTILINE):
        raise ValueError("The release cask is not named pond")
    if re.findall(r'^  version "([^"]+)"$', cask, re.MULTILINE) != [version]:
        raise ValueError("The cask version does not match the requested release")
    expected = {}
    for line in (directory / "checksums.txt").read_text().splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[a-f0-9]{64}", parts[0]):
            raise ValueError("Invalid release checksum line")
        filename = parts[1].lstrip("*")
        if filename in expected:
            raise ValueError("Duplicate release checksum: " + filename)
        expected[filename] = parts[0]
    links = re.findall(r'sha256 "([a-f0-9]{64})"\s+url "([^"]+)"', cask)
    if len(links) != len(TARGETS):
        raise ValueError("Expected cask URLs for all four release targets")
    actual_links = {url.replace("#{version}", version): digest for digest, url in links}
    for target in TARGETS:
        filename = f"pond_{version}_{target}.tar.gz"
        url = f"https://github.com/{REPOSITORY}/releases/download/{tag}/{filename}"
        recorded = expected.get(filename)
        if not recorded or actual_links.get(url) != recorded:
            raise ValueError("Cask and release checksums disagree for " + filename)
        digest = hashlib.sha256()
        with (directory / filename).open("rb") as archive:
            for chunk in iter(lambda: archive.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != recorded:
            raise ValueError("Archive checksum mismatch: " + filename)
    return cask


def download_release(directory, tag, version):
    result = subprocess.run(
        ["gh", "release", "view", tag, "--repo", REPOSITORY,
         "--json", "tagName,isDraft,isPrerelease,assets"],
        check=True, capture_output=True, text=True,
    )
    release = json.loads(result.stdout)
    if release["tagName"] != tag or release["isDraft"] or release["isPrerelease"]:
        raise ValueError("A published stable Pond release is required")
    names = ["pond.rb", "checksums.txt"] + [f"pond_{version}_{target}.tar.gz" for target in TARGETS]
    available = {asset["name"] for asset in release["assets"]}
    missing = set(names) - available
    if missing:
        raise ValueError("Missing release assets: " + ", ".join(sorted(missing)))
    command = ["gh", "release", "download", tag, "--repo", REPOSITORY, "--dir", str(directory)]
    for name in names:
        command.extend(["--pattern", name])
    subprocess.run(command, check=True)


def write_cask(output, content):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".pond-", suffix=".rb", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.chmod(temporary, 0o644)
        os.replace(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)


def style_cask(content):
    """Normalize GoReleaser's zap array indentation and Homebrew ordering."""
    pattern = r'^  zap trash: \[\n((?:[ \t]*"[^"\n]+",?\n)+)[ \t]*\]'
    def format_array(match):
        items = sorted(re.findall(r'"([^"\n]+)"', match.group(1)))
        return '  zap trash: [\n' + ''.join(f'    "{item}",\n' for item in items) + '  ]'
    return re.sub(pattern, format_array, content, flags=re.MULTILINE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Published release tag, for example v0.1.0")
    parser.add_argument("--assets-dir", type=Path, help="Verify already downloaded release assets")
    parser.add_argument("--output", type=Path, help="Override the destination cask")
    args = parser.parse_args()
    if not re.fullmatch(r"v\d+\.\d+\.\d+", args.tag):
        parser.error("Use a stable version tag such as v0.1.0")
    version = args.tag[1:]
    output = args.output or Path(__file__).resolve().parents[1] / "Casks" / "pond.rb"
    try:
        if args.assets_dir:
            cask = validate_assets(args.assets_dir, version, args.tag)
        else:
            with tempfile.TemporaryDirectory(prefix="pond-release-") as directory:
                download_release(directory, args.tag, version)
                cask = validate_assets(directory, version, args.tag)
        write_cask(output, style_cask(cask))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Pond cask was not changed: {error}\n")
    print(f"Prepared {output} from verified {REPOSITORY} release {args.tag}. Review and commit it before pushing.")


if __name__ == "__main__":
    main()
