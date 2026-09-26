"""Assemble the two approved visual drafts without changing their sources."""
from pathlib import Path
import re
import json

root = Path(__file__).resolve().parents[1]
pages = []
for filename, selector in [('codex-five-hour-quota-concept-v3.html', 'seal-card'), ('antigravity-quota-concept-v4.html', 'card')]:
    source = (root / filename).read_text(encoding='utf-8')
    head = source.split('<head>', 1)[1].split('</head>', 1)[0]
    card = re.search(r'<article\b.*?</article>', source, re.S).group()
    card = card.replace('>概念</span>', '>示例</span>')
    card = re.sub(r'<button class="seal-lock".*?</button>', '', card, flags=re.S)
    if filename == 'antigravity-quota-concept-v4.html':
        card = re.sub(r'<h2 class="title">.*?</h2>', '', card, flags=re.S)
    card = card.replace('反重力概念稿4，示例额度', 'Antigravity 额度卡，示例数据')
    head += '<style>html,body{margin:0!important;padding:0!important;width:480px!important;height:270px!important;min-height:0!important;overflow:hidden!important;background:transparent!important}body:before,body:after{display:none!important}.five-hour-concept{margin:0!important;padding:0!important;width:480px!important;max-width:none!important}.seal-card,.card{width:480px!important;height:270px!important;transform:none!important;zoom:1!important;margin:0!important}</style>'
    head += '<style>.five-hour-concept .account-actions{right:81px;top:13px;height:28px}.editorial-mark{top:24%}</style>'
    # The concept's relative positioning pushes the gold motto band above the card.
    # Restore its bottom anchor and remove the auto margins that shift its center.
    head += '<style>.five-hour-concept .motto{position:absolute;top:auto;bottom:10px;left:50%;margin:0;transform:translateX(-50%);background:none;box-shadow:none}</style>'
    pages.append(f'<!doctype html><html lang="zh-CN"><head>{head}</head><body><div class="five-hour-concept" data-five-state="full">{card}</div></body></html>')

template = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>凡人额度卡 · 正式版第一稿</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100dvh;display:grid;place-items:center;background:radial-gradient(ellipse at 50% 35%,#203b31,#081410 72%);color:#e7e7d6;font-family:STKaiti,KaiTi,serif}main{width:min(480px,calc(100vw - 32px));margin:32px 0}header{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:18px}h1{font-size:20px;font-weight:400;letter-spacing:.15em;margin:0}header span{font:10px Consolas,monospace;color:#a68b52}.viewport{width:100%;aspect-ratio:480/270;position:relative;filter:drop-shadow(0 24px 30px #0008)}.pages{width:480px;height:270px;transform-origin:top left}iframe{display:block;width:480px;height:270px;border:0}iframe[hidden]{display:none}nav{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:22px}button{font:14px STKaiti,KaiTi,serif;color:#94a394;background:transparent;border:1px solid #a68b5238;padding:8px 16px;cursor:pointer;border-radius:3px}button[aria-selected=true]{color:#e7e7d6;background:#8cbca514;border-color:#a68b52}button:focus-visible{outline:2px solid #8cbca5;outline-offset:4px}footer{text-align:center;font-size:11px;color:#94a394;margin-top:18px;letter-spacing:.06em}
</style></head><body><main><header><h1>凡人 · 额度图卷</h1><span>EDITION 01</span></header>
<div class="viewport"><div class="pages"><iframe id="page-0" title="第一页：Codex 额度卡"></iframe><iframe id="page-1" title="第二页：Antigravity 额度卡" hidden></iframe><button class="page-switch" type="button" aria-label="切换到 Antigravity" title="切换到 Antigravity" aria-controls="page-0 page-1"><span aria-hidden="true">引</span></button></div></div>
<footer>正式版第一稿 · 示例数据，未接入实时额度</footer></main>
<script>
const documents = PAGE_DOCUMENTS;
const frames = [...document.querySelectorAll('iframe')];
const pageSwitch = document.querySelector('.page-switch');
let currentPage = 0;
frames.forEach((frame, i) => frame.srcdoc = documents[i]);
pageSwitch.addEventListener('click',()=>{currentPage=1-currentPage;frames.forEach((frame,i)=>frame.hidden=i!==currentPage);const label=currentPage===0?'切换到 Antigravity':'切换到 Codex';pageSwitch.setAttribute('aria-label',label);pageSwitch.title=label;});
new ResizeObserver(([entry])=>{document.querySelector('.pages').style.transform=`scale(${entry.contentRect.width/480})`}).observe(document.querySelector('.viewport'));
</script></body></html>'''
shared_css = (root / 'styles/mortal-seal-card.css').read_text(encoding='utf-8')
control_css = shared_css[shared_css.index('.seal-lock {'):shared_css.index('.seal-formation {')]
template = template.replace('class="page-switch"', 'class="page-switch antigravity-seal"')
lock = '<button class="seal-lock" type="button" aria-label="窗口锁定（桌面功能尚未接入）" title="窗口锁定：桌面功能尚未接入" disabled><svg viewBox="0 0 24 24" aria-hidden="true"><path class="lock-shackle" d="M7.5 10V7.4a4.5 4.5 0 0 1 9 0V10"/><path d="M6.2 10h11.6v9H6.2z"/><path d="M12 13.1v3"/></svg></button>'
template = template.replace('<span aria-hidden="true">引</span></button>', '<span aria-hidden="true">引</span></button>' + lock)
template = template.replace('</style></head>', control_css + '.pages{position:relative;--ward-gold:#d5b564;--moon-white:#e7e7d6}.page-switch{position:absolute;z-index:10;right:49px;top:15px}.pages>.seal-lock{position:absolute;z-index:10;right:14px;top:13px;cursor:default}</style></head>')
def normalized_output(value):
    return '\n'.join(line.rstrip() for line in value.splitlines()) + '\n'

(root / 'quota-card-formal-v1.html').write_text(
    normalized_output(template.replace('PAGE_DOCUMENTS', json.dumps(pages, ensure_ascii=False).replace('</', '<\\/'))),
    encoding='utf-8',
)

# The desktop entry contains the approved cards only. Stable IDs are injected
# into the generated copies so the source concepts remain the visual baseline.
app_pages = list(pages)
app_pages[0] = app_pages[0].replace(
    '</head>',
    '<style>.five-hour-concept .seal-card{--card-radius:8px;border-radius:0!important;clip-path:none!important}</style></head>',
)
app_pages[0] = app_pages[0].replace('class="sync-status" data-state="preview"', 'class="sync-status" id="codexStatus" data-state="preview"')
app_pages[0] = app_pages[0].replace('<span class="plan-mark">PLUS</span>', '<span class="plan-mark" id="planType">—</span>')
app_pages[0] = app_pages[0].replace('<strong class="ledger-value">$39.36</strong>', '<strong class="ledger-value" id="creditBalance">—</strong>')
app_pages[0] = app_pages[0].replace('<span class="ledger-reset">9月21日 07:45 到期</span>', '<span class="ledger-reset" id="resetCreditExpiry">重置卡信息待同步</span>')
ag_ids = [
    ('agGeminiWeekly', 'agGeminiWeeklyReset'), ('agGeminiFiveHour', 'agGeminiFiveHourReset'),
    ('agClaudeWeekly', 'agClaudeWeeklyReset'), ('agClaudeFiveHour', 'agClaudeFiveHourReset'),
]
counter = iter(ag_ids)
def add_ag_ids(match):
    value_id, reset_id = next(counter)
    return f'<strong id="{value_id}">—</strong><time id="{reset_id}">待同步</time>'
app_pages[1] = re.sub(r'<strong>.*?</strong><time(?: datetime="[^"]*")?>.*?</time>', add_ag_ids, app_pages[1], count=4)
app_pages[1] = app_pages[1].replace('<footer class="foot"><span>概念预览 · 非实时数据</span>', '<footer class="foot"><span id="agCredits">可用灵石 —</span>')

app_template = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=480,initial-scale=1">
<title>凡人额度卡</title><style>
*{box-sizing:border-box}html,body{margin:0;width:480px;height:270px;overflow:hidden;background:#07130f}.pages{position:relative;width:480px;height:270px;border-radius:0;overflow:hidden;background:#07130f;--ward-gold:#d5b564;--moon-white:#e7e7d6}iframe{display:block;width:480px;height:270px;border:0;background:#07130f}iframe[hidden]{display:none}.drag-surface{position:absolute;inset:0;z-index:10}.pages>.page-switch,.pages>.seal-lock{position:absolute;z-index:20;-webkit-app-region:no-drag}.pages>.page-switch{right:49px;top:15px}.pages>.seal-lock{right:14px;top:13px}.page-switch,.pages>.seal-lock{cursor:pointer}
APP_CONTROL_CSS</style></head><body><div class="pages">
<iframe id="page-codex" title="Codex 额度卡" srcdoc="CODEX_PAGE"></iframe><iframe id="page-antigravity" title="Antigravity 额度卡" srcdoc="ANTIGRAVITY_PAGE" hidden></iframe>
<div id="drag-surface" class="pywebview-drag-region" aria-hidden="true"></div>
<button id="page-switch" class="page-switch antigravity-seal" type="button" aria-label="切换到 Antigravity" title="切换到 Antigravity"><span aria-hidden="true">引</span></button>
<button id="lock-button" class="seal-lock" type="button" aria-label="锁定位置" title="锁定位置并启用鼠标穿透" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path class="lock-shackle" d="M7.5 10V7.4a4.5 4.5 0 0 1 9 0V10"/><path d="M6.2 10h11.6v9H6.2z"/><path d="M12 13.1v3"/></svg></button>
</div><script src="/scripts/quota-card-app.js"></script></body></html>'''
app_html = app_template.replace('APP_CONTROL_CSS', control_css)
app_html = app_html.replace('CODEX_PAGE', app_pages[0].replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'))
app_html = app_html.replace('ANTIGRAVITY_PAGE', app_pages[1].replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'))
(root / 'quota-card-app.html').write_text(normalized_output(app_html), encoding='utf-8')
print('Created quota-card-formal-v1.html and quota-card-app.html')
