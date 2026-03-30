cask "parakatt" do
  version "0.1.0"
  sha256 "fbf693d90c6a2177343e253d9770bcbfad26baeda96066cc86adc84006b162b7"

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
