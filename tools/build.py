#!/usr/bin/env python3
"""Build the localized support pages from template.html + content/<code>.json.

    python3 tools/build.py          # writes index.html, <code>/index.html, sitemap.xml

`en` is served at the site root, every other locale at `/<code>/`. A locale
is included only when its JSON exists in tools/content/. The legal pages
(privacy.html / terms.html) are hand-written and untouched.
"""
import html, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SITE = "https://montanuch.github.io/flaspek-support/"
APP_ID = "6762515189"
STORE_URL = f"https://apps.apple.com/app/id{APP_ID}"
EMAIL = "vibeprogerai@gmail.com"
VERSION = "1.02"

# code (folder), hreflang, <html lang>, og:locale, native name, rtl
LOCALES = [
    ("en", "en",      "en",      "en_US", "English",            False),
    ("ru", "ru",      "ru",      "ru_RU", "Русский",            False),
    ("es", "es",      "es",      "es_ES", "Español",            False),
    ("zh", "zh-Hans", "zh-Hans", "zh_CN", "中文",                False),
    ("hi", "hi",      "hi",      "hi_IN", "हिन्दी",              False),
    ("fr", "fr",      "fr",      "fr_FR", "Français",           False),
    ("ar", "ar",      "ar",      "ar_SA", "العربية",            True),
    ("pt", "pt-BR",   "pt-BR",   "pt_BR", "Português",          False),
    ("id", "id",      "id",      "id_ID", "Bahasa Indonesia",   False),
    ("de", "de",      "de",      "de_DE", "Deutsch",            False),
    ("ja", "ja",      "ja",      "ja_JP", "日本語",              False),
    ("tr", "tr",      "tr",      "tr_TR", "Türkçe",             False),
    ("ko", "ko",      "ko",      "ko_KR", "한국어",              False),
    ("it", "it",      "it",      "it_IT", "Italiano",           False),
    ("uk", "uk",      "uk",      "uk_UA", "Українська",         False),
]
IN_LANGUAGE = [l[1] for l in LOCALES]

def url_for(code):
    return SITE if code == "en" else f"{SITE}{code}/"

def rel_href(from_code, to_code):
    """Relative link between pages (works on github.io and on a custom domain)."""
    if from_code == "en":
        return "./" if to_code == "en" else f"{to_code}/"
    return "../" if to_code == "en" else f"../{to_code}/"

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))

def esc(s):
    return html.escape(s, quote=True)

def render(code, hreflang, html_lang, og_locale, rtl, c, available, hints):
    root = "" if code == "en" else "../"
    url = url_for(code)
    hreflangs = [f'<link rel="alternate" hreflang="{hl}" href="{url_for(cd)}">'
                 for cd, hl, *_ in available]
    hreflangs.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}">')
    og_alts = [f'<meta property="og:locale:alternate" content="{ogl}">'
               for cd, _, _, ogl, *_ in available if cd != code]
    lang_links = []
    for cd, hl, _, _, native, _ in available:
        cur = ' aria-current="page"' if cd == code else ""
        lang_links.append(f'      <a href="{rel_href(code, cd)}" hreflang="{hl}" lang="{hl}" data-code="{cd}"{cur}>{native}</a>')
    steps = "\n".join(f"        <li><strong>{esc(b)}</strong> {t}</li>" for b, t in c["steps"])
    faq = "\n".join(f"\n      <h3>{esc(q)}</h3>\n      <p>{a}</p>" for q, a in c["faq"])
    req = "\n".join(f"        <li>{esc(r)}</li>" for r in c["req"])

    ld_app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Flaspek: LED Banner & Big Text",
        "alternateName": "Flaspek",
        "description": c["ld_description"],
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": c["ld_os"],
        "softwareVersion": VERSION,
        "url": url,
        "installUrl": STORE_URL,
        "downloadUrl": STORE_URL,
        "image": f"{SITE}og-image.png",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": c["ld_offer"]},
        "featureList": c["ld_features"],
        "inLanguage": IN_LANGUAGE,
        "author": {"@type": "Person", "name": "Viktor Gorbatiuk", "email": EMAIL},
        "sameAs": [STORE_URL],
    }
    ld_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": hreflang,
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in c["faq"]
        ],
    }
    # Hints for every OTHER locale, with hrefs relative to this page.
    my_hints = {cd: {"href": rel_href(code, cd), "text": hints[cd]} for cd in hints if cd != code}

    values = {
        "html_lang": html_lang, "dir": "rtl" if rtl else "ltr", "code": code,
        "url": url, "site": SITE, "app_id": APP_ID, "store_url": STORE_URL, "email": EMAIL,
        "root": root, "og_locale": og_locale,
        "hreflangs": "\n".join(hreflangs), "og_alternates": "\n".join(og_alts),
        "lang_links": "\n".join(lang_links), "steps": steps, "faq": faq, "req": req,
        "ld_app": json.dumps(ld_app, ensure_ascii=False, indent=2),
        "ld_faq": json.dumps(ld_faq, ensure_ascii=False, indent=2),
        "hints_json": json.dumps(my_hints, ensure_ascii=False),
    }
    for k in ("title", "description", "og_title", "og_description", "tagline", "store_cta",
              "what_h", "how_h", "support_h", "faq_h", "privacy_h", "privacy_link",
              "terms_link", "req_h", "footer_privacy", "footer_terms", "footer_contact"):
        values[k] = esc(c[k])
    for k in ("what_lead", "what_p", "modes_p", "support_p", "privacy_p"):
        values[k] = c[k]  # may carry <strong>/<em>

    tpl = (TOOLS / "template.html").read_text(encoding="utf-8")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], tpl)
    return out

def main():
    content = {}
    for cd, *_ in LOCALES:
        p = TOOLS / "content" / f"{cd}.json"
        if p.exists():
            content[cd] = json.loads(p.read_text(encoding="utf-8"))
    available = [l for l in LOCALES if l[0] in content]
    hints = {cd: content[cd]["hint"] for cd in content}
    # Every locale must carry exactly the English keys and FAQ count.
    en_keys = set(content["en"])
    for cd, c in content.items():
        missing = en_keys - set(c)
        if missing or len(c["faq"]) != len(content["en"]["faq"]):
            sys.exit(f"{cd}.json: missing {sorted(missing)} / faq {len(c['faq'])} != {len(content['en']['faq'])}")
    today = date.today().isoformat()
    urls = []
    for cd, hl, hlang, ogl, native, rtl in available:
        out = render(cd, hl, hlang, ogl, rtl, content[cd], available, hints)
        dest = ROOT / "index.html" if cd == "en" else ROOT / cd / "index.html"
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        urls.append((url_for(cd), today, "1.0" if cd == "en" else "0.9"))
        print(f"wrote {dest.relative_to(ROOT)}")
    alt = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{hl}" href="{url_for(cd)}"/>'
                  for cd, hl, *_ in available)
    alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
    entries = [f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{p}</priority>{alt}\n  </url>"
               for u, d, p in urls]
    for page in ("privacy.html", "terms.html"):
        entries.append(f"  <url>\n    <loc>{SITE}{page}</loc>\n    <lastmod>2026-10-14</lastmod>\n    <changefreq>yearly</changefreq>\n    <priority>0.3</priority>\n  </url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
               '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(entries) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("wrote sitemap.xml")
    # llms.txt is hand-written down to "## Pages"; the page list below it is generated.
    llms = ROOT / "llms.txt"
    head = llms.read_text(encoding="utf-8").split("## Pages")[0].rstrip()
    pages = [f"- Support & FAQ ({native}): {url_for(cd)}" for cd, _, _, _, native, _ in available]
    pages += [f"- Privacy Policy: {SITE}privacy.html", f"- Terms of Use: {SITE}terms.html"]
    llms.write_text(head + "\n\n## Pages\n\n" + "\n".join(pages) + "\n", encoding="utf-8")
    print("wrote llms.txt")

if __name__ == "__main__":
    main()
