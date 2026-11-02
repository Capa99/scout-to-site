#!/usr/bin/env python3
"""
Scout - trova aziende con siti web vecchi e da' a ciascun sito un punteggio.

Comandi:
  python scout.py scopri  --comune Vigevano -o prospect/vigevano-grezzo.csv
  python scout.py valuta  prospect/vigevano-grezzo.csv -o prospect/vigevano-valutati.csv
  python scout.py tutto   --comune Vigevano -o prospect/vigevano-valutati.csv

Funziona su Windows, macOS e Linux. Dietro proxy aziendale usa le variabili
HTTPS_PROXY / HTTP_PROXY e, se installato, il pacchetto "truststore" per
fidarsi dei certificati di sistema (utile con l'ispezione SSL aziendale).
"""
import argparse
import csv
import datetime
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote, urlparse

# Certificati di sistema (Windows/macOS): risolve gli errori SSL dietro proxy aziendale.
try:
    import truststore  # type: ignore

    truststore.inject_into_ssl()
except Exception:
    pass

import requests
from bs4 import BeautifulSoup

# Console Windows: evita errori con accenti e simboli.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
OVERPASS_SERVER = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
PAGESPEED = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
ANNO = datetime.date.today().year
TIMEOUT = (6, 15)  # connessione, lettura

CAMPI_INPUT = ["nome", "sito", "categoria", "comune", "telefono"]
CAMPI_OUTPUT = [
    "punteggio", "priorita", "nome", "sito", "categoria", "comune", "telefono",
    "email", "motivi", "anno_copyright", "https", "mobile", "generator",
    "jquery", "tempo_s", "pagespeed_mobile",
]

SOCIAL = (
    "facebook.com", "fb.com", "instagram.com", "linkedin.com", "tiktok.com",
    "twitter.com", "x.com", "youtube.com",
)
DIRECTORY = (
    "paginegialle.it", "paginebianche.it", "google.com", "goo.gl",
    "tripadvisor.", "booking.com", "thefork.", "just-eat.", "deliveroo.",
    "glovoapp.", "subito.it", "virgilio.it", "wikipedia.org",
)

PARCHEGGIATO = re.compile(
    r"(domain (is )?for sale|dominio (e |è )?in vendita|questo dominio|"
    r"this domain (has been|is) (registered|parked)|parked (free|domain)|"
    r"sito in costruzione|work in progress|under construction|coming soon|"
    r"account suspended|default web site page|apache2? .*default page|"
    r"it works!|welcome to nginx|index of /)",
    re.I,
)
COPYRIGHT = re.compile(
    r"(?:©|&copy;|\(c\)|copyright|tutti i diritti riservati|all rights reserved)"
    r"[^0-9]{0,60}((?:19|20)\d{2})(?:\s*[-–/]\s*((?:19|20)\d{2}))?",
    re.I,
)
PIVA = re.compile(r"(p\.?\s?i\.?v\.?a\.?|partita\s+iva|c\.?f\.?\s*/\s*p\.?\s?iva|vat)[^0-9]{0,25}(it)?\s?\d{11}", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TELEFONO = re.compile(r"(?<![\d])(?:\+39[\s.]?)?(?:0\d{1,3}|3\d{2})[\s./-]?\d{3,4}[\s.-]?\d{2,4}(?![\d])")
JQUERY_SRC = re.compile(r"jquery(?:[.-]min)?[.-]v?(\d)\.(\d+)", re.I)
JQUERY_VER = re.compile(r"jquery[^\"'?]*\.js\?ver=(\d)\.(\d+)", re.I)
JQUERY_BANNER = re.compile(r"jQuery (?:JavaScript Library )?v(\d)\.(\d+)", re.I)
GENERATORI_VECCHI = re.compile(
    r"(frontpage|dreamweaver|iweb|microsoft word|publisher|netobjects|"
    r"homestead|golive|joomla! 1\.|joomla! 2\.|website x5 (evolution|v?[1-9]\b))",
    re.I,
)

ESCLUDI_AMENITY = {
    "school", "townhall", "place_of_worship", "police", "hospital", "library",
    "university", "kindergarten", "post_office", "bank", "fuel", "atm",
    "fire_station", "courthouse", "prison", "social_facility", "college",
    "community_centre", "parking", "toilets", "grave_yard", "public_building",
}
CHIAVI_CATEGORIA = [
    "craft", "office", "industrial", "shop", "amenity", "tourism",
    "healthcare", "leisure", "man_made", "company",
]

_sessione = None


def sessione():
    global _sessione
    if _sessione is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9"})
        # requests legge da solo HTTPS_PROXY / HTTP_PROXY / NO_PROXY.
        _sessione = s
    return _sessione


# ---------------------------------------------------------------- utilità

def normalizza_url(u):
    u = (u or "").strip().strip("/")
    if not u:
        return ""
    if not re.match(r"^https?://", u, re.I):
        u = "http://" + u
    return u


def pulisci_tel(t):
    """Tiene solo numeri italiani plausibili (fisso 0..., cellulare 3...), altrimenti ''."""
    t = (t or "").split(";")[0].strip()
    cifre = re.sub(r"\D", "", t)
    if cifre.startswith("0039"):
        cifre = cifre[4:]
    elif cifre.startswith("39") and len(cifre) >= 11:
        cifre = cifre[2:]
    if cifre.startswith("0") and 6 <= len(cifre) <= 10:  # 11 cifre = probabile P.IVA
        return "+39 " + cifre
    if cifre.startswith("3") and len(cifre) == 10:
        return "+39 " + cifre
    return ""


def dominio(u):
    host = urlparse(normalizza_url(u)).netloc.lower()
    host = host.split("@")[-1]
    return host[4:] if host.startswith("www.") else host


def leggi_csv(percorso):
    with open(percorso, encoding="utf-8-sig", newline="") as f:
        campione = f.read(4096)
        f.seek(0)
        sep = ";" if campione.count(";") >= campione.count(",") else ","
        return [
            {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            for r in csv.DictReader(f, delimiter=sep)
        ]


def chiave(riga):
    """Identifica un'azienda: dominio del sito, oppure il nome se non ha sito."""
    d = dominio(riga.get("sito", ""))
    if d and not any(d == s or d.endswith("." + s) for s in SOCIAL):
        return d
    return "nome:" + re.sub(r"\W+", " ", (riga.get("nome") or "").lower()).strip()


def esistenti(percorso):
    """Righe già presenti nel file di output (lista vuota se il file non c'è)."""
    if percorso and os.path.exists(percorso):
        return leggi_csv(percorso)
    return []


def scrivi_csv(percorso, righe, campi, vecchie=None):
    """Scrive il CSV. Con 'vecchie' aggiunge in coda solo le righe nuove, senza doppioni,
    e mantiene le colonne aggiunte a mano (note, chiamato, ...)."""
    vecchie = vecchie or []
    visti = {chiave(r) for r in vecchie}
    nuove = []
    for r in righe:
        k = chiave(r)
        if k not in visti:
            visti.add(k)
            nuove.append(r)

    oggi = datetime.date.today().isoformat()
    for r in nuove:
        r.setdefault("trovato_il", oggi)
    tutte = vecchie + nuove
    if "punteggio" in campi:
        tutte.sort(key=lambda x: int(x.get("punteggio") or 0), reverse=True)

    colonne = list(campi) + ["trovato_il"]
    for r in vecchie:  # colonne extra create dall'utente
        for c in r:
            if c and c not in colonne:
                colonne.append(c)

    cartella = os.path.dirname(percorso)
    if cartella:
        os.makedirs(cartella, exist_ok=True)
    try:
        # ";" + BOM: Excel in italiano lo apre correttamente; Google Sheets lo importa.
        with open(percorso, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colonne, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(tutte)
    except PermissionError:
        sys.exit(f"\nNon riesco a scrivere {percorso}: è aperto in Excel? Chiudilo e rilancia.")
    print(f"\n{len(nuove)} aziende nuove aggiunte, {len(vecchie)} già presenti, totale {len(tutte)}.")
    return tutte


# ---------------------------------------------------------------- scoperta

def scopri(comune, tipi=None, includi_catene=False):
    """Cerca su OpenStreetMap le attività di un comune che hanno un sito web."""
    comune_q = comune.replace('"', '\\"')
    query = f"""
[out:json][timeout:120];
area["ISO3166-1"="IT"]["admin_level"="2"]->.it;
rel(area.it)["boundary"="administrative"]["admin_level"="8"]["name"="{comune_q}"];
map_to_area->.a;
(
  nwr(area.a)["website"];
  nwr(area.a)["contact:website"];
  nwr(area.a)["url"];
);
out tags center;
"""
    print(f"Cerco su OpenStreetMap le attività di {comune} con un sito...", file=sys.stderr)
    # Overpass rifiuta (406) gli User-Agent generici da browser o "python-requests":
    # vuole un nome di programma riconoscibile.
    intestazioni = {
        "User-Agent": os.environ.get("OVERPASS_UA", "ScoutSitiLocali/1.1 (script personale, Python requests)"),
        "Referer": "https://overpass-turbo.eu/",
        "Accept": "*/*",
    }
    elementi, ultimo_errore = None, None
    for server in OVERPASS_SERVER:
        try:
            r = requests.post(server, data={"data": query}, headers=intestazioni, timeout=(10, 180))
            if r.status_code in (406, 429, 502, 503, 504):
                ultimo_errore = f"{server} ha risposto {r.status_code}"
                print(f"  {ultimo_errore}, provo il server successivo...", file=sys.stderr)
                continue
            r.raise_for_status()
            elementi = r.json().get("elements", [])
            break
        except (requests.RequestException, ValueError) as e:
            ultimo_errore = f"{server}: {e}"
            print(f"  {server} non risponde, provo il server successivo...", file=sys.stderr)
    if elementi is None:
        raise requests.RequestException(
            f"Nessun server OpenStreetMap disponibile ({ultimo_errore}). "
            "Riprova tra qualche minuto: non insistere, i server bloccano chi ripete subito."
        )

    righe, visti = [], set()
    for el in elementi:
        t = el.get("tags", {})
        if not includi_catene and (t.get("brand") or t.get("brand:wikidata")):
            continue
        if t.get("amenity") in ESCLUDI_AMENITY:
            continue
        chiave = next((k for k in CHIAVI_CATEGORIA if k in t), None)
        if tipi and chiave not in tipi:
            continue
        sito = t.get("website") or t.get("contact:website") or t.get("url") or ""
        d = dominio(sito)
        if not d or d in visti:
            continue
        visti.add(d)
        righe.append({
            "nome": t.get("name", "(senza nome)"),
            "sito": normalizza_url(sito),
            "categoria": f"{chiave}={t.get(chiave)}" if chiave else "",
            "comune": t.get("addr:city", comune),
            "telefono": t.get("phone") or t.get("contact:phone") or "",
        })
    print(f"Trovate {len(righe)} attività con sito (su {len(elementi)} risultati).", file=sys.stderr)
    return righe


# ---------------------------------------------------------------- valutazione

def _scarica(url):
    t0 = time.time()
    r = sessione().get(url, timeout=TIMEOUT, allow_redirects=True)
    return r, time.time() - t0


def _pagespeed(url, chiave=None):
    params = {"url": url, "strategy": "mobile", "category": "performance"}
    if chiave:
        params["key"] = chiave
    try:
        r = sessione().get(PAGESPEED, params=params, timeout=(10, 90))
        r.raise_for_status()
        return round(r.json()["lighthouseResult"]["categories"]["performance"]["score"] * 100)
    except Exception:
        return None


def valuta_sito(riga, pagespeed=False, chiave_ps=None):
    ris = {k: riga.get(k, "") for k in CAMPI_INPUT}
    motivi, punti = [], 0
    url = normalizza_url(riga.get("sito"))
    ris["sito"] = url

    if not url:
        ris.update(punteggio=95, priorita="SENZA SITO", motivi="Nessun sito indicato")
        return ris
    d = dominio(url)
    if any(d == s or d.endswith("." + s) for s in SOCIAL):
        ris.update(punteggio=80, priorita="SOLO SOCIAL",
                   motivi="Usa un profilo social al posto di un sito")
        return ris
    if any(s in d for s in DIRECTORY):
        ris.update(punteggio=0, priorita="SCARTA",
                   motivi="Il link punta a una directory, non al sito dell'azienda")
        return ris

    host = urlparse(url).netloc
    alt = host[4:] if host.startswith("www.") else "www." + host
    resp, tempo, errore_ssl = None, None, False

    for h in (host, alt):
        try:
            r, t = _scarica(f"https://{h}/")
            if r.status_code < 400:
                resp, tempo = r, t
                break
        except requests.exceptions.SSLError:
            errore_ssl = True
        except requests.RequestException:
            pass
    if resp is None:
        for h in (host, alt):
            try:
                r, t = _scarica(f"http://{h}/")
                if r.status_code < 400:
                    resp, tempo = r, t
                    break
            except requests.RequestException:
                pass

    if resp is None:
        ris.update(punteggio=90, priorita="MORTO",
                   motivi="Sito irraggiungibile: verificare se l'azienda è ancora attiva")
        return ris

    https_ok = resp.url.lower().startswith("https://")
    if https_ok:
        ris["https"] = "sì"
        try:
            rh, _ = _scarica(f"http://{urlparse(resp.url).netloc}/")
            if not rh.url.lower().startswith("https://"):
                punti += 5
                motivi.append("La versione http non reindirizza su https")
        except requests.RequestException:
            pass
    else:
        ris["https"] = "certificato non valido" if errore_ssl else "no"
        punti += 20
        motivi.append("Certificato HTTPS non valido" if errore_ssl
                      else "Niente HTTPS: Chrome lo segna 'Non sicuro'")

    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    html = resp.text
    zuppa = BeautifulSoup(html, "html.parser")
    for s in zuppa(["script", "style", "noscript"]):
        s.extract()
    testo = zuppa.get_text(" ", strip=True)
    zuppa = BeautifulSoup(html, "html.parser")  # di nuovo, completo, per i tag

    if len(testo) < 400 and PARCHEGGIATO.search(testo[:3000] + " " + (zuppa.title.string if zuppa.title and zuppa.title.string else "")):
        ris.update(punteggio=85, priorita="SITO VUOTO",
                   motivi="Dominio parcheggiato o pagina in costruzione", https=ris.get("https", ""))
        return ris

    # Leggibilità da cellulare
    vp = zuppa.find("meta", attrs={"name": re.compile(r"^viewport$", re.I)})
    if not vp or "width" not in (vp.get("content") or "").lower():
        ris["mobile"] = "no"
        punti += 25
        motivi.append("Non pensato per cellulare (manca il viewport)")
    else:
        ris["mobile"] = "sì"

    # Anno del copyright
    anni = []
    for m in COPYRIGHT.finditer(testo):
        anni += [int(a) for a in m.groups() if a and 1990 <= int(a) <= ANNO]
    if anni:
        anno = max(anni)
        ris["anno_copyright"] = anno
        eta = ANNO - anno
        if eta >= 6:
            punti += 20
            motivi.append(f"Copyright fermo al {anno}")
        elif eta >= 3:
            punti += 10
            motivi.append(f"Copyright fermo al {anno}")
        elif eta == 2:
            punti += 5

    # Tecnologie superate
    low = html.lower()
    if ".swf" in low or zuppa.find(["object", "embed"], attrs={"type": re.compile("flash", re.I)}):
        punti += 15
        motivi.append("Usa Flash (non funziona più nei browser)")
    if zuppa.find(["frameset", "frame"]):
        punti += 15
        motivi.append("Costruito con i frame")
    tabelle = [t for t in zuppa.find_all("table")
               if any(a in t.attrs for a in ("width", "bgcolor", "cellpadding", "background"))]
    if len(tabelle) >= 2:
        punti += 10
        motivi.append("Impaginazione a tabelle (stile anni 2000)")
    vecchi = sorted({t.name for t in zuppa.find_all(["font", "center", "marquee", "blink"])})
    if vecchi:
        punti += 10
        motivi.append("Tag HTML obsoleti: " + ", ".join(vecchi))

    m = JQUERY_SRC.search(html) or JQUERY_VER.search(html) or JQUERY_BANNER.search(html)
    if m:
        maj, mnr = int(m.group(1)), int(m.group(2))
        ris["jquery"] = f"{maj}.{mnr}"
        if (maj, mnr) < (1, 9):
            punti += 10
            motivi.append(f"jQuery {maj}.{mnr} molto vecchio")
        elif maj < 3:
            punti += 4

    gen = zuppa.find("meta", attrs={"name": re.compile(r"^generator$", re.I)})
    gen = (gen.get("content") or "").strip() if gen else ""
    ris["generator"] = gen
    if gen:
        wp = re.search(r"wordpress\s+(\d+)\.", gen, re.I)
        if GENERATORI_VECCHI.search(gen) or (wp and int(wp.group(1)) < 5):
            punti += 10
            motivi.append(f"Creato con uno strumento datato ({gen})")

    if not PIVA.search(testo):
        punti += 3
        motivi.append("P.IVA non visibile in homepage (è obbligatoria)")

    ris["tempo_s"] = round(tempo, 1)
    if tempo > 4:
        punti += 5
        motivi.append(f"Lento a rispondere ({tempo:.1f} s)")

    if pagespeed:
        ps = _pagespeed(resp.url, chiave_ps)
        if ps is not None:
            ris["pagespeed_mobile"] = ps
            if ps < 50:
                punti += 10
                motivi.append(f"PageSpeed mobile {ps}/100")

    # Contatti (solo dati aziendali pubblici in homepage)
    mail = [unquote(a["href"][7:]).split("?")[0].strip() for a in zuppa.select('a[href^="mailto:"]')]
    mail += EMAIL.findall(testo)
    mail = [e for e in mail if EMAIL.fullmatch(e) and not e.lower().endswith((".png", ".jpg", ".gif", ".webp"))]
    ris["email"] = mail[0] if mail else ""
    tel_osm = pulisci_tel(ris["telefono"])
    if tel_osm:
        ris["telefono"] = tel_osm
    else:
        candidati = [unquote(a["href"][4:]) for a in zuppa.select('a[href^="tel:"]')]
        candidati += TELEFONO.findall(testo)
        validi = [t for t in (pulisci_tel(c) for c in candidati) if t]
        ris["telefono"] = validi[0] if validi else ""

    punti = min(punti, 100)
    ris["punteggio"] = punti
    ris["priorita"] = "ALTA" if punti >= 60 else "MEDIA" if punti >= 35 else "BASSA"
    ris["motivi"] = " | ".join(motivi) or "Sito in buono stato"
    return ris


def valuta(righe, paralleli=8, pagespeed=False, chiave_ps=None):
    # Elimina doppioni per dominio
    uniche, visti = [], set()
    for r in righe:
        d = dominio(r.get("sito", "")) or r.get("nome", "")
        if d not in visti:
            visti.add(d)
            uniche.append(r)

    risultati = []
    with ThreadPoolExecutor(max_workers=paralleli) as ex:
        futuri = {ex.submit(valuta_sito, r, pagespeed, chiave_ps): r for r in uniche}
        for i, f in enumerate(as_completed(futuri), 1):
            r = futuri[f]
            try:
                risultati.append(f.result())
            except Exception as e:  # un sito strano non deve fermare tutto
                base = {k: r.get(k, "") for k in CAMPI_INPUT}
                base.update(punteggio=0, priorita="ERRORE", motivi=f"Errore: {e}")
                risultati.append(base)
            print(f"  [{i}/{len(uniche)}] {r.get('nome', '')}", file=sys.stderr)
    risultati.sort(key=lambda x: int(x.get("punteggio") or 0), reverse=True)
    return risultati


def riepilogo(risultati, n=15):
    print("\nMigliori prospect:")
    for r in risultati[:n]:
        print(f"  {str(r['punteggio']).rjust(3)}  {r['priorita']:<11} {r['nome'][:35]:<35} {r['sito']}")
    conta = {}
    for r in risultati:
        conta[r["priorita"]] = conta.get(r["priorita"], 0) + 1
    print("\nTotale per priorità: " + ", ".join(f"{k} {v}" for k, v in sorted(conta.items())))


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description="Scout: trova aziende con siti web vecchi.")
    sub = p.add_subparsers(dest="cmd", required=True)

    def opzioni_scoperta(sp):
        sp.add_argument("--comune", required=True, help='Es. "Vigevano"')
        sp.add_argument("--tipi", default="",
                        help="Filtra per tipo OSM, separati da virgola: craft,office,industrial,shop,amenity,...")
        sp.add_argument("--catene", action="store_true", help="Includi catene e franchising")
        sp.add_argument("--sovrascrivi", action="store_true",
                        help="Riscrive il file da zero invece di aggiungere le aziende nuove")

    def opzioni_valutazione(sp):
        sp.add_argument("--paralleli", type=int, default=8)
        sp.add_argument("--pagespeed", action="store_true", help="Aggiungi il punteggio PageSpeed (più lento)")
        sp.add_argument("--min", type=int, default=0, help="Tieni solo i siti con punteggio >= min")

    s1 = sub.add_parser("scopri", help="Trova attività con sito in un comune")
    opzioni_scoperta(s1)
    s1.add_argument("-o", "--output", required=True)

    s2 = sub.add_parser("valuta", help="Dà un punteggio ai siti di un CSV")
    s2.add_argument("input")
    s2.add_argument("-o", "--output", required=True)
    s2.add_argument("--sovrascrivi", action="store_true",
                    help="Riscrive il file da zero invece di aggiungere le aziende nuove")
    opzioni_valutazione(s2)

    s3 = sub.add_parser("tutto", help="scopri + valuta in un colpo")
    opzioni_scoperta(s3)
    s3.add_argument("-o", "--output", required=True)
    opzioni_valutazione(s3)

    a = p.parse_args()
    tipi = {t.strip() for t in getattr(a, "tipi", "").split(",") if t.strip()} or None

    vecchie = [] if a.sovrascrivi else esistenti(a.output)
    gia = {chiave(r) for r in vecchie}

    if a.cmd == "scopri":
        righe = scopri(a.comune, tipi, a.catene)
        scrivi_csv(a.output, righe, CAMPI_INPUT, vecchie)
        print(f"Salvato: {a.output}")
        return

    righe = leggi_csv(a.input) if a.cmd == "valuta" else scopri(a.comune, tipi, a.catene)
    da_valutare = [r for r in righe if chiave(r) not in gia]
    if vecchie:
        print(f"{len(righe) - len(da_valutare)} aziende già nel file: le salto.", file=sys.stderr)
    chiave_ps = os.environ.get("PAGESPEED_API_KEY")
    risultati = valuta(da_valutare, a.paralleli, a.pagespeed, chiave_ps)
    risultati = [r for r in risultati if int(r.get("punteggio") or 0) >= a.min]
    tutte = scrivi_csv(a.output, risultati, CAMPI_OUTPUT, vecchie)
    if vecchie:
        print("\nNuove trovate in questo giro:", end="")
    riepilogo(risultati)
    if vecchie:
        print(f"(Nel file in totale: {len(tutte)} aziende.)")
    print(f"\nSalvato: {a.output}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ProxyError as e:
        sys.exit(f"\nErrore di proxy: {e}\nSe sei sulla rete aziendale, controlla HTTPS_PROXY "
                 "(vedi README) o se il sito è bloccato dal filtro web.")
    except requests.exceptions.SSLError as e:
        sys.exit(f"\nErrore certificati: {e}\nInstalla 'truststore' (pip install truststore): "
                 "fa usare a Python i certificati di Windows, inclusi quelli del proxy aziendale.")
    except requests.RequestException as e:
        sys.exit(f"\nErrore di rete: {e}")
    except KeyboardInterrupt:
        sys.exit("\nInterrotto.")
