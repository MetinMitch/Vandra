#!/usr/bin/env python3
"""Compare the rebuilt pages against the measured extracts (block rects, section rects, header, text sizes)."""
import json, sys, os, re, asyncio
from playwright.async_api import async_playwright
ROOT = '/home/claude/vandra'
PAGES = {'index': 'index.html', 'store': 'store.html', 'river': 'river.html', 'about': 'about.html', 'stories': 'stories.html',
         'iceland': 'stories-iceland.html', 'norway': 'stories-norway.html', 'contact': 'contact.html', 'community': 'community.html',
         'registration': 'registration.html', 'terms': 'terms.html', 'shipping': 'shipping.html', 'privacy': 'privacy.html'}
JS = r"""() => {
  const out = {secs: [], blocks: {}, texts: [], hdr: null, doc: document.documentElement.scrollHeight};
  document.querySelectorAll('section.sec').forEach(s => { const r = s.getBoundingClientRect(); out.secs.push({id: s.id, y: Math.round(r.y + scrollY), h: Math.round(r.height)}); });
  document.querySelectorAll('.fe').forEach(b => { const r = b.getBoundingClientRect(); const t = b.querySelector('h1,h2,h3,h4,p'); const cs = t ? getComputedStyle(t) : null;
    out.blocks[b.getAttribute('style')] = {r: [Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)], fs: cs ? cs.fontSize : null, lh: cs ? cs.lineHeight : null, ff: cs ? cs.fontFamily : null, tag: t ? t.tagName : null}; });
  const h = document.querySelector('.hdr'); const hr = (h.querySelector('.hdr-d').offsetParent ? h.querySelector('.hdr-d') : h.querySelector('.hdr-m')).getBoundingClientRect();
  out.hdr = {h: hr.height, logo: (() => { const l = h.querySelector('.hdr-logo img, .hdr-mlogo img'); const ls = [...h.querySelectorAll('img')].find(i => i.offsetParent); const r = ls.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]; })(),
    nav: [...h.querySelectorAll('.hdr-nav a')].map(a => { const r = a.getBoundingClientRect(); return {t: a.textContent, x: Math.round(r.x), w: Math.round(r.width), fs: getComputedStyle(a).fontSize}; })};
  return out; }"""

async def main(which):
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for w, h in ((1920, 1080), (375, 812)):
            ctx = await br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            page = await ctx.new_page()
            for key in which:
                ref_p = f'{ROOT}/scrape/computed/{key}-{w}.json'
                if not os.path.exists(ref_p):
                    continue
                ref = json.load(open(ref_p))
                await page.goto(f'file://{ROOT}/site/{PAGES[key]}')
                await page.wait_for_timeout(300)
                got = await page.evaluate(JS)
                # sections
                print(f'=== {key} @{w}  doc {got["doc"]} vs {ref["doc"]}   header {got["hdr"]["h"]:.1f} vs {ref["header"]["h"]}  logo {got["hdr"]["logo"]} vs {ref["header"].get("logo") if w==1920 else ref["header"].get("mlogo")}')
                if w == 1920:
                    print('   nav', [(n['t'], n['x'], n['w'], n['fs']) for n in got['hdr']['nav']], 'vs', [(n['t'], n['r'][0], n['r'][2], n['fs']) for n in ref['header']['nav']['items']])
                rsecs = ref['sections']; gsecs = got['secs']
                for i, rs in enumerate(rsecs):
                    gs = next((g for g in gsecs if g['id'] == 's-' + rs['id'][-6:]), None)
                    if gs is None:
                        print(f'   sec {i} {rs["id"][-6:]} MISSING (kind {rs["kind"]})'); continue
                    dy = gs['y'] - rs['rect'][0]; dh = gs['h'] - rs['rect'][1]
                    flag = '' if abs(dy) <= 4 and abs(dh) <= 4 else '  <<<'
                    print(f'   sec {i} {rs["id"][-6:]} y {gs["y"]} vs {rs["rect"][0]} ({dy:+d})  h {gs["h"]} vs {rs["rect"][1]} ({dh:+d}){flag}')
                    # blocks: match by desktop/mobile area string in the style attr
                    for b in rs['blocks']:
                        area = b['area'].replace(' ', '')
                        keyattr = f'--d:{area};' if w == 1920 else f'--m:{area};'
                        cands = [(k, v) for k, v in got['blocks'].items() if keyattr in k and ('id="s-' + rs['id'][-6:]) or True]
                        # restrict to this section via y range
                        cands = [(k, v) for k, v in got['blocks'].items() if keyattr in k and gs['y'] - 2 <= v['r'][1] <= gs['y'] + gs['h'] + 2]
                        if not cands:
                            if b['type'].endswith('code-block'): continue
                            print(f'      block {b["id"][-8:]} {area} MISSING'); continue
                        v = cands[0][1]
                        d = [v['r'][j] - b['rect'][j] for j in range(4)]
                        fsd = ''
                        m = re.search(r'data-fs="([^"]+)" data-lh="([^"]+)"', b.get('html') or '')
                        if m and v['fs']:
                            fsd = f'  fs {float(v["fs"][:-2]):.2f}/{v["lh"][:-2] if v["lh"]!="normal" else "n"} vs {float(m.group(1)[:-2]):.2f}/{m.group(2)[:-2]}'
                            if abs(float(v['fs'][:-2]) - float(m.group(1)[:-2])) > 0.6: fsd += ' <<FS'
                        flag = '' if max(abs(x) for x in d) <= 4 else '  <<<'
                        print(f'      {b["type"].split()[-1][:5]} {area:<14} {v["r"]} vs {b["rect"]} d={d}{fsd}{flag}')
            await ctx.close()
        await br.close()

asyncio.run(main(sys.argv[1:] or list(PAGES)))
