cask "parakatt" do
  version "0.1.1"
  sha256 "abdcac36385a057fa533d20e037a456f4fe51816b281fce58b9d0af1b0c9c77d"

  url "https://github.com/asabla/parakatt/releases/download/v#{version}/Parakatt-#{version}-arm64.dmg"
  name "Parakatt"
  desc "Voice-to-text transcription for macOS menu bar"
  homepage "https://github.com/asabla/parakatt"

  depends_on macos: ">= :sonoma"
  depends_on arch: :arm64

  app "Parakatt.app"

  postflight do
    ohai "Parakatt requires Microphone and Accessibility permissions."
    ohai "Grant these in System Settings > Privacy & Security."
  end

  zap trash: [
    "~/Library/Application Support/Parakatt",
    "~/Library/Preferences/com.parakatt.app.plist",
  ]
end
