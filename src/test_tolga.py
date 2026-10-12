import subprocess
import os

ps_code = """
$stream = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]::new()
Add-Type -AssemblyName System.Speech
# Windows Media SpeechSynthesis (OneCore)
[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime] | Out-Null
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.Language -like "tr*" -and $_.Gender -eq "Male" } | Select-Object -First 1
if (-not $voice) {
    $voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.Language -like "tr*" } | Select-Object -First 1
}
if ($voice) {
    $synth.Voice = $voice
    Write-Host "Secilen Ses: $($voice.DisplayName)"
    $asyncOp = $synth.SynthesizeTextToStreamAsync("1950 yılında dünyayı sarsan soru soruldu: Makineler düşünebilir mi?")
    $asyncOp.AsTask().Wait()
    $stream = $asyncOp.GetResults()
    
    $reader = New-Object Windows.Storage.Streams.DataReader($stream)
    $reader.LoadAsync($stream.Size).AsTask().Wait()
    $bytes = New-Object byte[] $stream.Size
    $reader.ReadBytes($bytes)
    [System.IO.File]::WriteAllBytes("test_tolga.wav", $bytes)
    Write-Host "Ses kaydedildi: test_tolga.wav"
} else {
    Write-Host "Turkce ses bulunamadi"
}
"""

res = subprocess.run(["powershell", "-Command", ps_code], capture_output=True, text=True, encoding="utf-8")
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
