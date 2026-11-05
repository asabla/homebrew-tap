import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("update_pond", ROOT / "scripts" / "update_pond.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PondCaskTests(unittest.TestCase):
    def assets(self, directory):
        cask = (ROOT / "Casks" / "pond.rb.in").read_text()
        cask = cask.replace("@VERSION@", "0.1.0").replace("@TAG@", "v0.1.0")
        checksums = []
        for target in MODULE.TARGETS:
            filename = f"pond_0.1.0_{target}.tar.gz"
            contents = ("fixture " + target).encode()
            (directory / filename).write_bytes(contents)
            digest = hashlib.sha256(contents).hexdigest()
            cask = cask.replace("@SHA256_" + target.upper() + "@", digest)
            checksums.append(digest + "  " + filename)
        (directory / "pond.rb").write_text(cask)
        (directory / "checksums.txt").write_text("\n".join(checksums) + "\n")
        return cask

    def test_verified_assets_and_atomic_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            expected = self.assets(directory)
            actual = MODULE.validate_assets(directory, "0.1.0", "v0.1.0")
            self.assertEqual(actual, expected)
            output = directory / "tap" / "Casks" / "pond.rb"
            MODULE.write_cask(output, actual)
            self.assertEqual(output.read_text(), expected)

    def test_corrupt_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.assets(directory)
            (directory / "pond_0.1.0_darwin_arm64.tar.gz").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Archive checksum mismatch"):
                MODULE.validate_assets(directory, "0.1.0", "v0.1.0")

    def test_wrong_release_and_cask_hash_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.assets(directory)
            with self.assertRaisesRegex(ValueError, "version does not match"):
                MODULE.validate_assets(directory, "0.2.0", "v0.2.0")
            cask = (directory / "pond.rb").read_text()
            digest = (directory / "checksums.txt").read_text().split()[0]
            (directory / "pond.rb").write_text(cask.replace(digest, "0" * 64))
            with self.assertRaisesRegex(ValueError, "checksums disagree"):
                MODULE.validate_assets(directory, "0.1.0", "v0.1.0")

    def test_goreleaser_zap_array_is_normalized(self):
        original = '  zap trash: [\n      "~/Library/Application Support/pond/recent.json",\n      "~/.config/pond/recent.json",\n    ]\n'
        expected = '  zap trash: [\n    "~/.config/pond/recent.json",\n    "~/Library/Application Support/pond/recent.json",\n  ]\n'
        self.assertEqual(MODULE.style_cask(original), expected)

    def test_snapshot_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.assets(directory)
            with self.assertRaisesRegex(ValueError, "stable release"):
                MODULE.validate_assets(directory, "0.1.0-SNAPSHOT-test", "v0.1.0")


if __name__ == "__main__":
    unittest.main()
