#!/usr/bin/env python3
"""
Builder - attrezzi per costruire, controllare e consegnare la demo di un cliente.
Le pagine HTML le scrive l'agent (o tu) seguendo brief.md e lo stile scelto;
questo script fa il lavoro ripetitivo.

Comandi (dalla cartella principale del progetto):
  python builder/builder.py stili
  python builder/builder.py prepara clienti/sugar-s-a-s --stile atelier --colori accento=#485745
  python builder/builder.py immagini clienti/sugar-s-a-s 07-201621-1.jpg 36-logoimg-8276-low-7.jpg
  python builder/builder.py controlla clienti/sugar-s-a-s
  python builder/builder.py favicon clienti/sugar-s-a-s [--lettere DA] [--da logo.png]
  python builder/builder.py anteprima clienti/sugar-s-a-s
  python builder/builder.py screenshot clienti/sugar-s-a-s      (facoltativo, serve Playwright)
  python builder/builder.py pacchetto clienti/sugar-s-a-s

La demo finisce in clienti/<azienda>/demo/ ; il pacchetto per Netlify Drop in
clienti/<azienda>/demo-<azienda>-AAAAMMGG.zip
"""
import argparse
import datetime
import functools
import http.server
import io
import json
import os
import re
import shutil
import socketserver
import sys
import tarfile
import threading
import webbrowser
import zipfile
from html import escape as html_escape
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

try:
    import truststore  # type: ignore

    truststore.inject_into_ssl()
except Exception:
    pass

import requests
from PIL import Image, ImageOps

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STILI = os.path.join(RADICE, "stili")
CACHE_FONT = os.path.join(RADICE, ".cache", "font")
NPM = "https://registry.npmjs.org"
LARGHEZZE = (800, 1600)
COLORI = {  # nome in italiano -> variabile CSS
    "sfondo": "--c-bg", "superficie": "--c-surface", "testo": "--c-text", "attenuato": "--c-muted",
    "primario": "--c-primary", "su-primario": "--c-on-primary", "accento": "--c-accent",
    "scuro": "--c-dark", "su-scuro": "--c-on-dark", "linee": "--c-line",
}


def cartella_cliente(percorso):
    p = os.path.abspath(percorso)
    if not os.path.isdir(p):
        alt = os.path.join(RADICE, "clienti", percorso)
        if os.path.isdir(alt):
            return alt
        sys.exit(f"Cartella cliente non trovata: {percorso}")
    return p


def cartella_demo(cliente):
    return os.path.join(cliente, "demo")


def stili_disponibili():
    return sorted(d for d in os.listdir(STILI) if os.path.isfile(os.path.join(STILI, d, "stile.css")))


# ---------------------------------------------------------------- font

def scarica_pacchetto_font(pacchetto):
    """Scarica (una volta sola) il pacchetto Fontsource da npm e lo tiene in cache."""
    os.makedirs(CACHE_FONT, exist_ok=True)
    meta = requests.get(f"{NPM}/@fontsource/{pacchetto}/latest", timeout=(10, 30))
    meta.raise_for_status()
    info = meta.json()
    tgz = os.path.join(CACHE_FONT, f"{pacchetto}-{info['version']}.tgz")
    if not os.path.exists(tgz):
        print(f"  scarico il carattere {pacchetto} {info['version']}...")
        r = requests.get(info["dist"]["tarball"], timeout=(10, 120))
        r.raise_for_status()
        with open(tgz, "wb") as f:
            f.write(r.content)
    return tgz


def installa_font(stile, dest_font, dest_css):
    voci = json.load(open(os.path.join(STILI, stile, "font.json"), encoding="utf-8"))
    os.makedirs(dest_font, exist_ok=True)
    regole = ["/* Caratteri ospitati in locale (niente richieste a Google: più veloce e senza cookie). */"]
    for v in voci:
        tgz = scarica_pacchetto_font(v["pacchetto"])
        with tarfile.open(tgz, "r:gz") as t:
            nomi = t.getnames()
            richiesti = [(p, "normal") for p in v.get("pesi", [])] + [(p, "italic") for p in v.get("corsivo", [])]
            for peso, tipo in richiesti:
                nome = f"{v['pacchetto']}-latin-{peso}-{tipo}.woff2"
                membro = next((n for n in nomi if n.endswith("/files/" + nome)), None)
                if not membro:
                    print(f"  ! {nome} non presente nel pacchetto, salto")
                    continue
                with open(os.path.join(dest_font, nome), "wb") as f:
                    f.write(t.extractfile(membro).read())
                regole.append(
                    "@font-face { font-family: \"%s\"; font-style: %s; font-weight: %d; font-display: swap;\n"
                    "  src: url(\"../fonts/%s\") format(\"woff2\"); }" % (v["famiglia"], tipo, peso, nome))
    with open(dest_css, "w", encoding="utf-8") as f:
        f.write("\n".join(regole) + "\n")


# ---------------------------------------------------------------- prepara

def scrivi_tema(dest, colori):
    righe = ["/* Colori del cliente: sovrascrivono quelli dello stile. Modificabili a mano. */", ":root {"]
    for nome, valore in colori.items():
        righe.append(f"  {COLORI[nome]}: {valore};")
    righe.append("}")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(righe) + "\n")


def prepara(cliente, stile, colori, forza=False):
    if stile not in stili_disponibili():
        sys.exit(f"Stile '{stile}' inesistente. Disponibili: {', '.join(stili_disponibili())}")
    demo = cartella_demo(cliente)
    css, js, img = (os.path.join(demo, "assets", s) for s in ("css", "js", "img"))
    for d in (css, js, img):
        os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(STILI, "base.css"), css)
    shutil.copy(os.path.join(STILI, stile, "stile.css"), css)
    shutil.copy(os.path.join(STILI, "componenti.js"), js)
    tema = os.path.join(css, "tema.css")
    if colori or not os.path.exists(tema) or forza:
        scrivi_tema(tema, colori)
    print("Scarico i caratteri dello stile...")
    installa_font(stile, os.path.join(demo, "assets", "fonts"), os.path.join(css, "font.css"))
    index = os.path.join(demo, "index.html")
    if not os.path.exists(index):
        shutil.copy(os.path.join(STILI, "modello.html"), index)
    with open(os.path.join(demo, ".stile"), "w") as f:
        f.write(stile)
    print(f"\nDemo preparata in {os.path.relpath(demo, os.getcwd())} con lo stile '{stile}'.")
    print(f"Regole dello stile: stili/{stile}/stile.md")
    print("Prossimo passo: scegli le immagini con  builder.py immagini <cliente> <file...>")


# ---------------------------------------------------------------- immagini

def nome_pulito(file):
    base = os.path.splitext(os.path.basename(file))[0]
    base = re.sub(r"^(logo-)?\d{1,3}-", r"\1", base)
    return re.sub(r"[^a-z0-9-]+", "-", base.lower()).strip("-") or "img"


def ottimizza(src, dest_dir, nome, larghezze=LARGHEZZE, qualita=80):
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        trasparente = im.mode in ("RGBA", "LA", "P") and "transparency" in im.info or im.mode == "RGBA"
        im = im.convert("RGBA" if trasparente else "RGB")
        w, h = im.size
        uscite = {}
        misure = sorted({min(l, w) for l in larghezze})
        for lw in misure:
            out = im if lw == w else im.resize((lw, round(h * lw / w)), Image.LANCZOS)
            nome_file = f"{nome}-{lw}.webp"
            out.save(os.path.join(dest_dir, nome_file), "WEBP", quality=qualita, method=6)
            uscite[str(lw)] = nome_file
        return {"larghezza": w, "altezza": h, "file": uscite}


def immagini(cliente, file, tutte=False):
    demo = cartella_demo(cliente)
    if not os.path.isdir(demo):
        sys.exit("Prima lancia il comando 'prepara'.")
    sorgenti = os.path.join(cliente, "img")
    dest = os.path.join(demo, "assets", "img")
    os.makedirs(dest, exist_ok=True)
    manifesto_p = os.path.join(dest, "immagini.json")
    manifesto = json.load(open(manifesto_p, encoding="utf-8")) if os.path.exists(manifesto_p) else {}
    if tutte:
        file = sorted(f for f in os.listdir(sorgenti) if re.search(r"\.(jpe?g|png|webp)$", f, re.I))
    for f in file:
        src = f if os.path.isfile(f) else os.path.join(sorgenti, f)
        if not os.path.isfile(src):
            print(f"  ! non trovata: {f}")
            continue
        nome = nome_pulito(src)
        info = ottimizza(src, dest, nome)
        info["origine"] = os.path.basename(src)
        manifesto[nome] = info
        prima = os.path.getsize(src) // 1024
        dopo = sum(os.path.getsize(os.path.join(dest, x)) for x in info["file"].values()) // 1024
        avviso = "  ⚠ piccola: usala solo in riquadri" if info["larghezza"] < 800 else ""
        print(f"  {nome}: {info['larghezza']}×{info['altezza']}  {prima} KB → {dopo} KB{avviso}")
    with open(manifesto_p, "w", encoding="utf-8") as fh:
        json.dump(manifesto, fh, indent=2, ensure_ascii=False)
    print("\nEsempio di codice per una delle immagini:")
    if manifesto:
        nome, info = next(iter(manifesto.items()))
        print(tag_img(nome, info))


def tag_img(nome, info, alt="DESCRIZIONE", sizes="100vw"):
    file = {str(k): v for k, v in info["file"].items()}
    misure = sorted(int(k) for k in file)
    srcset = ", ".join(f"assets/img/{file[str(m)]} {m}w" for m in misure)
    grande = misure[-1]
    h = round(info["altezza"] * grande / info["larghezza"])
    return (f'<img src="assets/img/{file[str(grande)]}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{grande}" height="{h}" alt="{alt}" loading="lazy" decoding="async">')


# ---------------------------------------------------------------- favicon

FONT_CANDIDATI = ["georgia.ttf", "Georgia.ttf", "DejaVuSerif.ttf", "times.ttf", "arial.ttf", "DejaVuSans.ttf",
                  "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/arial.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/Library/Fonts/Georgia.ttf"]
LINK_FAVICON = ('  <link rel="icon" href="favicon.ico" sizes="any">\n'
                '  <link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
                '  <link rel="apple-touch-icon" href="apple-touch-icon.png">\n')


def colore_tema(cartella, nome, predefinito):
    for f in ("tema.css", "stile.css"):
        p = os.path.join(cartella, "assets", "css", f)
        if os.path.exists(p):
            m = re.search(rf"--{nome}:\s*(#[0-9a-fA-F]{{3,8}})", open(p, encoding="utf-8").read())
            if m:
                return m.group(1)
    return predefinito


def iniziali_da_sito(cartella):
    p = os.path.join(cartella, "index.html")
    if os.path.exists(p):
        m = re.search(r'<a class="brand[^"]*"[^>]*>([^<]+)', open(p, encoding="utf-8").read())
        if m:
            parole = [w for w in re.findall(r"[A-Za-zÀ-ÿ0-9]+", m.group(1)) if len(w) > 1 or w.isdigit()]
            return "".join(w[0] for w in parole[:2]).upper() or "?"
    return "?"


def _font(dim):
    from PIL import ImageFont
    for f in FONT_CANDIDATI:
        try:
            return ImageFont.truetype(f, dim)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=dim)
    except TypeError:
        return ImageFont.load_default()


def _monogramma(lettere, sfondo, testo, lato, arrotonda=True):
    from PIL import ImageDraw
    im = Image.new("RGBA", (lato, lato), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, lato - 1, lato - 1), radius=int(lato * 0.18) if arrotonda else 0, fill=sfondo)
    font = _font(int(lato * (0.56 if len(lettere) == 1 else 0.44)))
    x0, y0, x1, y1 = d.textbbox((0, 0), lettere, font=font)
    d.text(((lato - (x1 - x0)) / 2 - x0, (lato - (y1 - y0)) / 2 - y0), lettere, font=font, fill=testo)
    return im


def collega_favicon(cartella):
    """Aggiunge i link della favicon nell'<head> di tutte le pagine che non li hanno."""
    n = 0
    for pg in sorted(f for f in os.listdir(cartella) if f.endswith(".html")):
        p = os.path.join(cartella, pg)
        html_ = open(p, encoding="utf-8").read()
        if 'rel="icon"' in html_:
            continue
        nuovo = re.sub(r"(<title>.*?</title>\s*\n)", lambda m: m.group(1) + LINK_FAVICON, html_, count=1, flags=re.S)
        if nuovo == html_:
            nuovo = html_.replace("</head>", LINK_FAVICON + "</head>", 1)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(nuovo)
        n += 1
    return n


def crea_favicon(cartella, lettere=None, sorgente=None, sfondo=None, testo=None):
    """Crea favicon.ico, favicon.svg e apple-touch-icon.png in `cartella` (demo o sito definitivo)."""
    sfondo = sfondo or colore_tema(cartella, "c-accent", colore_tema(cartella, "c-primary", "#1d1d1b"))
    testo = testo or "#ffffff"
    lettere = (lettere or iniziali_da_sito(cartella))[:2]
    if sorgente:
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(sorgente)).convert("RGBA"), (512, 512))
        grande = im
    else:
        grande = _monogramma(lettere, sfondo, testo, 512)
    apple = grande.resize((180, 180), Image.LANCZOS) if sorgente else _monogramma(lettere, sfondo, testo, 180, False)
    apple.save(os.path.join(cartella, "apple-touch-icon.png"))  # iOS arrotonda da solo gli angoli
    grande.save(os.path.join(cartella, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    svg = os.path.join(cartella, "favicon.svg")
    if sorgente:
        if os.path.exists(svg):
            os.remove(svg)
    else:
        dim = 36 if len(lettere) == 1 else 28
        with open(svg, "w", encoding="utf-8") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
                    f'<rect width="64" height="64" rx="12" fill="{sfondo}"/>'
                    f'<text x="32" y="33" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="Georgia, \'Times New Roman\', serif" font-size="{dim}" fill="{testo}">'
                    f'{html_escape(lettere)}</text></svg>\n')
    collegate = collega_favicon(cartella)
    if sorgente:  # niente svg: togli il link che punterebbe a un file mancante
        for pg in (f for f in os.listdir(cartella) if f.endswith(".html")):
            p = os.path.join(cartella, pg)
            t = open(p, encoding="utf-8").read().replace('  <link rel="icon" href="favicon.svg" type="image/svg+xml">\n', "")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(t)
    print(f"Favicon creata ({'da ' + os.path.basename(sorgente) if sorgente else 'monogramma ' + lettere + ' ' + sfondo})"
          f": favicon.ico, apple-touch-icon.png{'' if sorgente else ', favicon.svg'}"
          f" · link aggiunti in {collegate} pagine")


# ---------------------------------------------------------------- controlla

class Analizzatore(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag = []
        self.h1 = 0
        self.testo = []

    def handle_starttag(self, tag, attrs):
        self.tag.append((tag, dict(attrs)))
        if tag == "h1":
            self.h1 += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.testo.append(data)


def controlla(cliente):
    demo = cartella_demo(cliente)
    pagine = sorted(f for f in os.listdir(demo) if f.endswith(".html")) if os.path.isdir(demo) else []
    if not pagine:
        sys.exit("Nessuna pagina HTML nella demo.")
    errori, avvisi = [], []
    for pg in pagine:
        percorso = os.path.join(demo, pg)
        html = open(percorso, encoding="utf-8").read()
        a = Analizzatore()
        a.feed(html)
        tags = a.tag
        attr = lambda t: [d for n, d in tags if n == t]
        e = lambda m: errori.append(f"{pg}: {m}")
        w = lambda m: avvisi.append(f"{pg}: {m}")

        if not any(d.get("lang") for d in attr("html")):
            e("manca lang=\"it\" su <html>")
        metas = attr("meta")
        if not any(d.get("name") == "viewport" for d in metas):
            e("manca il meta viewport (la pagina non si adatta al telefono)")
        if not any(d.get("name") == "robots" and "noindex" in d.get("content", "") for d in metas):
            e("manca <meta name=\"robots\" content=\"noindex\">: la demo finirebbe su Google")
        if not any(d.get("name") == "description" and len(d.get("content", "")) > 50 for d in metas):
            w("meta description mancante o troppo corta")
        if not re.search(r"<title>[^<{]{5,}</title>", html):
            e("titolo della pagina mancante o da compilare")
        if "demo-tag" not in html:
            e("manca l'avviso .demo-tag (la demo non deve sembrare il sito ufficiale)")
        if a.h1 != 1:
            w(f"ci sono {a.h1} titoli <h1> (ne serve esattamente 1)")
        testo = " ".join(a.testo)
        for segnaposto in re.findall(r"\{\{[^}]{0,40}\}\}|lorem ipsum|TODO|XXX", html, re.I):
            e(f"segnaposto rimasto: {segnaposto[:40]}")
        if "fonts.googleapis" in html or "fonts.gstatic" in html:
            w("caratteri caricati da Google: usa quelli locali di font.css")
        for m in re.findall(r'(?:src|href)="(http://[^"]+)"', html):
            e(f"risorsa non sicura (http): {m}")

        peso = os.path.getsize(percorso)
        visti = set()
        for n, d in tags:
            for chiave in ("src", "href", "srcset", "data-lightbox"):
                val = d.get(chiave)
                if not val:
                    continue
                candidati = [p.strip().split(" ")[0] for p in val.split(",")] if chiave == "srcset" else [val]
                for c in candidati:
                    u = urlparse(c)
                    if u.scheme or c.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                        continue
                    locale = os.path.normpath(os.path.join(demo, unquote(u.path)))
                    if not os.path.exists(locale):
                        e(f"file mancante: {c}")
                    elif locale not in visti and os.path.isfile(locale):
                        visti.add(locale)
                        if chiave not in ("data-lightbox",) and not (chiave == "srcset"):
                            peso += os.path.getsize(locale)
                        if os.path.getsize(locale) > 500 * 1024 and locale.endswith((".jpg", ".jpeg", ".png", ".webp")):
                            w(f"immagine pesante ({os.path.getsize(locale)//1024} KB): {c}")
            if n == "img":
                if "alt" not in d:
                    e(f"immagine senza alt: {d.get('src')}")
                if not (d.get("width") and d.get("height")):
                    w(f"immagine senza width/height (la pagina 'salta' mentre carica): {d.get('src')}")
                if d.get("src", "").lower().endswith((".jpg", ".jpeg", ".png")) and "logo" not in d.get("src", ""):
                    w(f"immagine non ottimizzata (usa il comando immagini): {d.get('src')}")
        for css in ("assets/css/base.css", "assets/css/stile.css", "assets/css/tema.css", "assets/css/font.css"):
            if css not in html:
                w(f"non collega {css}")
        if 'rel="icon"' not in html:
            w("manca la favicon (icona della scheda): builder.py favicon <cliente>")
        if not re.search(r'href="tel:', html) and pg == "index.html":
            w("nessun numero di telefono cliccabile (tel:)")
        if peso > 2.5 * 1024 * 1024:
            w(f"pagina pesante: circa {peso // 1024} KB al primo caricamento")
        print(f"  {pg}: ~{peso // 1024} KB")

    print()
    for x in errori:
        print("  ✗ " + x)
    for x in avvisi:
        print("  ! " + x)
    if not errori and not avvisi:
        print("  ✓ Tutto a posto.")
    print(f"\n{len(errori)} errori, {len(avvisi)} avvisi.")
    return not errori


# ---------------------------------------------------------------- anteprima, screenshot, pacchetto

class GestoreSilenzioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):  # niente righe di log nel prompt
        pass


def anteprima(cliente, porta=8000):
    demo = cartella_demo(cliente)
    gestore = functools.partial(GestoreSilenzioso, directory=demo)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", porta), gestore) as srv:
        url = f"http://127.0.0.1:{porta}/"
        print(f"Anteprima su {url}")
        print("È solo per te, sul tuo PC: il cliente vedrà la versione pubblicata su Netlify.")
        print("Per chiudere premi Ctrl+C (se non risponde: Ctrl+Interr, oppure chiudi la finestra).")
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nAnteprima chiusa.")


def screenshot(cliente):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Serve Playwright:  .venv\\Scripts\\pip install playwright  e poi  .venv\\Scripts\\playwright install chromium")
    demo = cartella_demo(cliente)
    uscita = os.path.join(cliente, "screenshot")
    os.makedirs(uscita, exist_ok=True)
    class Silenzioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    gestore = functools.partial(Silenzioso, directory=demo)
    srv = socketserver.TCPServer(("127.0.0.1", 0), gestore)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    pagine = sorted(f for f in os.listdir(demo) if f.endswith(".html"))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for nome, vista in (("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})):
            ctx = browser.new_context(viewport=vista, device_scale_factor=2 if nome == "mobile" else 1,
                                      is_mobile=nome == "mobile", has_touch=nome == "mobile")
            pg = ctx.new_page()
            for f in pagine:
                pg.goto(base + f, wait_until="networkidle")
                # Carica subito le immagini "lazy" e mostra gli elementi animati, poi fotografa
                pg.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
                pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');"
                            "document.querySelectorAll('[data-reveal]').forEach(e=>e.classList.add('is-visible'))")
                altezza = pg.evaluate("document.documentElement.scrollHeight")
                for y in range(0, altezza, 400):  # scorre come un visitatore: le immagini partono
                    pg.evaluate(f"window.scrollTo(0, {y})")
                    pg.wait_for_timeout(80)
                pg.evaluate("window.scrollTo(0, 0)")
                pg.wait_for_load_state("networkidle")
                try:
                    pg.wait_for_function("[...document.images].filter(i => i.getAttribute('src'))"
                                         ".every(i => i.complete && i.naturalWidth > 0)", timeout=20000)
                except Exception:
                    print(f"  ! {f} ({nome}): alcune immagini non si sono caricate in tempo")
                pg.wait_for_timeout(300)
                dest = os.path.join(uscita, f"{os.path.splitext(f)[0]}-{nome}.jpg")
                pg.screenshot(path=dest, full_page=True, type="jpeg", quality=80)
                print(f"  {os.path.relpath(dest, os.getcwd())}")
            ctx.close()
        browser.close()
    srv.shutdown()


def pacchetto(cliente):
    print("Controllo la demo prima di impacchettarla...")
    if not controlla(cliente):
        sys.exit("\nCorreggi gli errori prima di creare il pacchetto.")
    demo = cartella_demo(cliente)
    with open(os.path.join(demo, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n")
    with open(os.path.join(demo, "_headers"), "w") as f:  # letto da Netlify
        f.write("/*\n  X-Robots-Tag: noindex, nofollow\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    slug = os.path.basename(os.path.normpath(cliente))
    nome = f"demo-{slug}-{datetime.date.today():%Y%m%d}.zip"
    dest = os.path.join(cliente, nome)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for radice, _, files in os.walk(demo):
            for f in files:
                if f in (".stile", "immagini.json"):
                    continue
                pieno = os.path.join(radice, f)
                z.write(pieno, os.path.relpath(pieno, demo))
    print(f"\nPacchetto pronto: {os.path.relpath(dest, os.getcwd())} ({os.path.getsize(dest) // 1024} KB)")
    print("Pubblicalo trascinando la CARTELLA demo (o lo zip estratto) su https://app.netlify.com/drop")


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description="Builder: prepara, controlla e impacchetta le demo.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stili", help="Elenca gli stili disponibili")
    s = sub.add_parser("prepara", help="Crea la cartella demo con stile, caratteri e colori")
    s.add_argument("cliente")
    s.add_argument("--stile", required=True)
    s.add_argument("--colori", default="", help="es. accento=#485745,primario=#1d1d1b")
    s.add_argument("--forza", action="store_true", help="Riscrive tema.css anche se esiste")
    s = sub.add_parser("immagini", help="Ottimizza le immagini scelte in WebP (800 e 1600 px)")
    s.add_argument("cliente")
    s.add_argument("file", nargs="*")
    s.add_argument("--tutte", action="store_true")
    for nome, aiuto in (("controlla", "Controlla la demo"), ("screenshot", "Foto della demo, desktop e mobile"),
                        ("pacchetto", "Controlla e crea lo zip per Netlify")):
        sub.add_parser(nome, help=aiuto).add_argument("cliente")
    s = sub.add_parser("favicon", help="Crea l'icona della scheda (monogramma o da un'immagine)")
    s.add_argument("cliente")
    s.add_argument("--lettere", help="1-2 lettere del monogramma (default: iniziali del nome nel menu)")
    s.add_argument("--da", help="Immagine quadrata da usare al posto del monogramma (es. il simbolo del logo)")
    s.add_argument("--colore", help="Colore di sfondo (default: accento del tema)")
    s = sub.add_parser("anteprima", help="Apre la demo nel browser")
    s.add_argument("cliente")
    s.add_argument("--porta", type=int, default=8000)

    a = p.parse_args()
    if a.cmd == "stili":
        for st in stili_disponibili():
            prima = open(os.path.join(STILI, st, "stile.md"), encoding="utf-8").read().split("\n")
            settori = next((r for r in prima if r.startswith("**Settori")), "")
            print(f"  {st:<10} {settori.replace('**Settori:**', '').strip()[:90]}")
        return
    cliente = cartella_cliente(a.cliente)
    if a.cmd == "prepara":
        colori = {}
        for coppia in filter(None, (x.strip() for x in a.colori.split(","))):
            k, _, v = coppia.partition("=")
            if k.strip() not in COLORI:
                sys.exit(f"Colore '{k}' sconosciuto. Usa: {', '.join(COLORI)}")
            colori[k.strip()] = v.strip()
        prepara(cliente, a.stile, colori, a.forza)
    elif a.cmd == "immagini":
        immagini(cliente, a.file, a.tutte)
    elif a.cmd == "controlla":
        sys.exit(0 if controlla(cliente) else 1)
    elif a.cmd == "favicon":
        crea_favicon(cartella_demo(cliente), a.lettere, a.da, a.colore)
    elif a.cmd == "anteprima":
        anteprima(cliente, a.porta)
    elif a.cmd == "screenshot":
        screenshot(cliente)
    elif a.cmd == "pacchetto":
        pacchetto(cliente)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ProxyError as e:
        sys.exit(f"\nErrore di proxy: {e}\nControlla HTTPS_PROXY o il filtro web aziendale.")
    except requests.RequestException as e:
        sys.exit(f"\nErrore di rete: {e}")
