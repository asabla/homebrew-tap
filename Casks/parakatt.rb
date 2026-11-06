cask "parakatt" do
  version "0.7.6"
  sha256 "4e0adf7f3cc181b9fe27e458032cca507cf7a69a053a88d6953b408579ee5ba9"

  url "https://github.com/asabla/parakatt/releases/download/v#{version}/Parakatt-#{version}-arm64.dmg"
  name "Parakatt"
  desc "Voice-to-text transcription for macOS menu bar"
  homepage "https://github.com/asabla/parakatt"

  depends_on macos: ">= :sonoma"
  depends_on arch: :arm64

  app "Parakatt.app"

  postflight do
    # Remove quarantine so the unsigned app can launch without right-click workaround
    system_command "/usr/bin/xattr",
                   args: ["-dr", "com.apple.quarantine", "#{appdir}/Parakatt.app"],
                   sudo: false

    ohai "Parakatt requires Microphone and Accessibility permissions."
    ohai "Grant these in System Settings > Privacy & Security on first launch."
  end

  zap trash: [
    "~/Library/Application Support/Parakatt",
    "~/Library/Preferences/com.parakatt.app.plist",
  ]
end
