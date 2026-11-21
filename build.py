#!/usr/bin/env python3
"""Build the static site into ./docs (served by GitHub Pages)

    python3 build.py

Edit config.json (link, reward, domain) or content/*.json (texts), then run
this again. Everything in ./docs can be uploaded to any static host.
"""
import datetime
import html
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "docs"
CFG = json.loads((ROOT / "config.json").read_text("utf-8"))
SITE = CFG["site_url"].rstrip("/")
LANGS = CFG["languages"]
DEFAULT = CFG["default_language"]
REF = CFG["referral_url"]
TODAY = datetime.date.today()
C = {l: json.loads((ROOT / "content" / f"{l}.json").read_text("utf-8")) for l in LANGS}

MONTHS = {
    "en": "January February March April May June July August September October November December".split(),
    "si": "ජනවාරි පෙබරවාරි මාර්තු අප්‍රේල් මැයි ජූනි ජූලි අගෝස්තු සැප්තැම්බර් ඔක්තෝබර් නොවැම්බර් දෙසැම්බර්".split(),
    "ta": "ஜனவரி பிப்ரவரி மார்ச் ஏப்ரல் மே ஜூன் ஜூலை ஆகஸ்ட் செப்டம்பர் அக்டோபர் நவம்பர் டிசம்பர்".split(),
}

GOOGLE_FONTS = {
    "en": "family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700",
    "si": "family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Noto+Sans+Sinhala:wght@400;500;600;700",
    "ta": "family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700",
}


def fmt_date(lang):
    m = MONTHS.get(lang, MONTHS["en"])[TODAY.month - 1]
    if lang == "si":
        return f"{TODAY.year} {m} {TODAY.day}"
    return f"{TODAY.day} {m} {TODAY.year}"


def page_path(lang):
    return "" if lang == DEFAULT else f"{lang}/"


def abs_url(lang):
    return f"{SITE}/{page_path(lang)}"


def rel(lang, target):
    """Relative link from a language page to a site-root path."""
    prefix = "" if lang == DEFAULT else "../"
    return (prefix + target) or "./"


def esc(s):
    return html.escape(s, quote=True)


def reward(lang):
    return CFG["reward"].get(lang, CFG["reward"][DEFAULT])


def fill(lang, s):
    return (s.replace("{year}", str(TODAY.year))
             .replace("{reward}", reward(lang))
             .replace("{date}", fmt_date(lang)))


def plain(lang, s):
    return fill(lang, s).replace("{link}", REF)


def rich(lang, s):
    link = f'<a class="reflink" href="{esc(REF)}" rel="sponsored noopener">{esc(REF)}</a>'
    return esc(fill(lang, s)).replace("{link}", link)


def hl(lang, s, cls):
    """Text with the reward amount wrapped in a styled span."""
    parts = s.split("{reward}")
    return f'<span class="{cls}">{esc(reward(lang))}</span>'.join(esc(plain(lang, p)) for p in parts)


def T(lang, key):
    return esc(plain(lang, C[lang][key]))


# ---------------------------------------------------------------- graphics
def icon(name, cls="ic"):
    paths = {
        "check": '<path d="M5 12.5l4.2 4.2L19 7"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
        "home": '<path d="M3 20h18M5 20V10l7-5 7 5v10M10 20v-5h4v5"/>',
        "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>',
        "study": '<path d="M2 9l10-5 10 5-10 5-10-5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/>',
        "bed": '<path d="M3 18V8M3 14h18v4M21 18v-4a3 3 0 0 0-3-3h-7v3"/><circle cx="7" cy="11" r="1.6"/>',
        "leaf": '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19l7-7"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
    }
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{paths[name]}</svg>')


LOGO = ('<svg class="logo" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#111318"/>'
        '<ellipse cx="16" cy="16" rx="12.5" ry="4.6" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.4" transform="rotate(-24 16 16)"/>'
        '<circle cx="16" cy="16" r="4" fill="#1F4FD1"/><circle cx="26" cy="11.6" r="2.2" fill="#F2A60C"/></svg>')

HERO_ART = '''<svg class="art" viewBox="0 0 480 230" aria-hidden="true">
<path d="M-10 200 Q240 120 490 200" fill="none" stroke="#111318" stroke-opacity=".12" stroke-width="1.5"/>
<path d="M30 190 Q240 -30 460 90" fill="none" stroke="#1F4FD1" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="4 8"/>
<path d="M10 120 Q260 -10 470 30" fill="none" stroke="#1F4FD1" stroke-opacity=".22" stroke-width="1.2" stroke-dasharray="2 9"/>
<g transform="translate(352 64) rotate(-16)">
<rect x="-62" y="-14" width="44" height="28" rx="3" fill="#fff" stroke="#111318" stroke-width="2"/>
<path d="M-51 -14v28M-40 -14v28M-29 -14v28M-62 0h44" stroke="#111318" stroke-opacity=".35" stroke-width="1"/>
<rect x="18" y="-14" width="44" height="28" rx="3" fill="#fff" stroke="#111318" stroke-width="2"/>
<path d="M29 -14v28M40 -14v28M51 -14v28M18 0h44" stroke="#111318" stroke-opacity=".35" stroke-width="1"/>
<path d="M-18 0h36" stroke="#111318" stroke-width="2"/>
<rect x="-10" y="-12" width="20" height="24" rx="4" fill="#111318"/>
<circle r="3.6" fill="#F2A60C"/>
</g>
<g fill="none" stroke="#F2A60C" stroke-width="3" stroke-linecap="round">
<path d="M196 150 q14 -16 32 -19"/><path d="M206 164 q26 -30 60 -35" stroke-opacity=".7"/><path d="M216 178 q38 -44 88 -51" stroke-opacity=".45"/>
</g>
<path d="M60 230 V178 L130 140 L200 178 V230 Z" fill="#fff" stroke="#111318" stroke-width="2" stroke-linejoin="round"/>
<path d="M44 186 L130 136 L216 186" fill="none" stroke="#111318" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="112" y="190" width="36" height="40" rx="3" fill="#EEF1F8" stroke="#111318" stroke-width="2"/>
<g transform="translate(168 146)">
<path d="M10 16 L16 -4" stroke="#111318" stroke-width="3" stroke-linecap="round"/>
<g transform="rotate(-30 16 -10)"><rect x="-6" y="-24" width="44" height="28" rx="5" fill="#fff" stroke="#111318" stroke-width="2"/></g>
</g>
</svg>'''

CSS = r"""
:root{--paper:#F7F5F0;--white:#fff;--ink:#111318;--ink-2:#22262E;--body:#3A3F49;--muted:#575C66;--line:#E4E1D8;--line-2:#D6D2C7;
--accent:#1F4FD1;--accent-hover:#163A9E;--tint:#EEF1F8;--saffron:#F2A60C;--saffron-ink:#9A6400;--saffron-soft:#FCF6E6;--saffron-line:#EFDDB0;--mark:#F8D58A;--ok:#0F7B4F;
--sans:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",Arial,sans-serif;
--display:"Space Grotesk",Inter,ui-sans-serif,system-ui,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;--max:1200px;--lh:1.65;color-scheme:light}
html:lang(si){--sans:Inter,"Noto Sans Sinhala","Iskoola Pota","Sinhala Sangam MN","Nirmala UI",system-ui,sans-serif;--display:"Space Grotesk","Noto Sans Sinhala","Iskoola Pota","Nirmala UI",sans-serif;--lh:1.8}
html:lang(ta){--sans:Inter,"Noto Sans Tamil","Latha","Tamil Sangam MN","Nirmala UI",system-ui,sans-serif;--display:"Space Grotesk","Noto Sans Tamil","Latha","Nirmala UI",sans-serif;--lh:1.8}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:84px}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/var(--lh) var(--sans);overflow-x:hidden}
a{color:var(--accent)}a:hover{color:var(--accent-hover)}
svg{display:block}
h1,h2,h3{margin:0;font-family:var(--display);font-weight:700}
.wrap{max-width:var(--max);margin:0 auto;padding:0 24px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--ink);color:#fff;padding:8px 12px;border-radius:8px;z-index:100}
.skip:focus{left:8px}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px;border-radius:6px}
/* header */
.top{position:sticky;top:0;z-index:40;background:rgba(247,245,240,.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:68px}
.brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;min-width:0}
.brand .logo{width:32px;height:32px;flex:none}
.brand span{font-family:"Space Grotesk",var(--sans);font-weight:700;font-size:18px;letter-spacing:-.01em;white-space:nowrap}
.brand b{font-weight:500;color:var(--muted)}
.top-right{display:flex;align-items:center;gap:14px}
.langs{display:flex;gap:4px;padding:4px;border:1px solid var(--line);border-radius:999px;background:var(--white)}
.langs a{padding:6px 14px;border-radius:999px;color:var(--ink);text-decoration:none;font-size:14px;line-height:1.4;white-space:nowrap}
.langs a[aria-current]{background:var(--ink);color:#fff;font-weight:600}
.langs a:not([aria-current]):hover{background:var(--paper)}
.langs a[lang=si]{font-family:"Noto Sans Sinhala","Iskoola Pota","Nirmala UI",var(--sans)}
.langs a[lang=ta]{font-family:"Noto Sans Tamil","Latha","Nirmala UI",var(--sans)}
.hcta{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:12px;background:var(--ink);color:#fff;text-decoration:none;font-weight:600;font-size:15px;white-space:nowrap}
.hcta:hover{background:#000;color:#fff}
.suggest{background:var(--tint);border-bottom:1px solid #C9D3F2;font-size:15px}
.suggest .wrap{display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}
.suggest a{font-weight:600}
.suggest button{background:var(--white);border:1px solid var(--line);color:var(--body);border-radius:999px;padding:4px 12px;cursor:pointer;font:inherit;font-size:13px;min-height:32px}
/* hero */
.hero .wrap{display:flex;flex-wrap:wrap;gap:56px;align-items:center;padding-top:72px;padding-bottom:56px}
.hero-copy{flex:1 1 520px;min-width:0}
.hero-side{flex:1 1 420px;min-width:0}
.chip{display:inline-flex;align-items:center;gap:8px;margin:0 0 22px;padding:5px 12px;border-radius:999px;background:var(--white);border:1px solid var(--line);font-size:14px;color:var(--muted)}
.chip i{width:8px;height:8px;border-radius:50%;background:var(--ok)}
.hero h1{margin:0 0 22px;letter-spacing:-.035em;line-height:1.02}
.hero h1 .kick{display:block;font-size:22px;letter-spacing:0;font-weight:600;color:var(--accent);margin-bottom:14px;line-height:1.35}
.hero h1 .big{display:block;font-size:clamp(42px,6.2vw,76px)}
html:lang(si) .hero h1 .big,html:lang(ta) .hero h1 .big{font-size:clamp(32px,4.6vw,56px);letter-spacing:-.01em;line-height:1.22}
.mk{white-space:nowrap;box-shadow:inset 0 -.26em 0 var(--mark);font-family:"Space Grotesk",var(--display)}
.lead{margin:0 0 30px;font-size:19px;color:var(--body);max-width:34em}
.ctas{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:22px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:12px;min-height:56px;padding:10px 26px;border-radius:14px;text-decoration:none;font-weight:700;font-size:18px;line-height:1.35;transition:background .15s,transform .15s}
.btn .ic{width:20px;height:20px;flex:none}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent-hover);color:#fff;transform:translateY(-1px)}
.btn-ghost{background:var(--white);color:var(--ink);border:1px solid var(--line-2);font-weight:600;font-size:17px}
.btn-ghost:hover{color:var(--ink);background:#fff;border-color:var(--ink)}
.btn-ink{background:var(--ink);color:#fff;font-size:16px;min-height:48px;padding:10px 20px;border-radius:12px;font-weight:600}
.btn-ink:hover{background:#000;color:#fff}
.btn-saffron{background:var(--saffron);color:var(--ink)}
.btn-saffron:hover{background:#FFB938;color:var(--ink)}
[dir=rtl] .btn .ic{transform:scaleX(-1)}
.trust{list-style:none;margin:0 0 30px;padding:0;display:flex;flex-wrap:wrap;gap:10px 22px;font-size:15px;color:var(--body)}
.trust li{display:flex;align-items:center;gap:8px}
.trust .ic{width:18px;height:18px;color:var(--ok);flex:none}
.copy{background:var(--white);border:1px solid var(--line);border-radius:16px;padding:14px 16px;max-width:560px}
.copy label{display:block;font-size:14px;color:var(--muted);margin-bottom:8px}
.copy .row{display:flex;gap:10px;flex-wrap:wrap}
.copy input{flex:1 1 260px;min-width:0;min-height:44px;padding:0 12px;border:1px solid var(--line);border-radius:10px;background:var(--paper);font:500 13px var(--mono);color:var(--body)}
.copy button{min-height:44px;padding:0 18px;border-radius:10px;border:1px solid var(--ink);background:var(--ink);color:#fff;font:600 15px var(--sans);cursor:pointer}
.copy button.ok{background:var(--ok);border-color:var(--ok)}
.disclose{margin:14px 0 0;font-size:13.5px;color:var(--muted);max-width:40em}
.ticket{background:var(--white);border:1px solid var(--line);border-radius:28px;overflow:hidden;box-shadow:0 30px 60px -36px rgba(17,19,24,.35)}
.ticket .art-wrap{background:var(--tint);padding:18px 18px 0}
.ticket .art{width:100%;height:auto}
.halves{display:flex;align-items:stretch}
.half{flex:1 1 0;padding:26px 18px 24px;text-align:center;min-width:0}
.half .lbl{margin:0 0 4px;font-size:14px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.half .amt{margin:0;font-family:"Space Grotesk",var(--display);font-size:clamp(28px,3.2vw,40px);font-weight:700;letter-spacing:-.02em;line-height:1.1}
.half .sub{margin:6px 0 0;font-size:14px;color:var(--muted);line-height:1.45}
.perf{width:0;border-left:2px dashed var(--line-2);margin:18px 0}
.tnote{margin:0;padding:14px 22px;border-top:1px solid var(--line);background:var(--saffron-soft);font-size:14px;color:var(--body);display:flex;align-items:center;gap:10px;line-height:1.5}
.tnote .ic{width:18px;height:18px;color:var(--saffron-ink);flex:none}
/* sections */
.sec{padding:80px 0 0}
.kicker{margin:0 0 10px;font-size:15px;font-weight:600;color:var(--accent)}
.h2{font-size:clamp(30px,3.6vw,44px);line-height:1.1;letter-spacing:-.025em;margin:0 0 12px;max-width:20em}
html:lang(si) .h2,html:lang(ta) .h2{font-size:clamp(25px,3vw,36px);line-height:1.35;letter-spacing:0}
.intro{margin:0 0 36px;font-size:18px;color:var(--muted);max-width:44em}
.quick{display:flex;flex-wrap:wrap;gap:12px 40px;background:var(--white);border:1px solid var(--line);border-radius:20px;padding:26px 28px}
.quick h2{flex:0 0 180px;font-size:15px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);line-height:1.6}
html:lang(si) .quick h2,html:lang(ta) .quick h2{letter-spacing:.02em}
.quick p{flex:1 1 520px;margin:0;color:var(--ink-2);min-width:0}
.reflink{overflow-wrap:anywhere;font-weight:600}
.band{background:var(--white);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:72px}
.band .wrap{padding-top:80px;padding-bottom:80px}
.band .h2{margin-bottom:44px}
ol.steps{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:28px}
ol.steps li{flex:1 1 190px;min-width:0;border-top:2px solid var(--ink);padding-top:18px}
ol.steps li:last-child{border-top-color:var(--saffron)}
ol.steps .num{margin:0 0 12px;font-family:"Space Grotesk",var(--display);font-size:34px;font-weight:700;color:var(--accent);line-height:1}
ol.steps li:last-child .num{color:var(--saffron-ink)}
ol.steps h3,.tips h3,.uses h3{font-size:18px;line-height:1.4;margin:0 0 6px;font-family:var(--sans);font-weight:650}
ol.steps p,.tips p,.uses p{margin:0;font-size:15.5px;color:var(--muted)}
.duo{display:flex;flex-wrap:wrap;gap:20px}
.panel{flex:1 1 440px;min-width:0;border-radius:24px;padding:32px}
.panel.light{background:var(--white);border:1px solid var(--line)}
.panel.dark{background:var(--ink);color:#fff}
.panel .lbl{margin:0 0 4px;font-size:15px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.panel.dark .lbl{color:#A4A9B4}
.panel .amt{margin:0 0 22px;font-family:"Space Grotesk",var(--display);font-size:clamp(36px,4vw,48px);font-weight:700;letter-spacing:-.02em;line-height:1.1}
.panel.dark .amt{color:var(--saffron)}
ul.ticks{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:14px;color:var(--body)}
.panel.dark ul.ticks{color:#D9DCE3}
ul.ticks li{display:flex;gap:12px}
ul.ticks .ic{width:22px;height:22px;flex:none;margin-top:2px;color:var(--ok)}
.panel.dark ul.ticks .ic{color:var(--saffron)}
.panel.dark .reflink{color:#9DB6FF}
.tips{display:flex;flex-wrap:wrap;gap:36px 40px}
.tips > div{flex:1 1 300px;min-width:0;border-top:1px solid var(--line-2);padding-top:20px}
.chips{list-style:none;margin:-18px 0 36px;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.chips li{padding:6px 14px;border-radius:999px;background:var(--white);border:1px solid var(--line);font-size:14px}
.uses{display:flex;flex-wrap:wrap;gap:16px}
.uses > div{flex:1 1 320px;min-width:0;display:flex;gap:16px;background:var(--white);border:1px solid var(--line);border-radius:18px;padding:22px}
.uses .tile{flex:none;width:44px;height:44px;border-radius:12px;background:var(--tint);display:flex;align-items:center;justify-content:center;color:var(--accent)}
.uses .tile .ic{width:24px;height:24px}
.uses h3{font-size:17px;margin-bottom:4px}
.uses p{font-size:15px}
.rules{display:flex;flex-wrap:wrap;gap:20px 32px;background:var(--saffron-soft);border:1px solid var(--saffron-line);border-radius:24px;padding:32px}
.rules > .ic{width:40px;height:40px;color:var(--saffron-ink);flex:none}
.rules > div{flex:1 1 520px;min-width:0}
.rules h2{font-size:28px;letter-spacing:-.015em;margin-bottom:14px}
.rules ul{margin:0;padding-inline-start:20px;display:flex;flex-direction:column;gap:8px;color:var(--body)}
.faq{display:flex;flex-wrap:wrap;gap:40px 64px}
.faq-side{flex:1 1 320px;min-width:0}
.faq-side p{margin:0 0 24px;color:var(--muted)}
.faq-list{flex:2 1 560px;min-width:0;display:flex;flex-direction:column;gap:10px}
.faq details{background:var(--white);border:1px solid var(--line);border-radius:16px}
.faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;padding:18px 20px;font-weight:600;font-size:17px;line-height:1.5}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";flex:none;font-size:24px;line-height:1;color:var(--muted);transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{margin:0;padding:0 20px 20px;color:var(--body)}
.final{margin:88px auto 0;background:var(--ink);color:#fff;border-radius:32px;padding:64px 32px;text-align:center}
.final h2{font-size:clamp(34px,4.4vw,52px);line-height:1.12;letter-spacing:-.03em;margin:0 0 16px}
html:lang(si) .final h2,html:lang(ta) .final h2{font-size:clamp(28px,3.6vw,42px);letter-spacing:0;line-height:1.35}
.final h2 span.line{display:block}
.sf{white-space:nowrap;color:var(--saffron);font-family:"Space Grotesk",var(--display)}
.final p{margin:0 auto 30px;max-width:34em;color:#C9CDD6;font-size:18px}
.final .small{margin:18px auto 0;font-size:14px;color:#A4A9B4}
footer{border-top:1px solid var(--line);margin-top:88px}
footer .wrap{padding-top:36px;padding-bottom:120px;display:flex;flex-direction:column;gap:14px;font-size:14px;color:var(--muted)}
footer nav{display:flex;gap:18px;flex-wrap:wrap}
footer nav a{color:var(--ink)}
footer p{margin:0;max-width:62em}
.mbar{position:fixed;left:0;right:0;bottom:0;z-index:50;padding:10px 16px calc(14px + env(safe-area-inset-bottom));background:rgba(247,245,240,.96);border-top:1px solid var(--line);transform:translateY(110%);transition:transform .25s ease;display:none}
.mbar.show{transform:none}
.mbar a{display:flex;align-items:center;justify-content:center;gap:8px;min-height:52px;border-radius:14px;background:var(--ink);color:#fff;text-decoration:none;font-weight:700;font-size:16px;text-align:center;padding:6px 14px;line-height:1.35}
@media (max-width:860px){.hcta{display:none}}
@media (max-width:720px){
 body{font-size:16px}
 .wrap{padding:0 16px}
 .top .wrap{min-height:60px}
 .brand span{display:none}
 .langs a{padding:5px 10px;font-size:13.5px}
 .hero .wrap{padding-top:32px;padding-bottom:24px;gap:28px}
 .hero h1 .kick{font-size:17px}
 .lead{font-size:16.5px}
 .btn{width:100%;justify-content:space-between;font-size:17px}
 .ctas .btn-ghost{display:none}
 .trust{flex-direction:column;gap:6px}
 .sec{padding-top:56px}
 .band{margin-top:56px}.band .wrap{padding-top:56px;padding-bottom:56px}
 .quick,.panel,.rules{padding:22px}
 .quick h2{flex-basis:100%}
 .final{padding:44px 20px;border-radius:24px}
 .final .btn{justify-content:center}
 .mbar{display:block}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

JS = r"""
(function(){
var d=document;
d.querySelectorAll('[data-copy]').forEach(function(b){
 b.addEventListener('click',function(){
  var v=b.getAttribute('data-copy');
  function done(){var o=b.textContent;b.textContent=b.getAttribute('data-copied');b.classList.add('ok');setTimeout(function(){b.textContent=o;b.classList.remove('ok')},1800)}
  function fb(){var t=d.getElementById('reflink');if(t){t.select();try{d.execCommand('copy');done()}catch(e){}}}
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(v).then(done,fb)}else{fb()}
 });
});
var cta=d.getElementById('hero-cta'),bar=d.getElementById('mbar');
if(cta&&bar&&'IntersectionObserver' in window){new IntersectionObserver(function(e){bar.classList.toggle('show',!e[0].isIntersecting)}).observe(cta)}
var S=__SUGGEST__,cur=d.documentElement.lang,box=d.getElementById('suggest');
try{if(localStorage.getItem('langHint'))return}catch(e){}
var prefs=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']);
for(var i=0;i<prefs.length;i++){
 var p=String(prefs[i]||'').toLowerCase().split('-')[0];
 if(p===cur)return;
 if(S[p]){
  var s=S[p],a=box.querySelector('a'),btn=box.querySelector('button');
  box.querySelector('[data-t]').textContent=s.text;a.textContent=s.go;a.href=s.href;a.lang=p;a.hreflang=p;btn.textContent=s.close;btn.lang=p;box.hidden=false;
  btn.onclick=function(){box.hidden=true;try{localStorage.setItem('langHint','1')}catch(e){}};
  return;
 }
}
})();
"""

WHO_ICONS = ["home", "laptop", "study", "bed", "leaf", "shield"]


def json_ld(lang):
    c = C[lang]
    url = abs_url(lang)
    graph = [
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": CFG["site_name"],
         "inLanguage": [C[l]["hreflang"] for l in LANGS]},
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": plain(lang, c["title"]),
         "description": plain(lang, c["description"]), "inLanguage": c["hreflang"],
         "isPartOf": {"@id": f"{SITE}/#website"}, "dateModified": TODAY.isoformat(),
         "primaryImageOfPage": {"@type": "ImageObject", "url": f"{SITE}/og/{lang}.png", "width": 1200, "height": 630},
         "about": {"@type": "Thing", "name": "Starlink referral program"},
         "spatialCoverage": {"@type": "Country", "name": "Sri Lanka", "identifier": "LK"},
         "significantLink": [REF],
         "mainEntity": {"@id": f"{url}#faq"}},
        {"@type": "FAQPage", "@id": f"{url}#faq", "inLanguage": c["hreflang"],
         "mainEntity": [{"@type": "Question", "name": plain(lang, f["q"]),
                         "acceptedAnswer": {"@type": "Answer", "text": plain(lang, f["a"])}} for f in c["faq"]]},
        {"@type": "HowTo", "@id": f"{url}#howto", "name": plain(lang, c["steps_h2"]), "inLanguage": c["hreflang"],
         "step": [{"@type": "HowToStep", "position": i + 1, "name": plain(lang, s["t"]), "text": plain(lang, s["d"]),
                   "url": f"{url}#how"} for i, s in enumerate(c["steps"])]},
    ]
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return data.replace("</", "<\\/")


def head(lang):
    c = C[lang]
    url = abs_url(lang)
    alts = "\n".join(f'<link rel="alternate" hreflang="{C[l]["hreflang"]}" href="{abs_url(l)}">' for l in LANGS)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{abs_url(DEFAULT)}">'
    og_alts = "\n".join(f'<meta property="og:locale:alternate" content="{C[l]["og_locale"]}">' for l in LANGS if l != lang)
    title, desc = T(lang, "title"), T(lang, "description")
    og_img = f"{SITE}/og/{lang}.png"
    fonts = GOOGLE_FONTS.get(lang, GOOGLE_FONTS["en"])
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{alts}
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="theme-color" content="#F7F5F0">
<meta name="geo.region" content="LK">
<meta name="geo.placename" content="Sri Lanka">
<link rel="icon" href="{rel(lang, 'favicon.svg')}" type="image/svg+xml">
<link rel="icon" href="{rel(lang, 'icon-192.png')}" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{rel(lang, 'apple-touch-icon.png')}">
<link rel="alternate" type="text/plain" title="LLM summary" href="{SITE}/llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&amp;display=swap">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(CFG['site_name'])}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{T(lang, 'og_text')}">
<meta property="og:locale" content="{c['og_locale']}">
{og_alts}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<script type="application/ld+json">
{json_ld(lang)}
</script>
<style>{CSS}</style>"""


def lang_switch(lang):
    out = []
    for l in LANGS:
        cur = ' aria-current="page"' if l == lang else ""
        out.append(f'<a href="{rel(lang, page_path(l))}" hreflang="{C[l]["hreflang"]}" lang="{C[l]["hreflang"]}"{cur}>{esc(C[l]["name"])}</a>')
    return "".join(out)


def ref_a(cls, inner, extra=""):
    return f'<a class="{cls}"{extra} href="{esc(REF)}" rel="sponsored noopener">{inner}</a>'


def brand_text():
    name = CFG["site_name"]
    if name.endswith(" Sri Lanka"):
        return f'{esc(name[:-10])} <b>· Sri Lanka</b>'
    return esc(name)


def page(lang):
    c = C[lang]
    r = esc(reward(lang))
    suggest = {l: {"text": plain(l, C[l]["suggest"]), "go": plain(l, C[l]["suggest_go"]),
                   "close": plain(l, C[l]["dismiss"]), "href": rel(lang, page_path(l))}
               for l in LANGS if l != lang}
    js = JS.replace("__SUGGEST__", json.dumps(suggest, ensure_ascii=False))
    tick = icon("check")
    trust = "".join(f"<li>{tick}{esc(plain(lang, t))}</li>" for t in c["trust"])
    you = "".join(f"<li>{tick}<span>{rich(lang, x)}</span></li>" for x in c["you_items"])
    me = "".join(f"<li>{tick}<span>{rich(lang, x)}</span></li>" for x in c["me_items"])
    steps = "".join(f'<li><p class="num" aria-hidden="true">{i + 1:02d}</p><h3>{esc(plain(lang, s["t"]))}</h3><p>{rich(lang, s["d"])}</p></li>'
                    for i, s in enumerate(c["steps"]))
    tips = "".join(f'<div><h3>{esc(plain(lang, s["t"]))}</h3><p>{rich(lang, s["d"])}</p></div>' for s in c["tips"])
    chips = "".join(f"<li>{esc(p)}</li>" for p in c["places"])
    uses = "".join(f'<div><span class="tile">{icon(WHO_ICONS[i % 6])}</span><div><h3>{esc(plain(lang, s["t"]))}</h3><p>{rich(lang, s["d"])}</p></div></div>'
                   for i, s in enumerate(c["who"]))
    rules = "".join(f"<li>{rich(lang, x)}</li>" for x in c["rules"])
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{esc(plain(lang, f["q"]))}</summary><p>{rich(lang, f["a"])}</p></details>'
                  for i, f in enumerate(c["faq"]))
    final_lines = "".join(f'<span class="line">{hl(lang, ln, "sf")}</span>' for ln in c["final_lines"])
    foot_langs = "".join(f'<a href="{rel(lang, page_path(l))}" hreflang="{C[l]["hreflang"]}" lang="{C[l]["hreflang"]}">{esc(C[l]["name"])}</a>' for l in LANGS)
    arrow = icon("arrow")

    return f"""<!doctype html>
<html lang="{c['hreflang']}" dir="{c['dir']}">
<head>
{head(lang)}
</head>
<body>
<a class="skip" href="#main">{T(lang, 'skip')}</a>
<header class="top">
 <div class="wrap">
  <a class="brand" href="{rel(lang, page_path(lang))}" aria-label="{esc(CFG['site_name'])}">{LOGO}<span>{brand_text()}</span></a>
  <div class="top-right">
   <nav class="langs" aria-label="{T(lang, 'lang_label')}">{lang_switch(lang)}</nav>
   {ref_a('hcta', T(lang, 'header_cta'))}
  </div>
 </div>
</header>
<div class="suggest" id="suggest" hidden><div class="wrap"><span data-t></span><a href="#"></a><button type="button"></button></div></div>
<main id="main">
 <section class="hero">
  <div class="wrap">
   <div class="hero-copy">
    <p class="chip"><i></i>{T(lang, 'updated')}</p>
    <h1><span class="kick">{T(lang, 'h1')}</span><span class="big">{hl(lang, c['h1_sub'], 'mk')}</span></h1>
    <p class="lead">{rich(lang, c['lead'])}</p>
    <div class="ctas">
     {ref_a('btn btn-primary', T(lang, 'cta') + arrow, ' id="hero-cta"')}
     <a class="btn btn-ghost" href="#how">{T(lang, 'cta_secondary')}</a>
    </div>
    <ul class="trust">{trust}</ul>
    <div class="copy">
     <label for="reflink">{T(lang, 'copy_label')}</label>
     <div class="row"><input id="reflink" readonly value="{esc(REF)}"><button type="button" data-copy="{esc(REF)}" data-copied="{T(lang, 'copied')}">{T(lang, 'copy')}</button></div>
    </div>
    <p class="disclose">{T(lang, 'disclosure')}</p>
   </div>
   <div class="hero-side">
    <div class="ticket">
     <div class="art-wrap">{HERO_ART}</div>
     <div class="halves">
      <div class="half"><p class="lbl">{T(lang, 'ticket_you')}</p><p class="amt">{r}</p><p class="sub">{T(lang, 'ticket_you_sub')}</p></div>
      <div class="perf" aria-hidden="true"></div>
      <div class="half"><p class="lbl">{T(lang, 'ticket_me')}</p><p class="amt">{r}</p><p class="sub">{T(lang, 'ticket_me_sub')}</p></div>
     </div>
     <p class="tnote">{icon('info')}{T(lang, 'ticket_note')}</p>
    </div>
   </div>
  </div>
 </section>

 <section id="answer">
  <div class="wrap">
   <div class="quick"><h2>{T(lang, 'quick_h2')}</h2><p>{rich(lang, c['quick_p'])}</p></div>
  </div>
 </section>

 <section id="how" class="band">
  <div class="wrap">
   <p class="kicker">{T(lang, 'cta_secondary')}</p>
   <h2 class="h2">{T(lang, 'steps_h2')}</h2>
   <ol class="steps">{steps}</ol>
  </div>
 </section>

 <section id="rewards" class="sec">
  <div class="wrap">
   <h2 class="h2">{T(lang, 'both_h2')}</h2>
   <p class="intro">{rich(lang, c['both_intro'])}</p>
   <div class="duo">
    <div class="panel light"><p class="lbl">{T(lang, 'you_h3')}</p><p class="amt">{r}</p><ul class="ticks">{you}</ul></div>
    <div class="panel dark"><p class="lbl">{T(lang, 'me_h3')}</p><p class="amt">{r}</p><ul class="ticks">{me}</ul></div>
   </div>
  </div>
 </section>

 <section id="tips" class="sec">
  <div class="wrap">
   <h2 class="h2">{T(lang, 'tips_h2')}</h2>
   <p class="intro">{rich(lang, c['tips_intro'])}</p>
   <div class="tips">{tips}</div>
  </div>
 </section>

 <section id="who" class="sec">
  <div class="wrap">
   <h2 class="h2">{T(lang, 'who_h2')}</h2>
   <p class="intro">{rich(lang, c['who_intro'])}</p>
   <ul class="chips" aria-label="{T(lang, 'places_label')}">{chips}</ul>
   <div class="uses">{uses}</div>
  </div>
 </section>

 <section id="rules" class="sec">
  <div class="wrap">
   <div class="rules">{icon('info')}<div><h2>{T(lang, 'rules_h2')}</h2><ul>{rules}</ul></div></div>
  </div>
 </section>

 <section id="faq" class="sec">
  <div class="wrap faq">
   <div class="faq-side">
    <h2 class="h2">{T(lang, 'faq_h2')}</h2>
    <p>{T(lang, 'faq_intro')}</p>
    {ref_a('btn btn-ink', T(lang, 'faq_cta'))}
   </div>
   <div class="faq-list">{faq}</div>
  </div>
 </section>

 <section id="start">
  <div class="wrap">
   <div class="final">
    <h2>{final_lines}</h2>
    <p>{rich(lang, c['final_p'])}</p>
    {ref_a('btn btn-saffron', T(lang, 'cta') + arrow)}
    <p class="small">{T(lang, 'disclosure')}</p>
   </div>
  </div>
 </section>
</main>
<footer>
 <div class="wrap">
  <nav aria-label="{T(lang, 'footer_langs')}">{foot_langs}</nav>
  <p>{T(lang, 'footer_disclaimer')}</p>
  <p>{T(lang, 'updated')} · © {TODAY.year} {esc(CFG['site_name'])}</p>
 </div>
</footer>
<div class="mbar" id="mbar">{ref_a('', hl(lang, c['mbar'], 'sf'))}</div>
<script>{js}</script>
</body>
</html>
"""


def not_found():
    c = C[DEFAULT]
    links = "".join(f'<li><a href="{abs_url(l)}" lang="{C[l]["hreflang"]}">{esc(C[l]["name"])}</a></li>' for l in LANGS)
    msgs = "".join(f'<p lang="{C[l]["hreflang"]}"><strong>{esc(C[l]["notfound_h1"])}</strong> – {esc(C[l]["notfound_p"])}</p>' for l in LANGS)
    return f"""<!doctype html>
<html lang="{c['hreflang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 – {esc(CFG['site_name'])}</title><meta name="robots" content="noindex">
<link rel="icon" href="{SITE}/favicon.svg" type="image/svg+xml">
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#F7F5F0;color:#111318;font:16px/1.7 Inter,system-ui,sans-serif;padding:24px}}a{{color:#1F4FD1}}main{{max-width:520px}}h1{{font:700 64px/1 "Space Grotesk",Inter,sans-serif;margin:0 0 16px}}ul{{display:flex;gap:16px;padding:0;list-style:none;font-size:18px}}</style>
</head><body><main><h1>404</h1>{msgs}<ul>{links}</ul></main></body></html>
"""


def sitemap():
    rows = []
    for l in LANGS:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{C[x]["hreflang"]}" href="{abs_url(x)}"/>' for x in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(DEFAULT)}"/>'
        rows.append(f"  <url>\n    <loc>{abs_url(l)}</loc>\n    <lastmod>{TODAY.isoformat()}</lastmod>{alts}\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
           "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot",
           "meta-externalagent", "DuckAssistBot"]


def robots():
    lines = ["User-agent: *", "Allow: /", "", "# AI search engines and assistants are welcome to read and cite this site"]
    for b in AI_BOTS:
        lines += [f"User-agent: {b}", "Allow: /", ""]
    lines += [f"Sitemap: {SITE}/sitemap.xml", ""]
    return "\n".join(lines)


def llms_txt():
    en = C[DEFAULT]
    out = [f"# {CFG['site_name']}", "",
           f"> {plain(DEFAULT, en['description'])} Independent page, not affiliated with Starlink or SpaceX.", "",
           f"Starlink referral link for Sri Lanka: {REF}", "",
           "## Key facts",
           f"- Current Sri Lanka referral reward: both the new customer and the referrer get {CFG['reward']['en']} "
           f"({' / '.join(CFG['reward'][l] for l in LANGS if l != 'en')}). Set by Starlink; may change; terms apply.",
           "- There is no promo code to type: the referral code is built into the link above.",
           "- Open the link before ordering on starlink.com and finish the order in the same browser.",
           "- New Starlink customers only. Order directly on starlink.com; kits from shops or resellers are not eligible.",
           "- The link is for orders in Sri Lanka (Starlink referrals generally require both customers to be in the same country).",
           "- Rewards are issued after the new customer's Starlink is activated and the referral is confirmed.",
           f"- Last updated: {TODAY.isoformat()}", "",
           "## Pages"]
    for l in LANGS:
        out.append(f"- [{C[l]['name']}]({abs_url(l)}): {plain(l, C[l]['title'])}")
    out += ["", "## FAQ", ""]
    for f in en["faq"]:
        out += [f"### {plain(DEFAULT, f['q'])}", plain(DEFAULT, f["a"]), ""]
    for l in LANGS:
        if l == DEFAULT:
            continue
        out += [f"## {C[l]['name']}", "", plain(l, C[l]["quick_p"]), ""]
    return "\n".join(out)


HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
/og/*
  Cache-Control: public, max-age=604800
"""


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for l in LANGS:
        out = DIST / page_path(l) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(l), "utf-8")
    (DIST / "404.html").write_text(not_found(), "utf-8")
    (DIST / "sitemap.xml").write_text(sitemap(), "utf-8")
    (DIST / "robots.txt").write_text(robots(), "utf-8")
    (DIST / "llms.txt").write_text(llms_txt(), "utf-8")
    (DIST / "_headers").write_text(HEADERS, "utf-8")
    (DIST / ".nojekyll").write_text("", "utf-8")
    if CFG.get("indexnow_key"):  # IndexNow: lets Bing & co. index new/changed pages instantly
        (DIST / f"{CFG['indexnow_key']}.txt").write_text(CFG["indexnow_key"], "utf-8")
    assets = ROOT / "assets"
    for f in assets.rglob("*"):
        if f.is_file():
            dest = DIST / f.relative_to(assets)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
    if "your-domain.com" in SITE:
        print("NOTE: set site_url in config.json to your real domain before going live.")
    print(f"Built {len(LANGS)} pages into {DIST}")


if __name__ == "__main__":
    main()
