$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$html = Get-Content -LiteralPath $htmlPath -Raw -Encoding UTF8
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $script:failures.Add($Message) }
}

$localAssets = @(
    'assets/hanli-nangong-background.png',
    'assets/nascent-soul-aura-reference.png',
    'assets/dageng-sword-array-v2.png',
    'assets/qingzhu-fengyun-sword-v2.png',
    'assets/wind-thunder-wings-v2.png'
)

foreach ($asset in $localAssets) {
    Assert-True (Test-Path -LiteralPath (Join-Path $projectRoot $asset)) "Missing local asset: $asset"
}

Assert-True ($html.Contains('class="geng-formation"')) 'Missing layered Great Geng formation'
Assert-True ($html.Contains('class="qingzhu-formation"')) 'Missing layered Qingzhu sword formation'
Assert-True ($html.Contains('class="wind-thunder-wings"')) 'Missing Wind-Thunder Wings progress marker'
Assert-True ($html.Contains('class="wing-asset"')) 'Wing source is not cropped through a dedicated SVG viewport'
Assert-True ($html.Contains('left:calc(4% + var(--used)*92%)')) 'Wing marker is not tied to --used'
Assert-True (($html | Select-String 'class="formation-sword"' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve sword slots'
Assert-True ($html.Contains('assets/wind-thunder-wings-v2.png')) 'Wind-Thunder Wings v2 texture is not rendered'
Assert-True ($html.Contains('width:72px;height:34px')) 'Wing marker must use the confirmed 72 by 34 geometry'
Assert-True ($html.Contains('translate:-50% 0')) 'Wing center is not anchored to the usage boundary'
Assert-True (-not $html.Contains('rotate:90deg')) 'Wing marker must remain horizontal'
Assert-True ($html.Contains('opacity:.72')) 'Wing marker must remain semi-transparent'
Assert-True ($html.Contains('assets/dageng-sword-array-v2.png')) 'Great Geng v2 texture is not rendered'
Assert-True ($html.Contains('assets/qingzhu-fengyun-sword-v2.png')) 'Qingzhu v2 sword texture is not rendered'
Assert-True ($html.Contains('class="formation-disc"')) 'Missing perspective formation disc'
Assert-True ($html.Contains('class="ring ring-outer"')) 'Missing outer formation ring'
Assert-True ($html.Contains('class="ring ring-middle"')) 'Missing middle formation ring'
Assert-True ($html.Contains('class="ring ring-inner"')) 'Missing inner formation ring'
Assert-True ($html.Contains('class="main-sword-asset"')) 'Missing Qingzhu main sword asset'
Assert-True (-not $html.Contains('.formation-swords{animation:')) 'Sword positions must not rotate with formation rings'
Assert-True ($html.Contains('class="formation-runes"')) 'Missing counter-rotating formation runes'
Assert-True ($html.Contains('class="formation-particles"')) 'Missing circular formation particles'
Assert-True ($html.Contains('class="formation-core"')) 'Missing breathing formation core'
Assert-True ($html.Contains('@media(prefers-reduced-motion:reduce)')) 'Missing reduced-motion treatment'
Assert-True ($html.Contains('function setUsed(value)')) 'Missing reusable usage-state updater'
Assert-True ($html.Contains("setUsed(Number(btn.dataset.used))")) 'Usage buttons do not call the updater'
Assert-True ($html.Contains('--aura-cyan:#8fe7ee')) 'Missing Nascent Soul cyan theme token'
Assert-True ($html.Contains('--jade:#4fd6a2')) 'Missing jade sword theme token'
Assert-True ($html.Contains('--geng-gold:#d9bd67')) 'Missing Great Geng gold theme token'
Assert-True ($html.Contains('class="nascent-aura"')) 'Missing Nascent Soul aura layer'
Assert-True ($html.Contains('url("assets/hanli-nangong-background.png")')) 'Face-to-face background must remain active'

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Host "FAIL: $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PASS: visual structure and local assets satisfy the refinement contract.' -ForegroundColor Green
