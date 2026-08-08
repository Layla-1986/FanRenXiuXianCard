# Nascent Soul Artifact Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the 480 × 270 quota card around Nascent Soul cyan-green aura, a dynamic Great Geng sword formation, a jade Qingzhu Fengyun main sword, and horizontal Wind-Thunder Wings whose center marks the usage boundary.

**Architecture:** Keep the existing single-file HTML prototype and its `--used` state contract. Localize the four user references into versioned project assets, layer the background, formation, sword, and wing effects with HTML/CSS, and make `setUsed(value)` drive the remaining percentage, lit sword count, and wing position. Extend the existing PowerShell contract test before each visual slice, then finish with computed-geometry and browser screenshot checks.

**Tech Stack:** HTML5, CSS custom properties and animations, inline SVG image cropping, vanilla JavaScript, PowerShell structural tests, local browser verification.

## Global Constraints

- Keep the formal floating card at exactly 480 × 270 pixels.
- Keep `assets/hanli-nangong-background.png` as the card background and preserve the face-to-face visual center.
- Preserve `--used`, `#percent`, `#used`, the three demo buttons, the top-right unlock button, and the independent five-hour quota.
- Use the user references as local assets; do not depend on temporary clipboard paths at runtime.
- Wind-Thunder Wings remain horizontal, approximately 72 × 34 pixels, 68%–76% opaque, and centered on the used/remaining boundary.
- Great Geng rings rotate while sword positions do not rotate with the rings.
- Remaining quota controls 0–12 lit swords using `Math.round(remaining * 12)`.
- Respect `prefers-reduced-motion: reduce` by stopping continuous ring, sword, wing, lightning, and particle animation.
- Do not modify `index.html`, connect a live Codex/Antigravity quota API, or build a desktop installer.

---

## File Map

- `original-artifact-refined.html`: owns the showcase page, 480 × 270 card markup, all visual CSS, demo state logic, and accessibility fallbacks.
- `tests/visual-spec.ps1`: verifies local assets, stable DOM hooks, horizontal wing geometry, dynamic sword-count logic, and reduced-motion support.
- `assets/nascent-soul-aura-reference.png`: immutable palette and light-flow reference copied from user image one; not rendered as the card background.
- `assets/dageng-sword-array-v2.png`: transparent Great Geng formation texture copied from user image two.
- `assets/qingzhu-fengyun-sword-v2.png`: transparent jade sword texture copied from user image three.
- `assets/wind-thunder-wings-v2.png`: transparent horizontal wing texture copied from user image four.

---

### Task 1: Localize the confirmed reference assets

**Files:**
- Create: `assets/nascent-soul-aura-reference.png`
- Create: `assets/dageng-sword-array-v2.png`
- Create: `assets/qingzhu-fengyun-sword-v2.png`
- Create: `assets/wind-thunder-wings-v2.png`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: the four confirmed clipboard PNG files at the exact paths listed below.
- Produces: stable project-relative assets for later HTML/CSS tasks.

- [ ] **Step 1: Replace the old asset contract with local and rendered asset lists**

In `tests/visual-spec.ps1`, replace `$assets` and its loop with:

```powershell
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
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

Expected: FAIL four times with `Missing local asset` for the new versioned PNG files.

- [ ] **Step 3: Copy the user references into the project**

Run these PowerShell commands from the project root:

```powershell
Copy-Item -LiteralPath 'C:\Users\Lelay\AppData\Local\Temp\codex-clipboard-0f34bcee-accf-4bd5-9ea0-8826fef204ec.png' -Destination 'assets\nascent-soul-aura-reference.png'
Copy-Item -LiteralPath 'C:\Users\Lelay\AppData\Local\Temp\codex-clipboard-0ea51ab1-2712-4645-bdf8-fa879aa47fb0.png' -Destination 'assets\dageng-sword-array-v2.png'
Copy-Item -LiteralPath 'C:\Users\Lelay\AppData\Local\Temp\codex-clipboard-68ff0c03-8229-4955-8dd5-3480e15ed3a2.png' -Destination 'assets\qingzhu-fengyun-sword-v2.png'
Copy-Item -LiteralPath 'C:\Users\Lelay\AppData\Local\Temp\codex-clipboard-7cb18433-3109-4a39-b0d1-715c5b0ee65f.png' -Destination 'assets\wind-thunder-wings-v2.png'
```

Do not overwrite the previous `dageng-sword-array.png`, `qingzhu-swords.png`, or `wind-thunder-wings.png`; Git should retain both visual generations.

- [ ] **Step 4: Run the asset test and verify GREEN**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
```

Expected: PASS with every new local asset present.

- [ ] **Step 5: Commit the localized assets**

```powershell
git add -- assets/nascent-soul-aura-reference.png assets/dageng-sword-array-v2.png assets/qingzhu-fengyun-sword-v2.png assets/wind-thunder-wings-v2.png tests/visual-spec.ps1
git commit -m "添加元婴灵气法宝参考素材"
```

---

### Task 2: Establish the Nascent Soul palette and card depth

**Files:**
- Modify: `original-artifact-refined.html:8-12`
- Modify: `original-artifact-refined.html:29-31`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `assets/hanli-nangong-background.png` and CSS variable `--used`.
- Produces: `.nascent-aura`, stable theme tokens, a face-preserving background mask, and a readable bottom data layer.

- [ ] **Step 1: Add failing theme and layer assertions**

Append these assertions to `tests/visual-spec.ps1`:

```powershell
Assert-True ($html.Contains('--aura-cyan:#8fe7ee')) 'Missing Nascent Soul cyan theme token'
Assert-True ($html.Contains('--jade:#4fd6a2')) 'Missing jade sword theme token'
Assert-True ($html.Contains('--geng-gold:#d9bd67')) 'Missing Great Geng gold theme token'
Assert-True ($html.Contains('class="nascent-aura"')) 'Missing Nascent Soul aura layer'
Assert-True ($html.Contains('url("assets/hanli-nangong-background.png")')) 'Face-to-face background must remain active'
```

- [ ] **Step 2: Run the test and verify RED**

Run the PowerShell contract test. Expected: FAIL for the three theme tokens and `.nascent-aura`.

- [ ] **Step 3: Add exact theme tokens and layered masks**

Change the `.widget` declaration to begin with:

```css
.widget{
  --used:.2;
  --danger:0;
  --ink:#031315;
  --deep-cyan:#082b31;
  --aura-cyan:#8fe7ee;
  --aura-ice:#d9fbff;
  --jade:#4fd6a2;
  --jade-deep:#0b745e;
  --geng-gold:#d9bd67;
  width:480px;
  height:270px;
}
```

Retain `url("assets/hanli-nangong-background.png")`, `background-size:cover`, and `background-position:center 47%`. Rebuild the overlays so the left formation zone and bottom 58px are dark cyan, while the central face area uses a transparent radial window.

Use this face-preserving overlay on `.widget::before`:

```css
.widget::before{
  content:"";
  position:absolute;
  inset:0;
  z-index:1;
  pointer-events:none;
  background:
    radial-gradient(ellipse at 56% 38%,transparent 0 21%,rgba(3,20,23,.06) 39%,rgba(2,15,18,calc(.18 + var(--used)*.18)) 100%),
    linear-gradient(90deg,rgba(2,18,20,.82) 0 29%,transparent 51% 73%,rgba(2,17,19,.34) 100%),
    linear-gradient(0deg,rgba(2,14,17,.88) 0 22%,transparent 54%);
}
```

- [ ] **Step 4: Add a non-interactive aura layer**

Insert immediately after `<i class="fog"></i>`:

```html
<i class="nascent-aura" aria-hidden="true"></i>
```

Implement it as two restrained cyan/green energy ribbons using `.nascent-aura`, `.nascent-aura::before`, and `.nascent-aura::after`. Set `pointer-events:none`, keep it below `.top` and `.content`, and use opacity below `.28` over the faces.

```css
.nascent-aura{position:absolute;z-index:2;inset:0;pointer-events:none;overflow:hidden;opacity:calc(.16 + var(--used)*.1)}
.nascent-aura::before,.nascent-aura::after{content:"";position:absolute;left:17%;top:34%;width:72%;height:46%;border-radius:50%;filter:blur(8px);mix-blend-mode:screen}
.nascent-aura::before{background:conic-gradient(from 205deg at 38% 55%,transparent 0 20%,rgba(143,231,238,.24) 24%,transparent 31% 63%,rgba(79,214,162,.2) 68%,transparent 75%);animation:auraDrift 11s ease-in-out infinite}
.nascent-aura::after{background:radial-gradient(ellipse,rgba(217,251,255,.16),transparent 66%);animation:auraBreathe 7s ease-in-out infinite reverse}
```

- [ ] **Step 5: Run the contract test and commit**

Run the PowerShell test and `git diff --check`. Expected: both exit successfully.

```powershell
git add -- original-artifact-refined.html tests/visual-spec.ps1
git commit -m "重塑元婴灵气卡片色彩层次"
```

---

### Task 3: Rebuild the Great Geng formation and Qingzhu sword hierarchy

**Files:**
- Modify: `original-artifact-refined.html:12-15`
- Modify: `original-artifact-refined.html:33-37`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `assets/dageng-sword-array-v2.png`, `assets/qingzhu-fengyun-sword-v2.png`, and `#widget` state.
- Produces: `.formation-disc`, three independently animated rings, twelve fixed `.formation-sword` slots, `.main-sword-asset`, and `.is-lit` sword state.

- [ ] **Step 1: Add failing formation assertions**

Replace obsolete balance-class and old-texture assertions with:

```powershell
Assert-True ($html.Contains('assets/dageng-sword-array-v2.png')) 'Great Geng v2 texture is not rendered'
Assert-True ($html.Contains('assets/qingzhu-fengyun-sword-v2.png')) 'Qingzhu v2 sword texture is not rendered'
Assert-True ($html.Contains('class="formation-disc"')) 'Missing perspective formation disc'
Assert-True ($html.Contains('class="ring ring-outer"')) 'Missing outer formation ring'
Assert-True ($html.Contains('class="ring ring-middle"')) 'Missing middle formation ring'
Assert-True ($html.Contains('class="ring ring-inner"')) 'Missing inner formation ring'
Assert-True (($html | Select-String 'class="formation-sword"' -AllMatches).Matches.Count -eq 12) 'Formation must expose twelve sword slots'
Assert-True ($html.Contains('class="main-sword-asset"')) 'Missing Qingzhu main sword asset'
Assert-True (-not $html.Contains('.formation-swords{animation:')) 'Sword positions must not rotate with formation rings'
```

- [ ] **Step 2: Run the test and verify RED**

Run the PowerShell contract test. Expected: FAIL for the v2 references, perspective disc, three rings, and main sword asset.

- [ ] **Step 3: Replace the formation markup**

Use this structure inside `.core` before `#percent`:

```html
<div class="geng-formation" aria-hidden="true">
  <div class="formation-disc">
    <img class="geng-texture" src="assets/dageng-sword-array-v2.png" alt="">
    <i class="ring ring-outer"></i>
    <i class="ring ring-middle"></i>
    <i class="ring ring-inner"></i>
    <i class="formation-runes"></i>
    <i class="formation-particles"></i>
  </div>
  <span class="formation-swords">
    <i class="formation-sword"></i><i class="formation-sword"></i>
    <i class="formation-sword"></i><i class="formation-sword"></i>
    <i class="formation-sword"></i><i class="formation-sword"></i>
    <i class="formation-sword"></i><i class="formation-sword"></i>
    <i class="formation-sword"></i><i class="formation-sword"></i>
    <i class="formation-sword"></i><i class="formation-sword"></i>
  </span>
  <i class="formation-core"></i>
</div>
<div class="qingzhu-formation" aria-hidden="true">
  <img class="main-sword-asset" src="assets/qingzhu-fengyun-sword-v2.png" alt="">
</div>
```

- [ ] **Step 4: Implement the perspective disc without rotating sword positions**

Use a 150 × 150 formation centered near `(105,142)`. Apply `perspective(320px) rotateX(58deg)` to `.formation-disc`, animate `.ring-outer` clockwise in 18s, `.ring-middle` counter-clockwise in 24s, and `.ring-inner` clockwise in 12s. Do not put a rotation animation on `.formation-swords` or `.formation-sword`.

```css
.geng-formation{position:absolute;z-index:1;left:8px;top:17px;width:150px;height:150px}
.formation-disc{position:absolute;inset:7px;transform:perspective(320px) rotateX(58deg);transform-style:preserve-3d}
.ring{position:absolute;border-radius:50%;border:1px solid var(--aura-cyan);box-shadow:0 0 9px rgba(143,231,238,.34),inset 0 0 12px rgba(79,214,162,.18)}
.ring-outer{inset:2px;animation:spin 18s linear infinite}
.ring-middle{inset:20px;border-color:var(--geng-gold);animation:spinReverse 24s linear infinite}
.ring-inner{inset:39px;border-style:dashed;animation:spin 12s linear infinite}
.formation-swords{position:absolute;inset:0;z-index:3;pointer-events:none}
.formation-sword{position:absolute;width:6px;height:30px;opacity:.16;transition:opacity .55s ease,filter .55s ease}
.formation-sword.is-lit{opacity:.96;filter:drop-shadow(0 0 5px var(--jade)) drop-shadow(0 0 9px rgba(143,231,238,.55))}
.formation-sword:nth-child(1){left:72px;top:4px;transform:rotate(0deg)}
.formation-sword:nth-child(2){left:105px;top:12px;transform:rotate(30deg)}
.formation-sword:nth-child(3){left:130px;top:31px;transform:rotate(60deg)}
.formation-sword:nth-child(4){left:140px;top:62px;transform:rotate(90deg)}
.formation-sword:nth-child(5){left:130px;top:94px;transform:rotate(120deg)}
.formation-sword:nth-child(6){left:105px;top:113px;transform:rotate(150deg)}
.formation-sword:nth-child(7){left:72px;top:121px;transform:rotate(180deg)}
.formation-sword:nth-child(8){left:39px;top:113px;transform:rotate(210deg)}
.formation-sword:nth-child(9){left:14px;top:94px;transform:rotate(240deg)}
.formation-sword:nth-child(10){left:4px;top:62px;transform:rotate(270deg)}
.formation-sword:nth-child(11){left:14px;top:31px;transform:rotate(300deg)}
.formation-sword:nth-child(12){left:39px;top:12px;transform:rotate(330deg)}
```

Place the twelve sword slots around an ellipse with fixed `nth-child` transforms at 30-degree increments. Style the unlit base at opacity `.13`–`.2`; style `.formation-sword.is-lit` with jade/ice highlights and a restrained gold spine. Give only the blade glow/pseudo-element a 4–7s phase-shifted floating animation so its anchor remains fixed.

- [ ] **Step 5: Place the Qingzhu main sword behind the percentage**

Render `.main-sword-asset` at approximately 24 × 104px using `object-fit:cover`, a crop/mask that preserves the jade blade, opacity `.58`–`.72`, and jade/gold drop shadows. Keep `.percent` at a higher `z-index`; its visual center and the formation core must coincide.

```css
.qingzhu-formation{position:absolute;z-index:4;left:71px;top:24px;width:24px;height:104px;pointer-events:none}
.main-sword-asset{width:100%;height:100%;object-fit:cover;object-position:center 30%;opacity:.66;mix-blend-mode:screen;mask-image:linear-gradient(#000 0 82%,transparent 100%);filter:drop-shadow(0 0 5px var(--jade)) drop-shadow(0 0 10px rgba(217,189,103,.35));animation:mainSwordBreathe 5.6s ease-in-out infinite}
.percent{position:relative;z-index:8}
```

- [ ] **Step 6: Run the contract test and commit**

Run the PowerShell test and `git diff --check`. Expected: PASS.

```powershell
git add -- original-artifact-refined.html tests/visual-spec.ps1
git commit -m "重构大庚剑阵与青竹蜂云剑"
```

---

### Task 4: Turn horizontal Wind-Thunder Wings into the progress marker

**Files:**
- Modify: `original-artifact-refined.html:16-17`
- Modify: `original-artifact-refined.html:39-43`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `assets/wind-thunder-wings-v2.png` and `--used` in the inclusive range `0..1`.
- Produces: `.wind-thunder-wings` centered at `calc(4% + var(--used) * 92%)`, a stable `.wing-core`, and a segmented `.progress-rail`.

- [ ] **Step 1: Replace the obsolete vertical-wing assertions**

Remove assertions for `width:42px;height:24px`, `rotate:90deg`, and the neutral grayscale filter. Add:

```powershell
Assert-True ($html.Contains('assets/wind-thunder-wings-v2.png')) 'Wind-Thunder Wings v2 texture is not rendered'
Assert-True ($html.Contains('width:72px;height:34px')) 'Wing marker must use the confirmed 72 by 34 geometry'
Assert-True ($html.Contains('left:calc(4% + var(--used)*92%)')) 'Wing marker is not tied to --used'
Assert-True ($html.Contains('translate:-50% 0')) 'Wing center is not anchored to the usage boundary'
Assert-True (-not $html.Contains('rotate:90deg')) 'Wing marker must remain horizontal'
Assert-True ($html.Contains('opacity:.72')) 'Wing marker must remain semi-transparent'
```

- [ ] **Step 2: Run the test and verify RED**

Run the PowerShell contract test. Expected: FAIL for the v2 texture, 72 × 34 geometry, horizontal orientation, and opacity.

- [ ] **Step 3: Replace the wing viewport and keep its center fixed**

Use this markup inside `.wing-meter`:

```html
<i class="progress-rail" aria-hidden="true"></i>
<div class="wind-thunder-wings" aria-label="风雷翅进度游标" role="img">
  <svg class="wing-asset" viewBox="0 100 1536 820" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
    <image href="assets/wind-thunder-wings-v2.png" x="0" y="0" width="1536" height="1024"/>
  </svg>
  <i class="wing-core"></i>
</div>
<svg class="lightning" viewBox="0 0 86 40" aria-hidden="true">
  <path class="silver" d="M3 23l16-5 10 6 14-13 14 13 10-6 16 5M8 31l17-5 10 6 8-9 8 9 10-6 17 5"/>
  <path class="gold" d="M9 18l14 4 9-6 11 8 11-8 9 6 14-4"/>
</svg>
```

Set the rail center at `top:42px;height:4px`. Set `.wind-thunder-wings` to `top:27px;width:72px;height:34px;left:calc(4% + var(--used)*92%);translate:-50% 0;opacity:.72`. Do not animate or translate the parent marker vertically.

```css
.progress-rail{position:absolute;z-index:4;left:4%;right:4%;top:42px;height:4px;border-radius:8px;background:linear-gradient(90deg,rgba(116,86,59,.72) 0 calc(var(--used)*100%),var(--aura-cyan) calc(var(--used)*100%) 82%,var(--jade) 94%,var(--geng-gold) 100%)}
.wind-thunder-wings{position:absolute;z-index:9;left:calc(4% + var(--used)*92%);top:27px;width:72px;height:34px;translate:-50% 0;opacity:.72;transform-origin:50% 50%;transition:left .65s cubic-bezier(.2,.8,.2,1);filter:drop-shadow(0 0 calc(4px + var(--used)*5px) rgba(143,231,238,.72))}
.wing-asset{display:block;width:100%;height:100%;overflow:visible;mix-blend-mode:screen;transform-origin:50% 50%;animation:wingBeat 3.8s ease-in-out infinite}
.wing-core{position:absolute;left:50%;top:50%;width:8px;height:8px;translate:-50% -50%;rotate:45deg;background:linear-gradient(135deg,var(--geng-gold),var(--aura-ice) 48%,var(--jade));filter:drop-shadow(0 0 5px var(--aura-cyan))}
.lightning{position:absolute;z-index:10;left:calc(4% + var(--used)*92%);top:24px;width:72px;height:40px;translate:-50% 0;pointer-events:none;transition:left .65s cubic-bezier(.2,.8,.2,1)}
```

- [ ] **Step 4: Animate only internal wing and lightning layers**

Animate `.wing-asset` with a subtle `scaleY(.96)` to `scaleY(1.02)` beat around `transform-origin:50% 50%`. Use cyan-white lightning as the primary stroke and `--geng-gold` for low-frequency secondary sparks. Make lightning opacity and rail-flow intensity increase with `--used`, while keeping the wing center and size constant.

- [ ] **Step 5: Keep labels clear of the wing**

Place `#used` and reset time below the rail at opposite ends. Confirm the wing at 20%, 55%, and 85% never covers either label. Keep the five-hour quota below as an independent low-contrast line.

- [ ] **Step 6: Run the contract test and commit**

Run the PowerShell test and `git diff --check`. Expected: PASS.

```powershell
git add -- original-artifact-refined.html tests/visual-spec.ps1
git commit -m "将横向风雷翅接入额度进度"
```

---

### Task 5: Generalize quota state and reduced-motion behavior

**Files:**
- Modify: `original-artifact-refined.html:19-21`
- Modify: `original-artifact-refined.html:57-76`
- Modify: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: `setUsed(value: number)` with any finite numeric value.
- Produces: clamped `safe`, `remaining`, `litSwordCount`, `.is-lit` sword classes, `--used`, `#percent`, and `#used`.

- [ ] **Step 1: Add failing state assertions**

Append:

```powershell
Assert-True ($html.Contains('const litSwordCount=Math.round(remaining*12)')) 'Lit sword count must be derived from remaining quota'
Assert-True ($html.Contains("sword.classList.toggle('is-lit',index<litSwordCount)")) 'Sword slots are not updated from the calculated count'
Assert-True ($html.Contains('Number.isFinite(Number(value))')) 'setUsed must guard non-finite input'
Assert-True ($html.Contains('@media(prefers-reduced-motion:reduce)')) 'Missing reduced-motion treatment'
Assert-True ($html.Contains('.ring,.formation-sword::before,.wing-asset,.lightning')) 'Reduced-motion selector does not cover all continuous artifact animation'
```

- [ ] **Step 2: Run the test and verify RED**

Run the PowerShell contract test. Expected: FAIL for dynamic sword count and finite input guard.

- [ ] **Step 3: Implement the complete state mapping**

Replace `setUsed` with:

```javascript
function setUsed(value){
  const numeric=Number.isFinite(Number(value))?Number(value):0;
  const safe=Math.max(0,Math.min(1,numeric));
  const remaining=1-safe;
  const litSwordCount=Math.round(remaining*12);
  widget.style.setProperty('--used',safe);
  percent.textContent=Math.round(remaining*100)+'%';
  used.textContent='已用 '+Math.round(safe*100)+'%';
  document.querySelectorAll('.formation-sword').forEach((sword,index)=>{
    sword.classList.toggle('is-lit',index<litSwordCount);
  });
}
```

Keep the three existing buttons and call `setUsed(.2)` after their listeners are registered.

- [ ] **Step 4: Complete reduced-motion CSS**

Inside `@media(prefers-reduced-motion:reduce)`, disable animation for `.ring`, `.formation-runes`, `.formation-particles`, `.formation-core`, `.formation-sword::before`, `.main-sword-asset`, `.wing-asset`, `.lightning`, `.progress-rail::after`, `.nascent-aura`, and `.fog`. Disable positional transitions on the wing, core, lightning, and widget, but retain static filters, opacity, and the correct progress position.

```css
@media(prefers-reduced-motion:reduce){
  .ring,.formation-runes,.formation-particles,.formation-core,.formation-sword::before,.main-sword-asset,.wing-asset,.lightning,.progress-rail::after,.nascent-aura,.nascent-aura::before,.nascent-aura::after,.fog{animation:none!important}
  .widget,.wind-thunder-wings,.wing-core,.lightning,.formation-sword{transition:none!important}
}
```

- [ ] **Step 5: Run the full structural verification**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
git diff --check
```

Expected: the test prints `PASS` and both commands exit with code 0.

- [ ] **Step 6: Commit the generalized state behavior**

```powershell
git add -- original-artifact-refined.html tests/visual-spec.ps1
git commit -m "完善剑阵额度联动与低动态模式"
```

---

### Task 6: Browser geometry, responsive, and visual verification

**Files:**
- Modify only if verification exposes a defect: `original-artifact-refined.html`
- Modify only if a corrected invariant needs coverage: `tests/visual-spec.ps1`

**Interfaces:**
- Consumes: local HTTP page `http://127.0.0.1:55569/original-artifact-refined.html`.
- Produces: evidence that the card meets geometry, state, responsive, and reduced-motion acceptance criteria.

- [ ] **Step 1: Start or confirm the local preview server**

Run:

```powershell
Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:55569/original-artifact-refined.html' | Select-Object StatusCode
```

Expected: `StatusCode` is `200`. If the request cannot connect, run the following and repeat the request before opening the browser:

```powershell
Start-Process -FilePath 'E:\anaconda3\python.exe' -ArgumentList '-m','http.server','55569' -WorkingDirectory 'F:\codex\tools\usage_windos' -WindowStyle Hidden
```

- [ ] **Step 2: Verify the three quota states at 480 × 270**

Open the page and click each demo button. Verify:

- 20% used: `80%`, 10 `.formation-sword.is-lit` nodes, wing center at 20% of the rail.
- 55% used: `45%`, 5 `.formation-sword.is-lit` nodes, wing center at 55% of the rail.
- 85% used: `15%`, 2 `.formation-sword.is-lit` nodes, wing center at 85% of the rail.

For each state, evaluate this geometry expression in the page context, with `usedValue` set to `.2`, `.55`, or `.85`:

```javascript
const rail=document.querySelector('.progress-rail').getBoundingClientRect();
const wing=document.querySelector('.wind-thunder-wings').getBoundingClientRect();
const wingCenter=wing.left+wing.width/2;
const expected=rail.left+rail.width*usedValue;
Math.abs(wingCenter-expected)<=1;
```

Expected: `true` for all three values.

- [ ] **Step 3: Verify visual hierarchy**

At the 480 × 270 card size confirm all of the following:

- the percentage is centered over the formation core and is not crossed by sword imagery;
- Han Li and Nangong Wan remain recognizable around the face-to-face center;
- rings rotate independently while the twelve sword anchors remain fixed;
- horizontal wings are semi-transparent and visibly sit on the main rail;
- cyan/ice aura dominates, jade defines swords, and gold remains an accent;
- the two bottom data rows remain legible and do not collide with the wings.

- [ ] **Step 4: Verify narrow layout and reduced motion**

Use a 523 × 792 viewport and confirm there is no horizontal page overflow and the scaled card remains inside `.display`. Emulate `prefers-reduced-motion: reduce`; confirm computed animation names/durations no longer produce continuous ring, sword, aura, wing, lightning, or particle motion while the 20%/55%/85% geometry remains correct.

- [ ] **Step 5: Capture the final preview and run final checks**

Capture one full-page preview and one card-focused screenshot at 20% used. Then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\visual-spec.ps1
git diff --check
git status --short
```

Expected: structural test PASS, no whitespace errors, and no uncommitted implementation files. If verification required a fix, repeat Tasks 6.2–6.5 and commit the fix with a narrow message describing the corrected visual invariant.
