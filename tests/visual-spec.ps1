$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$html = Get-Content -LiteralPath $htmlPath -Raw -Encoding UTF8
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $script:failures.Add($Message) }
}

$assets = @(
    'assets/hanli-nangong-background.png',
    'assets/dageng-sword-array.png',
    'assets/qingzhu-swords.png',
    'assets/wind-thunder-wings.png'
)

foreach ($asset in $assets) {
    Assert-True (Test-Path -LiteralPath (Join-Path $projectRoot $asset)) "Missing local asset: $asset"
    Assert-True ($html.Contains($asset)) "HTML does not reference: $asset"
}

Assert-True ($html.Contains('class="geng-formation"')) 'Missing layered Great Geng formation'
Assert-True ($html.Contains('class="qingzhu-formation"')) 'Missing layered Qingzhu sword formation'
Assert-True ($html.Contains('class="wind-thunder-wings"')) 'Missing Wind-Thunder Wings progress marker'
Assert-True ($html.Contains('class="wing-asset"')) 'Wing source is not cropped through a dedicated SVG viewport'
Assert-True ($html.Contains('left:calc(4% + var(--used)*92%)')) 'Wing marker is not tied to --used'
Assert-True ($html.Contains('@media(prefers-reduced-motion:reduce)')) 'Missing reduced-motion treatment'
Assert-True ($html.Contains('function setUsed(value)')) 'Missing reusable usage-state updater'
Assert-True ($html.Contains("setUsed(Number(btn.dataset.used))")) 'Usage buttons do not call the updater'

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Host "FAIL: $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PASS: visual structure and local assets satisfy the refinement contract.' -ForegroundColor Green
