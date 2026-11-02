#!/usr/bin/env python3
"""
Analista - estrae dal sito di un prospect tutto quello che serve per la demo:
testi pagina per pagina, contatti, logo, colori, immagini (scaricate) e sorgenti HTML.

Comandi (dalla cartella principale del progetto):
  python analista/analista.py analizza www.sito-azienda.it --nome "Rossi Srl"
  python analista/analista.py da-csv prospect/vigevano.csv --nome "SUGAR s.a.s."
  python analista/analista.py da-csv prospect/vigevano.csv --primi 3

Risultato in clienti/<nome-azienda>/:
  contenuti.md     riassunto leggibile (da qui parte il Builder)
  contenuti.json   gli stessi dati in formato strutturato
  img/             immagini scaricate, logo compreso
  sorgente/        HTML originale di ogni pagina visitata
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter
from urllib.parse import unquote, urldefrag, urljoin, urlparse

try:
    import truststore  # type: ignore

    truststore.inject_into_ssl()
except Exception:
    pass

import requests
from bs4 import BeautifulSoup

try:
    from PIL import Image

    PIL_OK = True
except Exception:
    PIL_OK = False

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
TIMEOUT = (6, 20)
MAX_IMMAGINI = 40
MIN_BYTE_IMMAGINE = 3000      # sotto: icone, pixel, spaziatori
BASSA_RISOLUZIONE = 800       # lato lungo in pixel

# Parole che indicano le pagine più utili, con il loro peso.
PAGINE_UTILI = [
    ("chi-siamo", 10), ("chi siamo", 10), ("chisiamo", 10), ("azienda", 9), ("about", 8),
    ("storia", 8), ("profilo", 7), ("servizi", 9), ("prodotti", 9), ("lavorazioni", 9),
    ("produzione", 8), ("macchin", 7), ("soluzioni", 7), ("settori", 7), ("attivita", 6),
    ("referenze", 6), ("clienti", 5), ("portfolio", 6), ("realizzazioni", 7), ("lavori", 5),
    ("gallery", 5), ("galleria", 5), ("foto", 4), ("certificaz", 6), ("qualita", 5),
    ("contatt", 9), ("dove", 6), ("menu", 6), ("camere", 6), ("ristorante", 6),
    ("cucina", 5), ("listino", 5), ("catalogo", 6), ("collezion", 7), ("negozio", 5),
    ("shop", 4), ("brand", 5), ("marchi", 5),
    # Archivi cronologici: si visitano solo se non resta altro.
    ("news", 0), ("eventi", 0), ("blog", 0), ("press", 0), ("archivio", -2),
]
PAGINAZIONE = re.compile(r"[?&](pagina|page|pag|p|start|offset|paged|pg)=\d+|/page/\d+", re.I)
ESCLUDI_LINK = re.compile(
    r"(privacy|cookie|login|logout|account|carrello|cart|checkout|wp-admin|wp-login|"
    r"feed|/tag/|/author/|\?replytocom|\.(pdf|jpe?g|png|gif|webp|zip|rar|docx?|xlsx?|mp4|mp3)$|"
    r"/(en|de|fr|es)(/|$)|[?&]lang=(en|de|fr|es))",
    re.I,
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TELEFONO = re.compile(r"(?<![\d])(?:\+39[\s.]?)?(?:0\d{1,3}|3\d{2})[\s./-]?\d{3,4}[\s.-]?\d{2,4}(?![\d])")
PIVA = re.compile(r"(?:p\.?\s?i\.?v\.?a\.?|partita\s+iva|vat)[^0-9]{0,25}(?:it)?\s?(\d{11})", re.I)
INDIRIZZO = re.compile(
    r"((?:via|viale|corso|c\.so|piazza|p\.zza|piazzale|strada|str\.|località|loc\.|vicolo)"
    r"\s+[^\n|•]{2,50}?\d{1,4}[a-zA-Z/]*[^\n|•]{0,40}?\b\d{5}\b[^\n|•]{0,40})",
    re.I,
)
COLORE_HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
COLORE_RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
URL_CSS = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.I)
SOCIAL = ("facebook.com", "instagram.com", "linkedin.com", "youtube.com", "tiktok.com", "x.com", "twitter.com")

_sessione = None


def sessione():
    global _sessione
    if _sessione is None:
        _sessione = requests.Session()
        _sessione.headers.update({"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9"})
    return _sessione


# ---------------------------------------------------------------- utilità

def slug(testo):
    s = re.sub(r"[^a-z0-9]+", "-", (testo or "").lower()).strip("-")
    return s[:50] or "azienda"


def normalizza_url(u):
    u = (u or "").strip()
    if u and not re.match(r"^https?://", u, re.I):
        u = "http://" + u
    return u


def url_pagina(u):
    """Normalizza l'indirizzo di una pagina: /index.html e / sono la stessa pagina."""
    u = urldefrag(u)[0]
    u = re.sub(r"/(index|default|home)\.(html?|php|asp|aspx)$", "/", u, flags=re.I)
    return u.rstrip("/")


def host_base(u):
    h = urlparse(u).netloc.lower().split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h


def scarica(url, binario=False):
    try:
        r = sessione().get(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException as e:
        print(f"  ! non raggiungibile: {url} ({e.__class__.__name__})", file=sys.stderr)
        return None
    if r.status_code >= 400:
        print(f"  ! errore {r.status_code}: {url}", file=sys.stderr)
        return None
    if not binario and (not r.encoding or r.encoding.lower() == "iso-8859-1"):
        r.encoding = r.apparent_encoding
    return r


def pulisci_tel(t):
    cifre = re.sub(r"\D", "", t or "")
    if cifre.startswith("0039"):
        cifre = cifre[4:]
    elif cifre.startswith("39") and len(cifre) >= 11:
        cifre = cifre[2:]
    if len(set(cifre.lstrip("0"))) <= 1:
        return ""
    if cifre.startswith("0") and 6 <= len(cifre) <= 10:
        return "+39 " + cifre
    if cifre.startswith("3") and len(cifre) == 10:
        return "+39 " + cifre
    return ""


def hex_normale(h):
    h = h.lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def rgb(hexcol):
    h = hexcol.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def e_neutro(hexcol):
    r, g, b = rgb(hexcol)
    return max(r, g, b) - min(r, g, b) < 24  # bianco, nero, grigi


# ---------------------------------------------------------------- pagine

def link_interni(zuppa, base_url, host):
    trovati = []
    for tag, attr in (("a", "href"), ("area", "href"), ("frame", "src"), ("iframe", "src")):
        for el in zuppa.find_all(tag):
            href = (el.get(attr) or "").strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            url = url_pagina(urljoin(base_url, href))
            if urlparse(url).scheme not in ("http", "https") or host_base(url) != host:
                continue
            if ESCLUDI_LINK.search(url):
                continue
            testo = el.get_text(" ", strip=True) if tag in ("a", "area") else "frame"
            trovati.append((url, testo, tag))
    return trovati


def peso_link(url, testo, tag):
    chiave = (unquote(urlparse(url).path) + " " + testo).lower()
    chiave = chiave.replace("à", "a").replace("è", "e").replace("é", "e")
    pesi = [p for parola, p in PAGINE_UTILI if parola in chiave]
    peso = (min(pesi) if any(p <= 0 for p in pesi) else max(pesi)) if pesi else 1
    if PAGINAZIONE.search(url):
        peso -= 20  # pagina 2, 3, 4... di un elenco: quasi mai utile
    elif urlparse(url).query:
        peso -= 3
    if tag in ("frame", "iframe"):
        peso += 20  # nei siti a frame il contenuto vero sta lì dentro
    peso -= urlparse(url).path.count("/") * 0.5  # meglio le pagine di primo livello
    return peso


def righe_testo(zuppa):
    z = BeautifulSoup(str(zuppa), "html.parser")
    for t in z(["head", "title", "script", "style", "noscript", "svg", "form", "select", "option"]):
        t.decompose()
    for br in z.find_all("br"):
        br.replace_with("\n")
    righe, prec = [], None
    for r in z.get_text("\n").split("\n"):
        r = re.sub(r"\s+", " ", r).strip()
        if len(r) < 2 or r == prec:
            continue
        righe.append(r)
        prec = r
    return righe


def immagini_pagina(zuppa, base_url, css_testo=""):
    trovate = []

    def aggiungi(src, alt="", origine="img"):
        src = (src or "").strip()
        if not src or src.startswith("data:"):
            return
        trovate.append({"url": urljoin(base_url, src), "alt": (alt or "").strip(), "origine": origine})

    for img in zuppa.find_all("img"):
        src = img.get("data-src") or img.get("data-lazy-src") or img.get("src")
        srcset = img.get("data-srcset") or img.get("srcset")
        if srcset:  # prende la versione più grande
            candidati = [p.strip().split(" ") for p in srcset.split(",") if p.strip()]
            def larghezza(c):
                try:
                    return int(re.sub(r"\D", "", c[1])) if len(c) > 1 else 0
                except ValueError:
                    return 0
            migliore = max(candidati, key=larghezza)
            if migliore and migliore[0]:
                src = migliore[0]
        aggiungi(src, img.get("alt") or img.get("title"), "img")
    for el in zuppa.find_all(["input"], attrs={"type": "image"}):
        aggiungi(el.get("src"), el.get("alt"), "img")
    for el in zuppa.find_all(attrs={"background": True}):  # siti anni 2000
        aggiungi(el.get("background"), "", "sfondo")
    for el in zuppa.find_all(style=True):
        for u in URL_CSS.findall(el["style"]):
            aggiungi(u, "", "sfondo")
    for u in URL_CSS.findall(css_testo):
        if re.search(r"\.(jpe?g|png|webp)", u, re.I):
            aggiungi(u, "", "sfondo-css")
    og = zuppa.find("meta", attrs={"property": "og:image"})
    if og and og.get("content"):
        aggiungi(og["content"], "og:image", "og")
    return trovate


def _firma(el):
    return " ".join([el.get("id") or "", " ".join(el.get("class") or []), el.get("name") or ""])


def candidati_logo(zuppa, base_url, home_url):
    """Riconosce il logo da: nome file/alt/id/classe dell'immagine, id o classe dei contenitori
    (es. <div id="logo">), oppure immagine in testata che porta alla homepage."""
    loghi, tutte = [], zuppa.find_all("img")
    for i, img in enumerate(tutte):
        src = img.get("data-src") or img.get("src")
        if not src:
            continue
        firma = " ".join([src, img.get("alt") or "", _firma(img)])
        firma += " " + " ".join(_firma(p) for p in list(img.parents)[:4])
        link = img.find_parent("a")
        verso_home = bool(link and link.get("href") and
                          url_pagina(urljoin(base_url, link["href"])) == url_pagina(home_url))
        if "logo" in firma.lower() or (verso_home and i < 5):
            loghi.append(urljoin(base_url, src))
    icone = []
    for el in zuppa.find_all("link", href=True):
        rel = " ".join(el.get("rel") or []).lower()
        if "apple-touch-icon" in rel:
            icone.insert(0, urljoin(base_url, el["href"]))
        elif "icon" in rel:
            icone.append(urljoin(base_url, el["href"]))
    return loghi + icone


def colori_da_testo(testo):
    colori = [hex_normale(h) for h in COLORE_HEX.findall(testo)]
    colori += ["#%02x%02x%02x" % tuple(min(255, int(x)) for x in m) for m in COLORE_RGB.findall(testo)]
    return colori


def colori_html(zuppa):
    testo = " ".join(s.get_text() for s in zuppa.find_all("style"))
    testo += " ".join(el["style"] for el in zuppa.find_all(style=True))
    for attr in ("bgcolor", "color", "text", "link", "vlink", "alink"):  # HTML vecchio
        for el in zuppa.find_all(attrs={attr: True}):
            testo += " " + str(el.get(attr))
    return colori_da_testo(testo)


def palette_immagine(percorso, n=5):
    if not PIL_OK:
        return []
    try:
        with Image.open(percorso) as im:
            im = im.convert("RGBA")
            im.thumbnail((200, 200))
            dati = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
            pixel = [p[:3] for p in dati if p[3] > 128]
            if not pixel:
                return []
            piccola = Image.new("RGB", (len(pixel), 1))
            piccola.putdata(pixel)
            q = piccola.quantize(colors=n + 3)
            pal = q.getpalette()
            conteggi = sorted(q.getcolors(), reverse=True)
            colori = []
            for cnt, idx in conteggi:
                c = "#%02x%02x%02x" % tuple(pal[idx * 3: idx * 3 + 3])
                if not e_neutro(c) and c not in colori:
                    colori.append(c)
            return colori[:n]
    except Exception:
        return []


def dimensioni(percorso):
    if not PIL_OK:
        return None
    try:
        with Image.open(percorso) as im:
            return im.size
    except Exception:
        return None


# ---------------------------------------------------------------- analisi

def analizza(url, nome=None, max_pagine=10, cartella_clienti=None, riga_csv=None):
    url = normalizza_url(url)
    pu = urlparse(url)
    radice = f"{pu.scheme}://{pu.netloc}/"
    print(f"Analizzo {radice}", file=sys.stderr)
    home = scarica(radice)  # si parte sempre dalla homepage, anche se il link è a una sottopagina
    if home is None and url.rstrip("/") != radice.rstrip("/"):
        home = scarica(url)
    if home is None:
        sys.exit(f"Il sito {url} non risponde: niente da analizzare.")
    host = host_base(home.url)
    zuppa_home = BeautifulSoup(home.text, "html.parser")
    titolo_home = zuppa_home.title.get_text(strip=True) if zuppa_home.title else ""
    nome = nome or (riga_csv or {}).get("nome") or titolo_home.split("|")[0].split("-")[0].strip() or host
    cartella = os.path.join(cartella_clienti or os.path.join(RADICE, "clienti"), slug(nome))
    for sotto in ("img", "sorgente"):  # una nuova analisi sostituisce la precedente
        shutil.rmtree(os.path.join(cartella, sotto), ignore_errors=True)
        os.makedirs(os.path.join(cartella, sotto), exist_ok=True)

    # 1-2. Visita: si parte dalla home e ogni pagina letta aggiunge i suoi link alla coda.
    #      Si visita sempre il link più utile non ancora visto (chi siamo, servizi, contatti...).
    #      Funziona anche con i siti a frame, dove il menu sta dentro un frame.
    candidati, visti = {}, set()
    if url_pagina(url) != url_pagina(home.url) and host_base(url) == host:
        candidati[url_pagina(url)] = 15  # la pagina indicata nel CSV va vista comunque
    pagine, css_visti, css_testo = [], set(), ""

    def accoda(zuppa, base):
        for u, testo, tag in link_interni(zuppa, base, host):
            if u in visti:
                continue
            p = peso_link(u, testo, tag)
            if u not in candidati or p > candidati[u]:
                candidati[u] = p

    prossimo, r, z = url_pagina(home.url), home, zuppa_home
    while True:
        visti.add(prossimo)
        if r is not None and "html" in r.headers.get("Content-Type", "html"):
            visti.add(url_pagina(r.url))
            accoda(z, r.url)
            for link in z.find_all("link", href=True):
                if "stylesheet" not in " ".join(link.get("rel") or []).lower():
                    continue
                cu = urljoin(r.url, link.get("href", ""))
                if cu and cu not in css_visti and len(css_visti) < 6:
                    css_visti.add(cu)
                    rc = scarica(cu)
                    if rc is not None:
                        css_testo += "\n" + rc.text
            i = len(pagine)
            percorso_url = urlparse(r.url).path.strip("/")
            nome_file = f"{i:02d}-{slug(percorso_url) if percorso_url else 'home'}.html"
            with open(os.path.join(cartella, "sorgente", nome_file), "w", encoding="utf-8") as f:
                f.write(r.text)
            descr = z.find("meta", attrs={"name": re.compile("^description$", re.I)})
            pagine.append({
                "url": r.url,
                "titolo": (z.title.get_text(strip=True) if z.title else "") or
                          (z.h1.get_text(" ", strip=True) if z.h1 else ""),
                "descrizione": (descr.get("content") or "").strip() if descr else "",
                "titoli": [h.get_text(" ", strip=True) for h in z.find_all(["h1", "h2", "h3"]) if h.get_text(strip=True)],
                "righe": righe_testo(z),
                "sorgente": f"sorgente/{nome_file}",
                "_zuppa": z,
            })
            print(f"  [{len(pagine)}] {r.url}", file=sys.stderr)
        da_fare = {u: p for u, p in candidati.items() if u not in visti and p > -10}
        if len(pagine) >= max_pagine or not da_fare:
            break
        prossimo = max(da_fare, key=da_fare.get)
        r = scarica(prossimo)
        z = BeautifulSoup(r.text, "html.parser") if r is not None else None

    # 3. Testi ripetuti su più pagine = menu, intestazioni, footer
    comuni = set()
    if len(pagine) >= 3:
        conta = Counter(r for p in pagine for r in set(p["righe"]))
        comuni = {r for r, c in conta.items() if c >= max(2, int(len(pagine) * 0.6))}
    for p in pagine:
        p["testo"] = [r for r in p["righe"] if r not in comuni]

    # 4. Contatti e social
    tutto = "\n".join("\n".join(p["righe"]) for p in pagine)
    email = []
    for p in pagine:
        email += [unquote(a["href"][7:]).split("?")[0].strip() for a in p["_zuppa"].select('a[href^="mailto:"]')]
    email += EMAIL.findall(tutto)
    email = list(dict.fromkeys(e.lower() for e in email
                               if EMAIL.fullmatch(e) and "example." not in e.lower()
                               and not e.lower().endswith((".png", ".jpg", ".gif"))))
    telefoni = []
    for p in pagine:
        telefoni += [unquote(a["href"][4:]) for a in p["_zuppa"].select('a[href^="tel:"]')]
    telefoni += TELEFONO.findall(tutto)
    telefoni = list(dict.fromkeys(t for t in (pulisci_tel(x) for x in telefoni) if t))
    piva = list(dict.fromkeys(PIVA.findall(tutto)))
    indirizzi = []
    tutto_righe_unite = " ".join(r for p in pagine for r in p["righe"])
    for m in INDIRIZZO.findall(tutto) + INDIRIZZO.findall(tutto_righe_unite):
        m = re.split(r"\s[-–|]\s*(?:tel|fax|cell|p\.?\s?iva|c\.?f\.|e-?mail)|\b(?:tel|fax)\.?\s*[:\d+]", m, flags=re.I)[0]
        m = re.sub(r"\s+", " ", m).strip(" -–,|")
        if m and m not in indirizzi:
            indirizzi.append(m)
    indirizzi = indirizzi[:3]
    social = sorted({a["href"].split("?")[0] for p in pagine for a in p["_zuppa"].find_all("a", href=True)
                     if any(s in a["href"] for s in SOCIAL)})

    # 5. Immagini: prima i loghi, poi a turno un'immagine per pagina (così ogni sezione
    #    è rappresentata), gli sfondi del foglio di stile per ultimi e al massimo 8.
    loghi = []
    for p in pagine[:3]:  # il logo sta in testata: basta guardare le prime pagine (e i frame)
        loghi += candidati_logo(p["_zuppa"], p["url"], home.url)
    loghi = list(dict.fromkeys(loghi))
    visti = set(loghi)
    tutte_img = [{"url": lg, "alt": "logo", "origine": "logo", "pagina": home.url} for lg in loghi]
    code = []
    for p in pagine:
        coda = []
        for im in immagini_pagina(p["_zuppa"], p["url"]):
            if im["url"] not in visti:
                visti.add(im["url"])
                im["pagina"] = p["url"]
                coda.append(im)
        code.append(coda)
    while any(code):
        for coda in code:
            if coda:
                tutte_img.append(coda.pop(0))
    sfondi = [im for im in immagini_pagina(BeautifulSoup("", "html.parser"), home.url, css_testo)
              if im["url"] not in visti]
    for im in sfondi[:8]:
        im["pagina"] = home.url
        tutte_img.append(im)

    scaricate, hash_visti = [], set()
    for im in tutte_img:
        if len(scaricate) >= MAX_IMMAGINI:
            break
        r = scarica(im["url"], binario=True)
        if r is None:
            continue
        dati = r.content
        e_logo = im["url"] in loghi
        if len(dati) < MIN_BYTE_IMMAGINE and not e_logo:
            continue
        h = hashlib.md5(dati).hexdigest()
        if h in hash_visti:
            continue
        hash_visti.add(h)
        est = os.path.splitext(urlparse(im["url"]).path)[1].lower()
        if est not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp"):
            tipo = r.headers.get("Content-Type", "")
            est = ".svg" if "svg" in tipo else ".png" if "png" in tipo else ".jpg"
        base = slug(os.path.splitext(os.path.basename(urlparse(im["url"]).path))[0]) or "immagine"
        nome_img = f"{'logo-' if e_logo else ''}{len(scaricate) + 1:02d}-{base}{est}"
        percorso = os.path.join(cartella, "img", nome_img)
        with open(percorso, "wb") as f:
            f.write(dati)
        dim = dimensioni(percorso) if est != ".svg" else None
        scaricate.append({
            "file": f"img/{nome_img}", "url": im["url"], "alt": im["alt"], "origine": im["origine"],
            "pagina": im["pagina"], "kb": round(len(dati) / 1024), "logo": e_logo,
            "larghezza": dim[0] if dim else None, "altezza": dim[1] if dim else None,
            "bassa_risoluzione": bool(dim and max(dim) < BASSA_RISOLUZIONE and not e_logo),
        })

    # 6. Colori: dal CSS/HTML e dal logo
    conta_colori = Counter(colori_da_testo(css_testo))
    for p in pagine:
        conta_colori.update(colori_html(p["_zuppa"]))
    palette_sito = [c for c, _ in conta_colori.most_common() if not e_neutro(c)][:6]
    neutri = [c for c, _ in conta_colori.most_common() if e_neutro(c)][:3]
    logo_file = next((i for i in scaricate if i["logo"] and not i["file"].endswith((".ico", ".svg"))), None)
    palette_logo = palette_immagine(os.path.join(cartella, logo_file["file"])) if logo_file else []

    # 7. Salvataggio
    for p in pagine:
        p.pop("_zuppa", None)
        p.pop("righe", None)
    dati = {
        "nome": nome, "sito": home.url, "analizzato_il": datetime.date.today().isoformat(),
        "prospect": riga_csv or {},
        "contatti": {"email": email, "telefoni": telefoni, "piva": piva, "indirizzi": indirizzi, "social": social},
        "colori": {"sito": palette_sito, "neutri": neutri, "logo": palette_logo},
        "testi_comuni": sorted(comuni),
        "pagine": pagine,
        "immagini": scaricate,
    }
    with open(os.path.join(cartella, "contenuti.json"), "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)
    with open(os.path.join(cartella, "contenuti.md"), "w", encoding="utf-8") as f:
        f.write(markdown(dati))

    print(f"\n{len(pagine)} pagine, {len(scaricate)} immagini "
          f"({sum(1 for i in scaricate if i['logo'])} logo), {len(palette_sito)} colori.", file=sys.stderr)
    rel = os.path.relpath(cartella, os.getcwd())
    print(f"Salvato in: {cartella if rel.startswith('..') else rel}")
    return cartella


def markdown(d):
    c = d["contatti"]
    righe = [f"# {d['nome']}", "", f"Sito analizzato: {d['sito']}  ", f"Data: {d['analizzato_il']}", ""]
    pr = d.get("prospect") or {}
    if pr.get("motivi"):
        righe += [f"**Dallo Scout:** punteggio {pr.get('punteggio', '?')}, priorità {pr.get('priorita', '?')}  ",
                  f"Problemi del sito: {pr['motivi']}", ""]

    righe += ["## Contatti", ""]
    righe += [f"- **Email:** {', '.join(c['email']) or '— non trovata'}",
              f"- **Telefoni:** {', '.join(c['telefoni']) or '— non trovati'}",
              f"- **P.IVA:** {', '.join(c['piva']) or '— non trovata (è obbligatoria in homepage)'}",
              f"- **Indirizzo:** {' / '.join(c['indirizzi']) or '— non trovato'}",
              f"- **Social:** {', '.join(c['social']) or '— nessuno'}", ""]

    col = d["colori"]
    righe += ["## Colori", "",
              f"- **Dal sito:** {' '.join(col['sito']) or '— nessun colore marcato'}",
              f"- **Dal logo:** {' '.join(col['logo']) or '— non ricavati'}",
              f"- **Neutri usati:** {' '.join(col['neutri']) or '—'}", ""]

    loghi = [i for i in d["immagini"] if i["logo"]]
    righe += ["## Logo", ""]
    righe += [f"- `{i['file']}` ({i['kb']} KB" + (f", {i['larghezza']}×{i['altezza']}px" if i['larghezza'] else "") + ")"
              for i in loghi] or ["- Nessun logo trovato: chiederlo al cliente o ricostruirlo dal nome."]
    righe.append("")

    righe += ["## Menu e testi ripetuti (intestazione/footer)", ""]
    righe += [f"- {t}" for t in d["testi_comuni"][:40]] or ["- —"]
    righe.append("")

    righe += ["## Pagine", ""]
    for p in d["pagine"]:
        righe += [f"### {p['titolo'] or p['url']}", "", f"URL: {p['url']}  ", f"Sorgente: `{p['sorgente']}`", ""]
        if p["descrizione"]:
            righe += [f"> {p['descrizione']}", ""]
        righe += p["testo"] or ["*(nessun testo proprio: pagina di sole immagini o solo menu)*"]
        righe.append("")

    righe += ["## Immagini", "", "| File | Dimensioni | Alt | Pagina |", "|---|---|---|---|"]
    for i in d["immagini"]:
        dim = f"{i['larghezza']}×{i['altezza']}" if i["larghezza"] else f"{i['kb']} KB"
        if i["bassa_risoluzione"]:
            dim += " ⚠ bassa"
        righe.append(f"| `{i['file']}` | {dim} | {i['alt'] or ''} | {urlparse(i['pagina']).path or '/'} |")
    righe.append("")

    # Note automatiche per il Builder
    note = []
    n_bassa = sum(1 for i in d["immagini"] if i["bassa_risoluzione"])
    n_foto = len([i for i in d["immagini"] if not i["logo"]])
    if not loghi:
        note.append("Nessun logo trovato.")
    if n_foto < 5:
        note.append(f"Solo {n_foto} immagini utilizzabili: servono foto stock o da chiedere al cliente.")
    if n_bassa:
        note.append(f"{n_bassa} immagini a bassa risoluzione (< {BASSA_RISOLUZIONE}px): nella demo vanno usate piccole o sostituite.")
    parole = sum(len(" ".join(p["testo"]).split()) for p in d["pagine"])
    if parole < 300:
        note.append(f"Pochi testi ({parole} parole in tutto): il Builder dovrà scriverne di nuovi partendo da settore e servizi.")
    if not c["piva"]:
        note.append("P.IVA non trovata: cercarla prima di metterla nel footer della demo.")
    righe += ["## Note per il Builder", ""] + ([f"- {n}" for n in note] or ["- Materiale sufficiente per la demo."])
    return "\n".join(righe) + "\n"


# ---------------------------------------------------------------- CLI

def leggi_csv(percorso):
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        campione = f.read(4096)
        f.seek(0)
        sep = ";" if campione.count(";") >= campione.count(",") else ","
        return [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
                for r in csv.DictReader(f, delimiter=sep)]


def main():
    p = argparse.ArgumentParser(description="Analista: estrae i contenuti dal sito di un prospect.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("analizza", help="Analizza un sito dato l'indirizzo")
    s1.add_argument("url")
    s1.add_argument("--nome", help="Nome dell'azienda (decide il nome della cartella)")

    s2 = sub.add_parser("da-csv", help="Analizza prospect presi da un CSV dello Scout")
    s2.add_argument("csv")
    g = s2.add_mutually_exclusive_group(required=True)
    g.add_argument("--nome", help="Nome esatto (o parte del nome) dell'azienda nel CSV")
    g.add_argument("--primi", type=int, help="Analizza i primi N prospect con un sito da analizzare")

    for s in (s1, s2):
        s.add_argument("--max-pagine", type=int, default=10)
        s.add_argument("--cartella", default=None, help="Dove creare le cartelle clienti (predefinito: clienti/)")

    a = p.parse_args()
    if a.cmd == "analizza":
        analizza(a.url, a.nome, a.max_pagine, a.cartella)
        return

    righe = leggi_csv(a.csv)
    analizzabili = ("ALTA", "MEDIA", "BASSA", "VERIFICA")
    if a.nome:
        scelte = [r for r in righe if a.nome.lower() in r.get("nome", "").lower()]
        if not scelte:
            sys.exit(f"Nessuna azienda con nome '{a.nome}' nel CSV.")
    else:
        scelte = [r for r in righe if r.get("priorita") in analizzabili][: a.primi]
    for r in scelte:
        if r.get("priorita") not in analizzabili:
            print(f"Salto {r.get('nome')}: priorità {r.get('priorita')}, non c'è un sito proprio da analizzare.\n"
                  "Per la demo raccogli a mano i contenuti dalla scheda (Booking, Google, Facebook).")
            continue
        analizza(r.get("sito"), r.get("nome"), a.max_pagine, a.cartella, riga_csv=r)
        print()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ProxyError as e:
        sys.exit(f"\nErrore di proxy: {e}\nControlla HTTPS_PROXY o il filtro web aziendale.")
    except KeyboardInterrupt:
        sys.exit("\nInterrotto.")
