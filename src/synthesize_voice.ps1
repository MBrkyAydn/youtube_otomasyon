param (
    [string]$Text,
    [string]$OutputFile
)

Add-Type -AssemblyName System.IO
[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime] | Out-Null

$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.Language -like 'tr*' -and $_.Gender -eq 'Male' } | Select-Object -First 1

if (-not $voice) {
    $voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object { $_.Language -like 'tr*' } | Select-Object -First 1
}

if ($voice) {
    $synth.Voice = $voice
    $asyncOp = $synth.SynthesizeTextToStreamAsync($Text)
    $stream = $asyncOp.GetAwaiter().GetResult()
    
    $fullPath = [System.IO.Path]::GetFullPath($OutputFile)
    $dir = [System.IO.Path]::GetDirectoryName($fullPath)
    if (-not [System.IO.Directory]::Exists($dir)) {
        [System.IO.Directory]::CreateDirectory($dir) | Out-Null
    }
    
    $fileStream = [System.IO.File]::Create($fullPath)
    $netStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
    $netStream.CopyTo($fileStream)
    $fileStream.Close()
    $netStream.Close()
    Write-Host "[OK] Tolga sesi uretildi: $OutputFile"
} else {
    Write-Error "Turkce ses bulunamadi"
}
