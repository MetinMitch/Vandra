#!/usr/bin/env python3
"""Regenerates /home/claude/vandra/site/*.html from the computed-style extracts of
vandrastudios.com (scrape/computed/<page>-1920.json and <page>-375.json).

The markup mirrors Squarespace 7.1's fluid engine: every section is a 24-column
(desktop) / 8-column (mobile) CSS grid and every block is placed by the grid-area
measured on the live site, so sizes, spacing and the responsive behaviour follow
the original rather than an approximation.  Copy is taken verbatim from the
extracts (plus the small set of edits listed in EDITS below)."""
import html as H, json, os, re, copy

ROOT = '/home/claude/vandra'
SRC = f'{ROOT}/scrape/computed'
OUT = f'{ROOT}/site'
IMG_FILES = sorted(os.listdir(f'{OUT}/images'))

AMZ = {'river': 'https://www.amazon.com/dp/B0DVBVTSXG', 'forest': 'https://www.amazon.com/dp/B0DVBWN23Z',
       'glacier': 'https://www.amazon.com/dp/B0DVBVF3F2', 'mountain': 'https://www.amazon.com/dp/B0GDBM1G58',
       'canyon': 'https://www.amazon.com/dp/B0GDBPD36J'}
NAV = [('store.html', 'Store'), ('stories.html', 'Stories'), ('about.html', 'About'), ('contact.html', 'Contact')]

PAGES = {  # key -> (output file, <title>)
    'index': ('index.html', 'Vandra | Scandinavian outdoor'),
    'store': ('store.html', 'Store | Explore Scandinavian Style Today — Vandra'),
    'river': ('river.html', 'Vandra™ River — Vandra'),
    'forest': ('forest.html', 'Vandra™ Forest — Vandra'),
    'glacier': ('glacier.html', 'Vandra™ Glacier — Vandra'),
    'mountain': ('mountain.html', 'Vandra™ Mountain — Vandra'),
    'canyon': ('canyon.html', 'Vandra™ Canyon — Vandra'),
    'about': ('about.html', 'About | Explore with Purpose — Start Your Journey — Vandra'),
    'stories': ('stories.html', 'Stories | Discover Vandra™ adventures — Vandra'),
    'iceland': ('stories-iceland.html', "Iceland: 'Hiking Europe’s biggest active volcano' — Vandra"),
    'norway': ('stories-norway.html', "Norway: 'Finding the trolltunga' — Vandra"),
    'contact': ('contact.html', 'Contact | Get in Touch Today — Vandra'),
    'community': ('community.html', 'Newsletter — Vandra'),
    'registration': ('registration.html', 'Product registration — Vandra'),
    'terms': ('terms.html', 'Terms & conditions — Vandra'),
    'shipping': ('shipping.html', 'Shipping & return — Vandra'),
    'privacy': ('privacy.html', 'Privacy & Cookies — Vandra'),
}
HREF = {'/': 'index.html', '/store': 'store.html', '/about': 'about.html', '/contact': 'contact.html',
        '/stories': 'stories.html', '/stories/iceland': 'stories-iceland.html', '/stories/norway': 'stories-norway.html',
        '/community': 'community.html', '/registration': 'registration.html', '/terms': 'terms.html',
        '/shipping': 'shipping.html', '/privacy': 'privacy.html', 'mailto:info@vandrastudios.com?': 'mailto:info@vandrastudios.com'}
for k in AMZ:
    HREF[f'/store/p/{k}'] = f'{k}.html'
    HREF[f'/store/{k}'] = f'store.html#{k}'

# text edits applied on top of the verbatim copy
EDITS = [
    ('related to you experience', 'related to your experience'),            # typo
    ('Submit you stories', 'Submit your stories'),                           # typo
    ('A Journey in Norw with', 'A Journey in Norway with'),                  # typo
    ('receive your supplements promptly', 'receive your products promptly'),  # typo
    ('Welcome to Ekstrakt.', 'Welcome to Vandra.'),                          # typo
    ('Vandra™ 2025 | All rights reserved', 'Vandra™ 2026 | All rights reserved'),
    ('choose from our three colors', 'choose from our five colors'),
    ('The features are consistent across all three carriers, but each one comes in a unique color scheme—off-white and grey for Glacier, deep green for Forest, and soothing blue for River—so you can pick the style that resonates with you.',
     'The features are consistent across all five carriers, but each one comes in a unique color scheme—off-white and grey for Glacier, deep green for Forest, soothing blue for River, deep charcoal for Mountain, and rust red for Canyon—so you can pick the style that resonates with you.'),
]

PRODUCTS = {
    'river': dict(name='Vandra™ River', hero='blue_back_.png', slug='river',
                  gallery=['blue_back_.png', 'back_blue.jpg', 'Front_B.jpg', '45_deg_right_blue.jpg', 'profile_1_blue.jpg', '45_Degree_B.jpg'], spec='45_deg_left_back_blue.jpg',
                  long=None),
    'forest': dict(name='Vandra™ Forest', hero='Green_back.png', slug='forest',
                   gallery=['Green_back.png', 'back_reen.jpg', 'Front_G.jpg', '45_deg_right_edit_reen.jpg', 'profile_1_reen.jpg', '45_Degree_G.jpg'], spec='45_deg_left_back_Green.jpg', long=None),
    'glacier': dict(name='Vandra™ Glacier', hero='white.png', slug='glacier',
                    gallery=['white.png', 'back_White.jpg', '45_deg_back_left_White.png', 'Front_White.jpg', '45_Degree_White.jpg', 'listing_white_01.jpg'], spec='45_deg_left_back_White_.jpg', long=None),
    'mountain': dict(name='Vandra™ Mountain', hero='listing_black_01.jpg', slug='mountain', color='#2B2B2B',
                     short='Experience the stillness of high alpine evenings with the Vandra™ Mountain. Its deep charcoal tone echoes dark rock at dusk, grounding every walk in quiet confidence. Padded straps and a supportive frame keep both of you comfortable on long climbs. Understated and durable, it moves from mountain trail to city street without a second thought.',
                     long='Feel the hush of the high alpine with the Vandra™ Mountain. Its deep charcoal shade is drawn from dark rock faces at dusk, bringing a calm, grounded presence to every outing—whether you’re climbing a ridge trail or crossing town on an ordinary evening. Adjustable fastenings keep your baby snug and secure, while the padded back panel and supportive frame carry the weight evenly on long climbs. Understated and durable, it’s the perfect companion for the moments that matter, wherever the path leads.',
                     gallery=['listing_black_01.jpg', 'listing_black_02.jpg', 'listing_black_03.jpg', 'listing_black_04.jpg', 'listing_black_05.jpg', 'listing_black_10.jpg'], spec='listing_black_08.jpg'),
    'canyon': dict(name='Vandra™ Canyon', hero='listing_red_01.jpg', slug='canyon', color='#8C3B2E',
                   short='Experience the warmth of red earth with the Vandra™ Canyon. Its rust-red shade recalls sun-baked desert walls, bringing energy and ease to open-country walks or everyday errands. Breathable fabrics and cushioned straps keep you both cool and comfortable. Bold yet timeless, it brings a little desert light wherever you wander.',
                   long='Carry the warmth of red earth with the Vandra™ Canyon. Its rust-red hue is inspired by sun-baked canyon walls and desert evenings, adding a sense of energy and openness to every journey—whether you’re following a dusty trail or strolling through the neighborhood. Breathable, mesh-infused fabrics keep parent and child cool in the heat, while adjustable straps and a cushioned back panel keep the fit snug and secure for both of you. Bold yet timeless, it’s made for the wide-open moments you’ll want to remember.',
                   gallery=['listing_red_01.jpg', 'listing_red_02.jpg', 'listing_red_03.jpg', 'listing_red_04.jpg', 'listing_red_05.jpg', 'listing_red_10.jpg'], spec='listing_red_08.jpg'),
}
ORDER = ['river', 'forest', 'glacier', 'mountain', 'canyon']

# ----------------------------------------------------------------------------- helpers
def load(page, w):
    p = f'{SRC}/{page}-{w}.json'
    return json.load(open(p)) if os.path.exists(p) else None

def img_file(src):
    """map a squarespace asset name to a file in site/images (ext may differ)"""
    stem = re.sub(r'\.[a-z]+$', '', src.replace('+', '_').replace(' ', '_'), flags=re.I)
    cands = [f for f in IMG_FILES if re.sub(r'\.[a-z]+$', '', f, flags=re.I).lower() == stem.lower()]
    if not cands:
        raise SystemExit(f'missing image {src}')
    exact = [f for f in cands if f == src.replace('+', '_')]
    return 'images/' + (exact[0] if exact else cands[0])

def px(v):
    return float(re.sub(r'px$', '', v or '0') or 0)

def unit(d, m, kind):
    """turn a desktop/mobile px pair into one fluid CSS length when it fits a
    known Squarespace unit, otherwise two per-breakpoint px values"""
    d, m = round(d, 2), round(m, 2)
    if d == 0 and m == 0:
        return '0', '0'
    for u, dd, mm in (('vmax', 19.2, 8.12), ('vw', 19.2, 3.75), ('vh', 10.8, 8.12)):
        a, b = d / dd, m / mm
        if abs(a - b) < 0.02 and a > 0:
            return f'{round(a, 3):g}{u}', f'{round(a, 3):g}{u}'
    return f'{d:g}px', f'{m:g}px'

def apply_edits(s):
    for a, b in EDITS:
        s = s.replace(a, b).replace(H.escape(a, quote=False), H.escape(b, quote=False))
    return s

def clean_html(h):
    h = re.sub(r'\s(data-[\w-]+)="[^"]*"', '', h)
    h = re.sub(r'\sstyle="white-space:pre-wrap;"', '', h)
    h = h.replace('style="text-align:center;white-space:pre-wrap;"', 'data-tc="1"')
    h = re.sub(r'\sid="[^"]*"', '', h)
    h = re.sub(r'class="\s*"', '', h)
    def tc(m):
        tag = m.group(0).replace(' data-tc="1"', '')
        return re.sub(r'class="([^"]*)"', r'class="\1 tc"', tag) if 'class="' in tag else tag.replace('>', ' class="tc">', 1)
    h = re.sub(r'<[^>]*data-tc="1"[^>]*>', tc, h)
    def href(m):
        u = m.group(1)
        return f'href="{HREF.get(u, u)}"' + (' target="_blank" rel="noopener"' if u.startswith('http') else '')
    h = re.sub(r'href="([^"]*)"', href, h)
    return apply_edits(h)

def area_css(area):
    return area.replace(' ', '')

# ----------------------------------------------------------------------------- block renderers
def r_html(b):
    return f'<div class="txt">{clean_html(b["html"])}</div>'

def r_img(b, page):
    i = b['img']
    src = img_file(i['src'])
    style = f'border-radius:{i.get("wrapRadius") or "0"}'
    alt = ''
    tag = f'<div class="imgw" style="{style}"><img src="{src}" alt="{alt}" style="object-position:{i.get("pos") or "50% 50%"}" loading="lazy"></div>'
    if b.get('href'):
        u = b['href']
        tag = f'<a href="{HREF.get(u, u)}">{tag}</a>'
    return tag

def r_accordion(b):
    items = b['accordion']['items']
    pad = b['accordion'].get('btnPad') or '30px 0px'
    out = [f'<ul class="acc" style="--apad:{pad}">']
    for n, it in enumerate(items):
        ans = clean_html(it['a'])
        ans = re.sub(r'<p[^>]*>\s*</p>', '', ans)
        out.append(f'<li class="acc-item"><h4 class="acc-h"><button class="acc-btn" aria-expanded="false" aria-controls="acc-{b["id"][-6:]}-{n}"><span class="acc-title">{H.escape(it["q"])}</span><span class="plus" aria-hidden="true"><i class="plus-h"></i><i class="plus-v"></i></span></button></h4>'
                   f'<div class="acc-panel" id="acc-{b["id"][-6:]}-{n}" hidden><div class="acc-desc">{ans}</div></div></li>')
    out.append('</ul>')
    return ''.join(out)

FORM_ENDPOINT = 'https://formspree.io/f/xkjjrqvg'

def r_newsletter(b):
    n = b['newsletter']
    return (f'<div class="nl"><h3 class="nl-title">{H.escape(n["title"])}</h3><p class="nl-desc">{H.escape(n["desc"])}</p>'
            f'<form class="nl-form" action="{FORM_ENDPOINT}" method="post" data-form="newsletter"><input type="hidden" name="_subject" value="Vandra website — newsletter signup">'
            f'<label class="sr" for="nl-{b["id"][-6:]}">Email Address</label><input id="nl-{b["id"][-6:]}" class="nl-in" type="email" name="email" placeholder="Email Address" required>'
            f'<button class="nl-btn" type="submit">{H.escape((n["btn"]["text"] if isinstance(n["btn"], dict) else n["btn"]).strip())}</button></form></div>')

def r_form(b, page):
    f = b['form']
    fname = {'/contact': 'contact', '/registration': 'registration', '/community': 'community'}.get(page, 'form')
    out = [f'<form class="sqf" action="{FORM_ENDPOINT}" method="post" data-form="{fname}" novalidate="false">'
           f'<input type="hidden" name="_subject" value="Vandra website — {fname} form"><input type="hidden" name="_gotcha" style="display:none">']
    n = 0
    for fl in f['fields']:
        cls = fl['cls']; label = (fl.get('label') or '').replace('\n', ' ')
        req = 'required' in cls or '(required)' in label
        n += 1
        if 'name' in cls.split():
            out.append(f'<fieldset class="fi fi-name"><legend class="fl">{H.escape(label)}</legend><div class="fi-cols">'
                       + ''.join(f'<div class="fi-col"><label class="fcap" for="f{n}{i["name"]}">{H.escape(i["cap"].replace(chr(10)," "))}</label><input id="f{n}{i["name"]}" class="fin" type="text" name="{i["name"].lower().replace("-","_")}" {"required" if "required" in i["cap"] else ""}></div>' for i in fl['inputs'])
                       + '</div></fieldset>')
        elif 'address' in cls.split():
            caps = [i['cap'] for i in fl['inputs'] if i['tag'] == 'INPUT']
            col = lambda k, c, extra='': f'<div class="fi-col"><label class="fcap" for="f{n}a{k}">{H.escape(c.replace(chr(10)," "))}</label><input id="f{n}a{k}" class="fin" type="text" name="{['address_line_1','address_line_2','city','state','zip'][k]}"{" required" if "required" in c else ""}{extra}></div>'
            out.append(f'<fieldset class="fi fi-addr"><legend class="fl">{H.escape(label)}</legend>'
                       f'<div class="fi-col"><label class="fcap" for="f{n}c">Country</label><select id="f{n}c" class="fin fsel fsel-locked" name="address_country" disabled><option selected>United States</option></select><input type="hidden" name="address_country" value="United States"></div>'
                       + ''.join(col(k, c) for k, c in enumerate(caps[:2]))
                       + '<div class="fi-cols3">' + ''.join(col(k + 2, c) for k, c in enumerate(caps[2:5])) + '</div></fieldset>')
        elif 'phone' in cls.split():
            out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label><input id="f{n}" class="fin" type="tel" name="phone"><label class="fcap" for="f{n}">&nbsp;</label></div>')
        elif 'select' in cls.split():
            opts = fl['inputs'][0]['opts']
            if 'Color' in label:
                opts = opts + ['Mountain', 'Canyon']
            fieldname = re.sub(r'[^a-z]+', '_', label.lower().replace('(required)', '')).strip('_') or f'f{n}'
            if label.startswith('Country'):
                out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label><div class="fselw"><select id="f{n}" class="fin fsel" name="{fieldname}" required><option selected>United States</option></select></div></div>')
            else:
                out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label><div class="fselw"><select id="f{n}" class="fin fsel" name="{fieldname}" {"required" if req else ""}>' + ''.join(f'<option{" value=\"\"" if o.startswith("Select") else ""}>{H.escape(o)}</option>' for o in opts) + '</select></div></div>')
        elif 'textarea' in cls.split():
            fieldname = re.sub(r'[^a-z]+', '_', label.lower().replace('(required)', '')).strip('_') or f'f{n}'
            out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label><textarea id="f{n}" class="fin fta" name="{fieldname}" {"required" if req else ""}></textarea></div>')
        elif 'file' in cls.split():
            out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label><p class="fdesc">Maximum 5 files (PDF, PNG, JPG, HEIC, MOV or MP4)</p><label class="fdrop"><input id="f{n}" class="ffile" type="file" name="f{n}" multiple accept="image/*,video/mp4,.pdf,.heic,.mov"><span class="fdrop-ico" aria-hidden="true"></span><span class="fdrop-txt">Add a File</span></label></div>')
        else:
            typ = 'email' if 'email' in cls.split() else 'text'
            ph = fl['inputs'][0].get('ph') or ''
            desc = '<p class="fdesc">Share your content via link (Wetransfer, Dropbox, OneDrive or Google Drive)</p>' if label.startswith('Share content') else ''
            opt = f'<label class="fopt"><input type="checkbox" name="newsletter" value="Sign up for news and updates"> <span>Sign up for news and updates</span></label>' if any(i['type'] == 'checkbox' for i in fl['inputs']) else ''
            fieldname = re.sub(r'[^a-z]+', '_', label.lower().replace('(required)', '')).strip('_') or f'f{n}'
            if typ == 'email': fieldname = 'email'
            out.append(f'<div class="fi"><label class="fl" for="f{n}">{H.escape(label)}</label>{desc}<input id="f{n}" class="fin" type="{typ}" name="{fieldname}" placeholder="{H.escape(ph)}" {"required" if req else ""}>{opt}</div>')
    out.append(f'<div class="fsub"><button class="fbtn" type="submit">{H.escape(f["btn"]["text"])}</button></div></form>')
    return ''.join(out)

def r_video(b, page, n):
    thumb = ''
    m = re.search(r'alexandriaUrl&quot;:&quot;([^&]+)\{variant\}', b.get('raw') or '')
    if m:
        thumb = m.group(1) + 'thumbnail'
    return f'<div class="vid"><video src="videos/{page}-{n}.mp4" poster="{thumb}" muted autoplay loop playsinline></video></div>'

def render_block(b, mb, page, vidn):
    t = b['type'].split()[-1]
    if t == 'code-block' or (t == 'html-block' and not b.get('html')):
        return ''
    if t == 'html-block':
        inner = r_html(b)
    elif t == 'image-block':
        inner = r_img(b, page)
    elif t == 'accordion-block' or b.get('accordion'):
        inner = r_accordion(b)
    elif t == 'newsletter-block' or b.get('newsletter'):
        inner = r_newsletter(b)
    elif t == 'form-block' or b.get('form'):
        inner = r_form(b, page)
    elif t == 'video-block':
        vidn[0] += 1
        inner = r_video(b, page, vidn[0])
    else:
        return ''
    darea = area_css(b['area'])
    marea = area_css(mb['area']) if mb else darea
    style = f'--d:{darea};--m:{marea};--jc:{b.get("jc") or "flex-start"};--jcm:{(mb or b).get("jc") or "flex-start"};z-index:{b.get("z") or 1}'
    return f'<div class="fe{" fe-nl" if t == "newsletter-block" else ""}{" fe-img" if t == "image-block" else ""}" style="{style}">{inner}</div>'

# ----------------------------------------------------------------------------- sections
def section_open(s, ms, first, page, extra_cls=''):
    theme = s['theme'] or 'white-bold'
    cls = ['sec', 't-' + theme]
    if 'has-background' in s['cls']:
        cls.append('has-bg')
    if 'vertical-alignment--top' in s['cls']:
        cls.append('va-top')
    if extra_cls:
        cls.append(extra_cls)
    ms = ms or s
    mh_d, mh_m = unit(px(s['minHeight']), px(ms['minHeight']), 'mh')
    pt_d, pt_m = unit(px(s['cwPad'][0]), px(ms['cwPad'][0]), 'pad')
    pb_d, pb_m = unit(px(s['cwPad'][1]), px(ms['cwPad'][1]), 'pad')
    spt_d = px(s['padTop']); spt_m = px(ms['padTop'])
    if abs(spt_d - 115.98) < 1 and abs(spt_m - 82) < 1:
        spt = 'var(--hh)'; sptm = 'var(--hh)'
    else:
        spt, sptm = unit(spt_d, spt_m, 'pad')
    style = f'--mh:{mh_d};--mhm:{mh_m};--pt:{pt_d};--ptm:{pt_m};--pb:{pb_d};--pbm:{pb_m};--spt:{spt};--sptm:{sptm}'
    bg = ''
    if s.get('bg'):
        bg = f'<div class="sec-bg"><img src="{img_file(s["bg"]["src"])}" alt="" style="object-position:{s["bg"]["pos"]}"><div class="sec-ov" style="opacity:{(s.get("overlay") or {}).get("op", s.get("overlay")) if isinstance(s.get("overlay"), (dict, type(None))) else s["overlay"]}"></div></div>'
    return f'<section class="{" ".join(cls)}" style="{style}" id="s-{s["id"][-6:]}">{bg}<div class="cw">', '</div></section>'

def render_fluid(s, ms, first, page, vidn):
    o, c = section_open(s, ms, first, page)
    gap_d = px(s.get('gap')); gap_m = px((ms or s).get('gap'))
    rows_d = s.get('rows') or 1; rows_m = (ms or s).get('rows') or rows_d
    mblocks = {b['id']: b for b in (ms or s)['blocks']}
    if ms and ms is not s and [b['id'] for b in ms['blocks']] != [b['id'] for b in s['blocks']]:
        # block ids differ (cloned page): pair by order
        mblocks = {b['id']: mb for b, mb in zip(s['blocks'], ms['blocks'])}
    blocks = ''.join(render_block(b, mblocks.get(b['id']), page, vidn) for b in s['blocks'])
    grid = f'<div class="fg" style="--gap:{gap_d:g}px;--gapm:{gap_m:g}px;--rows:{rows_d};--rowsm:{rows_m}">{blocks}</div>'
    return o + grid + c

# --- non-fluid sections -------------------------------------------------------
TESTIMONIALS = [
    ('"Took the Glacier out for a 3-day trip through icy valleys in northern Sweden. The padding kept our little one warm the whole time, and the off-white tone actually made us more visible in low light. Easy to clean, easy to trust — exactly what we needed in freezing weather."', 'Elias R., Kiruna'),
    ('"The Forest bag handled rain, mud, and uneven forest trails without fuss. I love how grounded and quiet the design feels — it doesn’t scream ‘baby gear’ but still does the job incredibly well. Bonus points for the snug fit and quiet zippers."', 'Line M., Oslo'),
    ('"Used the River bag on a weekend canoe trip. We got splashed plenty, but everything inside stayed dry. It’s lightweight, structured just enough, and blends beautifully into the scenery. My favorite part? No rustling noises when walking through still places."', 'Jonas V., Åre'),
]

def render_testimonials(s, ms):
    items = ''.join(f'<li class="tl-item"><h3 class="tl-q">{H.escape(q)}</h3><div class="tl-n"><p>{H.escape(n)}</p></div></li>' for q, n in TESTIMONIALS)
    return (f'<section class="sec t-white sec-list" id="s-{s["id"][-6:]}"><div class="tl"><div class="tl-title"><p>Hear what our customers has to say:</p></div>'
            f'<ul class="tl-grid">{items}</ul></div></section>')

def render_store_list(s, ms):
    crumbs = '<li class="pl-crumb"><a href="store.html#all" class="pl-cat on" data-cat="all">All</a><span class="pl-sep">|</span></li>' + ''.join(
        f'<li class="pl-crumb"><a href="store.html#{k}" class="pl-cat" data-cat="{k}">{PRODUCTS[k]["name"].split()[-1]}</a><span class="pl-sep">|</span></li>' for k in ORDER)
    items = ''.join(
        f'<div class="pl-item" data-cat="{k}"><a class="pl-link" href="{k}.html"><figure class="pl-fig"><img class="pl-img" src="images/{PRODUCTS[k]["hero"]}" alt="{PRODUCTS[k]["name"]}"><img class="pl-img pl-hover" src="images/{PRODUCTS[k]["gallery"][1]}" alt=""></figure>'
        f'<div class="pl-meta"><div class="pl-title">{PRODUCTS[k]["name"]}</div><div class="pl-price">$219.00</div></div></a></div>' for k in ORDER)
    return (f'<section class="sec t-white-bold sec-pl" id="s-{s["id"][-6:]}"><div class="pl"><h2 class="pl-mtitle">Store</h2>'
            f'<nav class="pl-nav"><ul class="pl-crumbs">{crumbs}</ul></nav><div class="pl-grid">{items}</div></div></section>')

def render_product_detail(key):
    p = PRODUCTS[key]
    slides = ''.join(f'<div class="pg-slide{" on" if i == 0 else ""}"><img src="images/{g}" alt="{p["name"]} – image {i+1} of {len(p["gallery"])}" loading="{"eager" if i == 0 else "lazy"}"></div>' for i, g in enumerate(p['gallery']))
    desc = p['long']
    return (f'<section class="sec t-white-bold sec-pd" id="s-pd" style="--spt:var(--hh);--sptm:var(--hh)"><div class="pd"><div class="pd-wrap">'
            f'<div class="pg"><div class="pg-slides">{slides}</div>'
            f'<div class="pg-ctl"><button class="pg-prev" type="button" aria-label="Previous image"></button><button class="pg-next" type="button" aria-label="Next image"></button></div><div class="pg-ind">1 / {len(p["gallery"])}</div></div>'
            f'<div class="pd-meta"><h1 class="pd-title">{p["name"]}</h1><div class="pd-price">$219.00</div><div class="pd-desc"><p>{H.escape(desc)}</p></div>'
            f'<div class="pd-cart"><a class="pd-buy" href="{AMZ[key]}" target="_blank" rel="noopener">Buy now</a></div></div>'
            f'</div></div></section>')

SPECS = None  # filled from river extract

def render_specs(key, s, ms):
    p = PRODUCTS[key]
    acc_b = SPECS
    return (f'<section class="sec t-white-bold sec-specs" id="s-specs"><div class="sl"><div class="sl-row">'
            f'<div class="sl-col"><div class="sl-img"><img src="images/{p["spec"]}" alt="{p["name"]}" loading="lazy"></div></div>'
            f'<div class="sl-col"><div class="sl-spacers"></div><div class="sl-h"><h2>Specifications</h2></div><div class="sl-acc">{r_accordion(acc_b)}</div></div>'
            f'</div></div></section>')

def render_stories_grid(s, ms):
    items = (('stories-iceland.html', 'DJI_0263.JPG', "Iceland: 'Hiking Europe’s biggest active volcano'"),
             ('stories-norway.html', '20250324_142713046_iOS.jpg', "Norway: 'Finding the trolltunga'"))
    g = ''.join(f'<a class="sg-item" href="{h}"><div class="sg-img"><img src="images/{i}" alt="{H.escape(t)}" loading="lazy"></div><div class="sg-text"><h3 class="sg-title">{H.escape(t)}</h3></div></a>' for h, i, t in items)
    return f'<section class="sec t-white-bold sec-sg" id="s-{s["id"][-6:]}"><div class="sg">{g}</div></section>'

# ----------------------------------------------------------------------------- page assembly
def header(key, theme):
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == PAGES[key][0] else ""}>{t}</a>' for h, t in NAV)
    return f'''<header class="hdr t-{theme}" id="header">
<div class="hdr-d"><a class="hdr-logo" href="index.html" aria-label="Vandra"><img src="images/Vandra_logo.png" alt="Vandra"></a><nav class="hdr-nav">{nav}</nav></div>
<div class="hdr-m"><button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="mmenu"><span class="bun"></span><span class="bun"></span></button><a class="hdr-mlogo" href="index.html" aria-label="Vandra"><img src="images/Vandra_logo.png" alt="Vandra"></a></div>
</header>
<div class="mmenu" id="mmenu" hidden><nav class="mmenu-nav">{nav}</nav></div>'''

def page_html(key, body, theme):
    f, title = PAGES[key]
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="images/Vandra_logo.png">
</head>
<body class="p-{key}">
{header(key, theme)}
<main id="sections">
{body}
</main>
<script src="main.js"></script>
</body>
</html>
'''

def build_page(key, src_key=None, product=None):
    src_key = src_key or key
    d = load(src_key, 1920); m = load(src_key, 375)
    if m is None and product:  # forest/glacier have no mobile extract: reuse river's (same layout)
        m = load('river', 375)
    msecs = {s['id']: s for s in (m or d)['sections']}
    if m and [s['id'] for s in m['sections']] != [s['id'] for s in d['sections']]:
        msecs = {s['id']: ms for s, ms in zip(d['sections'], m['sections'])}
    body = []
    vidn = [0]
    first = True
    for s in d['sections']:
        ms = msecs.get(s['id'])
        if s['kind'] == 'fluid':
            if key == 'index' and s['id'] == '6722614483a465349885d461':
                s, ms = extend_products(s, ms)
            body.append(render_fluid(s, ms, first, key, vidn))
        else:
            if key == 'index':
                body.append(render_testimonials(s, ms))
            elif key == 'store':
                body.append(render_store_list(s, ms))
            elif key == 'stories':
                body.append(render_stories_grid(s, ms))
            elif product:
                if 'product-detail' in s['cls']:
                    body.append(render_product_detail(product))
                elif 'layout-engine' in s['cls'] and 'full-bleed' not in s['cls'].split('layout-engine')[0]:
                    body.append(render_specs(product, s, ms))
        first = False
    if key in ('iceland', 'norway'):
        nxt = key == 'iceland'
        other = 'stories-norway.html' if nxt else 'stories-iceland.html'
        title = "Norway: 'Finding the trolltunga'" if nxt else "Iceland: 'Hiking Europe’s biggest active volcano'"
        caret = '<svg class="ip-caret" viewBox="0 0 9 16" aria-hidden="true"><polyline fill="none" stroke="currentColor" stroke-miterlimit="10" points="1.6,1.2 6.5,7.9 1.6,14.7"></polyline></svg>'
        fidx = next(i for i, sec in enumerate(d['sections']) if sec['inFooter'])
        body.insert(fidx, f'<section class="ip t-bright-inverse" id="itemPagination"><a class="ip-link {"ip-next" if nxt else "ip-prev"}" href="{other}">'
                    + ('' if nxt else caret) + f'<span class="sr">{"Next" if nxt else "Previous"}</span><h2 class="ip-title">{H.escape(title)}</h2>' + (caret if nxt else '') + '</a></section>')
    html = page_html(key, '\n'.join(body), d['header']['theme'] or 'white-bold')
    open(f'{OUT}/{PAGES[key][0]}', 'w').write(html)

def extend_products(s, ms):
    """homepage product row: add Mountain + Canyon below River/Forest/Glacier"""
    s = copy.deepcopy(s); ms = copy.deepcopy(ms)
    def shift(area, dr):
        r1, c1, r2, c2 = [int(x) for x in area.split('/')]
        return f'{r1+dr} / {c1} / {r2+dr} / {c2}'
    river = s['blocks'][:4]; forest = s['blocks'][4:8]
    mriver = ms['blocks'][:4]; mforest = ms['blocks'][4:8]
    def clone(blocks, key, color, dr, mobile):
        out = []
        p = PRODUCTS[key]
        for b in blocks:
            b = copy.deepcopy(b); b['id'] += '-' + key
            b['area'] = shift(b['area'], dr)
            if b.get('img'):
                b['img']['src'] = p['hero']
            elif b.get('html'):
                h = b['html']
                if '<h2' in h:
                    h = re.sub(r'(<span class="sqsrte-text-color--custom" style="color: )#[0-9A-Fa-f]+(")[^>]*>[^<]*</span>', rf'\1{color}\2>{p["name"].split()[-1]}</span>', h)
                elif '<h4' in h:
                    h = re.sub(r'/store/p/\w+', f'/store/p/{key}', h)
                else:
                    h = re.sub(r'(<span class="sqsrte-text-color--black"[^>]*>)[^<]*(</span>)', lambda mm: mm.group(1) + H.escape(p['short'], quote=False) + mm.group(2), h, count=1)
                b['html'] = h
            out.append(b)
        return out
    s['blocks'] += clone(river, 'mountain', PRODUCTS['mountain']['color'], 19, False) + clone(forest, 'canyon', PRODUCTS['canyon']['color'], 19, False)
    ms['blocks'] += clone(mriver, 'mountain', PRODUCTS['mountain']['color'], 54, True) + clone(mforest, 'canyon', PRODUCTS['canyon']['color'], 54, True)
    s['rows'] += 19; ms['rows'] += 36
    return s, ms

def main():
    global SPECS
    river = load('river', 1920)
    # specs accordion lives in a classic sqs-layout section: pull it from the cleaned html
    raw = open(f'{SRC}/river-1920-other1.html').read()
    qs = re.findall(r'accordion-item__title">(.*?)</span>', raw, re.S)
    ans = re.findall(r'accordion-item__description\s*">\s*(.*?)\s*</div>', raw, re.S)
    SPECS = {'id': 'fe-block-specs', 'accordion': {'items': [{'q': H.unescape(q.strip()), 'a': a.strip()} for q, a in zip(qs, ans)]}}
    # product descriptions from the extracts
    for k in ('river', 'forest', 'glacier'):
        r = load(k, 1920)['sections'][0]['raw']
        PRODUCTS[k]['long'] = H.unescape(re.sub(r'\s+', ' ', re.search(r'product-description hidden-down-md">\s*<p[^>]*>(.*?)</p>', r, re.S).group(1))).strip()
    for k in PAGES:
        if k in ('mountain', 'canyon'):
            build_page(k, 'river', product=k)
        elif k in ('river', 'forest', 'glacier'):
            build_page(k, k, product=k)
        else:
            build_page(k)
    print('built', len([f for f in os.listdir(OUT) if f.endswith('.html')]), 'pages')

if __name__ == '__main__':
    main()
