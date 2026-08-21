$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$htmlPath = Join-Path $projectRoot 'original-artifact-refined.html'
$cssPath = Join-Path $projectRoot 'styles/mortal-seal-card.css'
$jsPath = Join-Path $projectRoot 'scripts/quota-card.js'
$html = if (Test-Path -LiteralPath $htmlPath) { Get-Content -LiteralPath $htmlPath -Raw -Encoding UTF8 } else { '' }
$css = if (Test-Path -LiteralPath $cssPath) { Get-Content -LiteralPath $cssPath -Raw -Encoding UTF8 } else { '' }
$js = if (Test-Path -LiteralPath $jsPath) { Get-Content -LiteralPath $jsPath -Raw -Encoding UTF8 } else { '' }
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $script:failures.Add($Message) }
}

$localAssets = @(
    'assets/hanli-nangong-background.png',
    'assets/antigravity-nangong-background.jpg',
    'assets/nascent-soul-aura-reference.png',
    'assets/dageng-sword-array-v2.png',
    'assets/qingzhu-fengyun-sword-v2.png',
    'assets/wind-thunder-wings-v2.png'
)

foreach ($asset in $localAssets) {
    Assert-True (Test-Path -LiteralPath (Join-Path $projectRoot $asset)) "Missing local asset: $asset"
}

Assert-True (Test-Path -LiteralPath $cssPath) 'Missing focused card stylesheet'
Assert-True (Test-Path -LiteralPath $jsPath) 'Missing quota controller'
Assert-True ($html.Contains('href="styles/mortal-seal-card.css"')) 'HTML must load the focused card stylesheet'
Assert-True ($html.Contains('src="scripts/quota-card.js"')) 'HTML must load the quota controller'
Assert-True (-not $html.Contains('<style>')) 'Legacy inline stylesheet must be removed'
Assert-True (-not $html.Contains('class="data"')) 'Legacy right-side data panel must be removed'
Assert-True (-not $html.Contains('class="core"')) 'Legacy left-side quota panel must be removed'

Assert-True ($html.Contains('class="seal-card"')) 'Missing seal-card scene root'
Assert-True ($html.Contains('id="widget"')) 'Missing stable widget state root'
Assert-True ($html.Contains('class="portrait-scene"')) 'Missing portrait background layer'
Assert-True ($html.Contains('class="scene-veil"')) 'Missing scene readability veil'
Assert-True ($html.Contains('class="seal-formation"')) 'Missing overflow formation scene'
Assert-True (-not $html.Contains('class="formation-bloom"')) 'Blurred upper formation texture must be removed'
Assert-True ($html.Contains('class="formation-swords formation-swords--lower-arc"')) 'Formation swords must be gathered into the lower battle arc'
Assert-True ($html.Contains('class="quota-eye"')) 'Missing seven-day quota eye'
Assert-True ($html.Contains('id="percent"')) 'Missing seven-day quota value target'
Assert-True (-not $html.Contains('class="quota-name"')) 'Redundant seven-day quota caption must be removed'
Assert-True (-not $html.Contains('class="spirit-meridian"')) 'Curved progress meridian must be removed'
Assert-True (-not $html.Contains('meridian-')) 'All progress-line SVG layers must be removed'
Assert-True (-not $html.Contains('wind-thunder-wings')) 'Wind-Thunder Wings must be removed from the card'
$windThunderWingCopy = ([char]0x98CE) + ([char]0x96F7) + ([char]0x7FC5)
Assert-True (-not $html.Contains($windThunderWingCopy)) 'Obsolete Wind-Thunder Wings copy must be removed'
Assert-True ($html.Contains('class="quota-ledger"')) 'Missing right-side quota text ledger'
Assert-True ($html.Contains('class="ledger-item ledger-item--cycle"')) 'Missing seven-day cycle information group'
Assert-True ($html.Contains('class="ledger-item ledger-item--balance"')) 'Missing account dollar balance information group'
Assert-True ($html.Contains('id="balance"')) 'Missing account dollar balance value interface'
$accountCreditLabel = ([char]0x5F53) + ([char]0x524D) + ([char]0x4F59) + ([char]0x989D)
$dollarBalance = 'US$39.36'
$fiveHourCopy = ([char]0x4E94) + ([char]0x5C0F) + ([char]0x65F6) + ([char]0x4F59) + ([char]0x91CF)
Assert-True ($html.Contains($accountCreditLabel)) 'Account credit balance label must be visible'
Assert-True ($html.Contains($dollarBalance)) 'Account balance must use a US dollar amount'
Assert-True ($html.IndexOf($accountCreditLabel) -lt $html.IndexOf($dollarBalance)) 'Account balance label must appear above its dollar value'
Assert-True (-not $html.Contains($fiveHourCopy)) 'Obsolete five-hour quota copy must be removed'
Assert-True ($html.Contains('class="ledger-divider"')) 'Missing restrained ledger divider'
Assert-True ($html.Contains('id="used"')) 'Missing used quota label target'
Assert-True ($html.Contains('id="unlockButton"')) 'Missing unlock control'
Assert-True ($html.Contains('id="antigravityToggle"')) 'Missing Antigravity seal page control'
Assert-True ($html.Contains('class="antigravity-page"')) 'Missing Antigravity card page'
Assert-True ($html.Contains('id="agCredits"')) 'Missing Available AI Credits target'
Assert-True ($html.Contains('id="agGeminiWeekly"')) 'Missing Gemini weekly quota target'
Assert-True ($html.Contains('id="agGeminiFiveHour"')) 'Missing Gemini five-hour quota target'
Assert-True ($html.Contains('id="agClaudeWeekly"')) 'Missing Claude and GPT weekly quota target'
Assert-True ($html.Contains('id="agClaudeFiveHour"')) 'Missing Claude and GPT five-hour quota target'
Assert-True ($html.Contains('id="agSyncStatus"')) 'Missing Antigravity sync status target'
Assert-True ($html.Contains('id="agSyncedAt"')) 'Missing Antigravity sync time target'
Assert-True (($html | Select-String 'data-used=' -AllMatches).Matches.Count -eq 3) 'Exactly three quota demonstration states are required'
$mindClearCopy = ([char]0x5FF5) + ([char]0x5934) + ([char]0x901A) + ([char]0x8FBE)
$stewMortalWorldCopy = ([char]0x7096) + ([char]0x716E) + ([char]0x7EA2) + ([char]0x5C18)
$askSpringBreezeCopy = ([char]0x9047) + ([char]0x4E8B) + ([char]0x4E0D) + ([char]0x51B3) + ([char]0xFF0C) + ([char]0x53EF) + ([char]0x95EE) + ([char]0x6625) + ([char]0x98CE)
Assert-True ($html.Contains($askSpringBreezeCopy)) 'Account caption must use the ask-the-spring-breeze motto'
Assert-True (($html | Select-String 'class="mortal-motto"' -AllMatches).Matches.Count -eq 2) 'Card footer must contain exactly two mortal-world motto inscriptions'
Assert-True ($html.Contains($mindClearCopy)) 'Card footer must retain the classic mind-clear motto'
Assert-True ($html.Contains($stewMortalWorldCopy)) 'Card footer must retain the playful stew-the-mortal-world motto'

Assert-True (($html | Select-String 'class="formation-sword"' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve fixed sword slots'
Assert-True ([regex]::IsMatch($html, 'data-sword-index="0"[^>]*--angle:\s*103deg;[^>]*--radius:\s*61px;')) 'Left outer sword must begin the tightened lower horseshoe arc'
Assert-True ([regex]::IsMatch($html, 'data-sword-index="5"[^>]*--angle:\s*173deg;[^>]*--radius:\s*72px;')) 'Left inner sword must anchor the formation eye'
Assert-True ([regex]::IsMatch($html, 'data-sword-index="6"[^>]*--angle:\s*187deg;[^>]*--radius:\s*72px;')) 'Right inner sword must mirror the formation eye anchor'
Assert-True ([regex]::IsMatch($html, 'data-sword-index="11"[^>]*--angle:\s*257deg;[^>]*--radius:\s*61px;')) 'Right outer sword must close the tightened lower horseshoe arc'
Assert-True ($html.Contains('class="formation-ring formation-ring--outer"')) 'Missing outer perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--middle"')) 'Missing middle perspective ring'
Assert-True ($html.Contains('class="formation-ring formation-ring--inner"')) 'Missing inner perspective ring'
Assert-True (-not $html.Contains('class="qingzhu-sword"')) 'The isolated Qingzhu main sword must be removed'
Assert-True (-not $html.Contains('class="stray-sword')) 'Decorative stray swords must not inflate the quota sword count'
Assert-True (-not $html.Contains('assets/wind-thunder-wings-v2.png')) 'Wind-Thunder Wings texture must no longer render'

Assert-True ($css.Contains('--abyss-ink: #041416')) 'Missing abyss-ink token'
Assert-True ($css.Contains('--nascent-cyan: #71e2dc')) 'Missing Nascent Soul cyan token'
Assert-True ($css.Contains('--bamboo-jade: #59d99d')) 'Missing bamboo jade token'
Assert-True ($css.Contains('--moon-white: #eaf8ee')) 'Missing moon-white token'
Assert-True ($css.Contains('--ward-gold: #d5b564')) 'Missing ward-gold token'
Assert-True ($css.Contains('--mist-blue: #5ea8c9')) 'Missing mist-blue token'
Assert-True ($css.Contains('width: 480px')) 'Card must retain the exact 480px width'
Assert-True ($css.Contains('height: 270px')) 'Card must retain the exact 270px height'
Assert-True ($css.Contains('url("../assets/hanli-nangong-background.png")')) 'Confirmed Han Li and Nangong Wan background must remain active'
Assert-True ($css.Contains('background-position: 51% 48%')) 'Portrait crop must preserve the face-to-face center'
Assert-True ($css.Contains('url("../assets/antigravity-nangong-background.jpg")')) 'Antigravity page must use the confirmed portrait background'
Assert-True ($css.Contains('background-size: cover')) 'Antigravity portrait must fill the 480 by 270 card without distortion'
Assert-True ($css.Contains('background-position: center 44%')) 'Antigravity crop must preserve the face while excluding the bottom watermark'
Assert-True (-not $css.Contains('url("../assets/dageng-sword-array-v2.png")')) 'Blurred Great Geng texture overlay must not render'
Assert-True (-not $css.Contains('.qingzhu-sword')) 'The isolated Qingzhu main sword styling must be removed'
Assert-True ($css.Contains('.formation-ring--outer {')) 'Outer ring must have its own material rule'
Assert-True (-not $css.Contains('.formation-swords { animation:')) 'Sword slots must remain fixed while rings move'
Assert-True (-not $css.Contains('offset-path: path(')) 'Progress-marker motion path must be removed'
Assert-True (-not $css.Contains('.wind-thunder-wings')) 'Wind-Thunder Wings styling must be removed'
Assert-True (-not $css.Contains('.meridian-path')) 'Progress-line styling must be removed'
Assert-True ($css.Contains('.quota-ledger {')) 'Quota ledger must have a dedicated layout rule'
Assert-True ($css.Contains('right: 18px')) 'Quota ledger must align to the card right edge'
Assert-True ($css.Contains('width: 136px')) 'Quota ledger must preserve the portrait center with a compact width'
Assert-True ($css.Contains('--quota-optical-y: -5px')) 'Quota percentage must expose a small optical upward correction'
Assert-True ($css.Contains('font-size: 38px')) 'Quota percentage must fit compactly inside the formation eye'
Assert-True ($css.Contains('--spirit-highlight:')) 'Card must expose a shared spirit highlight color'
Assert-True ($css.Contains('--spirit-jade:')) 'Card must expose a shared jade body color'
Assert-True ($css.Contains('--spirit-gold:')) 'Card must expose a shared gold reflection color'
Assert-True ($css.Contains('--spirit-shadow:')) 'Card must expose a shared dark outline color'
Assert-True ($css.Contains('--spirit-glow:')) 'Card must expose a shared spirit glow color'
Assert-True ($css.Contains('.seal-card[data-used-state="warning"] {')) 'Warning state must override shared spirit colors'
Assert-True ($css.Contains('.seal-card[data-used-state="danger"] {')) 'Danger state must override shared spirit colors'
Assert-True ($css.Contains('var(--spirit-highlight) 48%')) 'Lit sword material must consume the shared spirit highlight'
Assert-True ($css.Contains('var(--spirit-jade) 58%')) 'Lit sword material must consume the shared jade color'
Assert-True ($css.Contains('drop-shadow(0 0 7px var(--spirit-glow))')) 'Lit sword glow must consume the shared spirit glow'
Assert-True ($css.Contains('--sword-energy: 0')) 'Each sword slot must expose continuous quota energy'
Assert-True ($css.Contains('opacity: calc(var(--sword-energy) * .9)')) 'Only quota-bearing swords may remain visibly modelled'
Assert-True ($css.Contains('.formation-sword::after')) 'Qingzhu sword must retain a separate guard detail layer'
Assert-True ($css.Contains('repeating-linear-gradient(180deg')) 'Qingzhu sword spine must expose bamboo-joint modelling'
Assert-True (-not $css.Contains('.stray-sword')) 'Decorative stray sword styling must be removed'
Assert-True ($css.Contains('font-family: Baskerville, "Times New Roman", Georgia, serif')) 'Quota numeral must use the restrained classical serif stack'
Assert-True ($css.Contains('background-clip: text')) 'Quota numeral must render its jade material inside the glyphs'
Assert-True ($css.Contains('-webkit-text-fill-color: transparent')) 'Quota numeral must expose the jade gradient instead of flat white'
Assert-True ($css.Contains('paint-order: stroke fill')) 'Quota numeral must keep a fine dark jade outline'
Assert-True ($css.Contains('stroke: var(--spirit-shadow)')) 'Quota numeral outline must share the spirit shadow color'
Assert-True ($css.Contains('@keyframes jadeNumeralBreathe')) 'Quota numeral must have a restrained material breathing animation'
Assert-True ($css.Contains('animation: jadeNumeralBreathe')) 'Quota numeral must use the material breathing animation'
Assert-True ($css.Contains('radial-gradient(ellipse, var(--spirit-glow)')) 'Quota eye aura must consume the shared spirit glow'
Assert-True ($css.Contains('--formation-eye-x: 98px')) 'Formation eye must expose one shared horizontal center'
Assert-True ($css.Contains('--content-axis-y: 168px')) 'Formation eye and quota ledger must expose one shared visual axis'
Assert-True ($css.Contains('--formation-eye-y: var(--content-axis-y)')) 'Formation eye must derive its vertical center from the shared visual axis'
Assert-True ($css.Contains('--formation-left: -22px')) 'Formation must expose its card-relative horizontal offset'
Assert-True ($css.Contains('--formation-top: 46px')) 'Formation must expose its card-relative vertical offset'
Assert-True ($css.Contains('left: calc(var(--formation-eye-x) - 80px)')) 'Quota percentage must derive its horizontal position from the formation eye center'
Assert-True ($css.Contains('top: calc(var(--formation-eye-y) - 46px + var(--quota-optical-y))')) 'Quota percentage must derive its vertical position from the formation eye center with optical correction'
Assert-True ($css.Contains('top: var(--content-axis-y)')) 'Quota ledger must derive its vertical position from the shared visual axis'
Assert-True ($css.Contains('transform: translateY(-50%)')) 'Quota ledger must center itself on the shared visual axis'
Assert-True ($css.Contains('animation: ledgerReveal')) 'Quota ledger reveal animation must preserve its shared-axis transform'
Assert-True ($css.Contains('left: calc(var(--formation-eye-x) - var(--formation-left) - 17px)')) 'Formation core must share the quota horizontal center'
Assert-True ($css.Contains('top: calc(var(--formation-eye-y) - var(--formation-top) - 17px)')) 'Formation core must share the quota vertical center'
Assert-True ($css.Contains('.ledger-item--cycle strong,') -and $css.Contains('.ledger-item--balance strong {')) 'Cycle use and account balance must share one value scale rule'
Assert-True ($css.Contains('.mortal-motto {')) 'Mortal-world motto inscriptions must have a dedicated style rule'
Assert-True ([regex]::IsMatch($css, '(?s)\.card-foot\s*\{.*?justify-content:\s*center;.*?gap:\s*1\.2em;')) 'Mortal-world motto inscriptions must gather at the card center with restrained separation'
Assert-True ($css.Contains('font-family: STKaiti, KaiTi, serif')) 'Mortal-world motto inscriptions must use the restrained calligraphic stack'
Assert-True ($css.Contains('color: rgba(117, 217, 182, .46)')) 'Mortal-world motto inscriptions must stay below primary quota data'
Assert-True ($css.Contains('letter-spacing: .18em')) 'Mortal-world motto inscriptions must use spacious seal-scroll tracking'
Assert-True (-not $css.Contains('.formation-bloom')) 'Blurred formation overlay styling must be removed'
Assert-True (-not $css.Contains('@keyframes windRun')) 'Obsolete wind-current animation must be removed'
Assert-True (-not $css.Contains('@keyframes thunderRun')) 'Obsolete thunder animation must be removed'
Assert-True ($css.Contains('@keyframes sealAwaken')) 'Missing one-shot awakening sequence'
Assert-True ($css.Contains('animation: sealAwaken 1.75s')) 'Awakening sequence must stay under 1.8 seconds'
Assert-True ($css.Contains('@media (prefers-reduced-motion: reduce)')) 'Missing reduced-motion treatment'
Assert-True ($css.Contains('.antigravity-page {')) 'Antigravity page must have a dedicated visual layer'
Assert-True ($css.Contains('.model-ledger--gemini')) 'Gemini model ledger must have a dedicated layer'
Assert-True ($css.Contains('.model-ledger--claude')) 'Claude and GPT model ledger must have a dedicated layer'
Assert-True ($css.Contains('@keyframes scrollPageIn')) 'Page switch must use a short scroll reveal'
Assert-True (-not $css.Contains('rotateY(')) 'Card page switch must not flip the card'
Assert-True ($css.Contains('animation: none !important')) 'Reduced-motion mode must stop continuous motion'
Assert-True ($css.Contains('transition-duration: .001ms !important')) 'Reduced-motion mode must suppress state-transition movement'
Assert-True ([regex]::IsMatch($css, '(?s)@media \(prefers-reduced-motion: reduce\).*?\.quota-ledger\s*\{.*?transform:\s*translateY\(-50%\);')) 'Reduced-motion mode must preserve quota ledger alignment'

Assert-True ($js.Contains('function setUsed(value)')) 'Missing reusable setUsed interface'
Assert-True ($js.Contains('Number.isFinite(Number(value))')) 'setUsed must guard non-finite input'
Assert-True ($js.Contains('const swordPairs = [[5, 6], [4, 7], [3, 8], [2, 9], [1, 10], [0, 11]]')) 'Sword energy must unfold symmetrically from the formation eye'
Assert-True ($js.Contains('const pairEnergy = remaining * swordPairs.length')) 'Sword pair energy must derive continuously from remaining quota'
Assert-True ($js.Contains("sword.style.setProperty('--sword-energy', energy.toFixed(3))")) 'Each mirrored sword must receive continuous quota energy'
Assert-True ($js.Contains("sword.classList.toggle('is-lit', energy > 0)")) 'Sword slots must retain a semantic lit state when they carry quota energy'
Assert-True ($js.Contains('setUsed(Number(button.dataset.used))')) 'Demo controls must use the public updater'
Assert-True ($js.Contains("unlockButton.addEventListener('click'")) 'Unlock button behavior must remain interactive'
Assert-True ($js.Contains('window.setUsed = setUsed')) 'setUsed must remain available to future integrations'
Assert-True ($js.Contains("fetch('/api/antigravity-quota'")) 'Antigravity page must use the local read-only API'
Assert-True ($js.Contains("sessionStorage.setItem('quota-card-page'")) 'Page preference must be scoped to the browser session'
Assert-True ($js.Contains("widget.dataset.page = page")) 'Page switch must use the stable card state root'
Assert-True ($js.Contains("status === 'expired'")) 'Expired Antigravity data must have an explicit rendering path'

$swordPairs = @(@(5, 6), @(4, 7), @(3, 8), @(2, 9), @(1, 10), @(0, 11))
foreach ($state in @(
    @{ Used = .20; ExpectedVisible = 10 },
    @{ Used = .55; ExpectedVisible = 6 },
    @{ Used = .85; ExpectedVisible = 2 }
)) {
    $remaining = 1 - $state.Used
    $pairEnergy = $remaining * $swordPairs.Count
    $energies = @(0.0) * 12

    for ($pairIndex = 0; $pairIndex -lt $swordPairs.Count; $pairIndex++) {
        $energy = [Math]::Min(1.0, [Math]::Max(0.0, $pairEnergy - $pairIndex))
        foreach ($swordIndex in $swordPairs[$pairIndex]) { $energies[$swordIndex] = $energy }
    }

    $visible = @($energies | Where-Object { $_ -gt 0 }).Count
    $energyEquivalent = ($energies | Measure-Object -Sum).Sum
    Assert-True ($visible -eq $state.ExpectedVisible) "Used $($state.Used) must illuminate $($state.ExpectedVisible) symmetric sword slots"
    Assert-True ([Math]::Abs($energyEquivalent - ($remaining * 12)) -lt .0001) "Used $($state.Used) sword energy must exactly equal remaining quota"
    for ($pairIndex = 0; $pairIndex -lt $swordPairs.Count; $pairIndex++) {
        $pair = $swordPairs[$pairIndex]
        Assert-True ([Math]::Abs($energies[$pair[0]] - $energies[$pair[1]]) -lt .0001) "Used $($state.Used) sword pair $pairIndex must stay mirrored"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Host "FAIL: $_" -ForegroundColor Red }
    exit 1
}

Write-Host 'PASS: mortal seal scroll structure, state interfaces, and local assets satisfy the visual contract.' -ForegroundColor Green
