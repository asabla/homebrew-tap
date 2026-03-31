cask "parakatt" do
  version "0.2.0"
  sha256 "72182b5bea047bf34a7a4faa6272f80360717996d7f8927469cbae4ca3f3c825"

  url "https://github.com/asabla/parakatt/releases/download/v#{version}/Parakatt-#{version}-arm64.dmg"
  name "Parakatt"
  desc "Voice-to-text transcription for macOS menu bar"
  homepage "https://github.com/asabla/parakatt"

  depends_on macos: ">= :sonoma"
  depends_on arch: :arm64

  app "Parakatt.app"

  preflight do
    system_command "/usr/bin/xattr",
                   args: ["-cr", "#{staged_path}/Parakatt.app"]
  end

  postflight do
    ohai "Parakatt requires Microphone and Accessibility permissions."
    ohai "Grant these in System Settings > Privacy & Security."
    ohai "After upgrading, you must re-grant Accessibility permission:"
    ohai "  System Settings > Privacy & Security > Accessibility"
    ohai "  Remove Parakatt, then re-add and enable it."
  end

  zap trash: [
    "~/Library/Application Support/Parakatt",
    "~/Library/Preferences/com.parakatt.app.plist",
  ]
end
