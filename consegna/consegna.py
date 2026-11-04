#!/usr/bin/env python3
"""
Consegna - dal "sì" del cliente al sito online sul suo dominio.

Comandi (dalla cartella principale del progetto):
  python consegna/consegna.py avvia clienti/sugar-s-a-s
  python consegna/consegna.py accordo clienti/sugar-s-a-s
  python consegna/consegna.py ricevuta clienti/sugar-s-a-s --tipo acconto
  python consegna/consegna.py ricevuta clienti/sugar-s-a-s --tipo saldo
  python consegna/consegna.py riepilogo
  python consegna/consegna.py produzione clienti/sugar-s-a-s --dominio www.domoadami.com
  python consegna/consegna.py verifica clienti/sugar-s-a-s
  python consegna/consegna.py repo clienti/sugar-s-a-s
  python consegna/consegna.py dns www.domoadami.com --salva clienti/sugar-s-a-s
  python consegna/consegna.py documento clienti/sugar-s-a-s

File:
  consegna/dati-personali.txt        i tuoi dati per le ricevute (NON va su GitHub)
  consegna/registro-ricevute.csv     numerazione e totali delle ricevute
  clienti/<azienda>/consegna/        cliente.txt, accordo, ricevute, foto DNS, documento di consegna
  ../siti-clienti/sito-<azienda>/    il sito definitivo (repo separato, collegato a Netlify)

Niente parte da solo: accordo, ricevute e documento sono bozze che l'utente legge e invia.
"""
import argparse
import csv
import datetime
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlparse

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUI = os.path.join(RADICE, "consegna")
MODELLI = os.path.join(QUI, "modelli")
DATI_PERSONALI = os.path.join(QUI, "dati-personali.txt")
REGISTRO_RICEVUTE = os.path.join(QUI, "registro-ricevute.csv")
CAMPI_RICEVUTE = ["numero", "data", "cliente", "cartella", "tipo", "descrizione", "lordo", "ritenuta", "netto",
                  "file", "incassato_il"]
SITI_CLIENTI = os.path.join(os.path.dirname(RADICE), "siti-clienti")
SOGLIA_INPS = 5000.0
SOGLIA_BOLLO = 77.47
NETLIFY_IP = "75.2.60.5"  # IP del load balancer Netlify per il dominio "nudo" (record A)


# ---------------------------------------------------------------- utilità

def oggi():
    return datetime.date.today()


def euro(x):
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {s}"


def numero(testo):
    s = str(testo).replace("€", "").strip()
    if "," in s:  # formato italiano 1.234,50
        s = s.replace(".", "").replace(",", ".")
    return float(s or 0)


def cartella_cliente(percorso):
    p = os.path.abspath(percorso)
    if not os.path.isdir(p):
        alt = os.path.join(RADICE, "clienti", percorso)
        if os.path.isdir(alt):
            return alt
        sys.exit(f"Cartella cliente non trovata: {percorso}")
    return p


def slug(cliente):
    return os.path.basename(os.path.normpath(cliente))


def cartella_consegna(cliente):
    d = os.path.join(cliente, "consegna")
    os.makedirs(d, exist_ok=True)
    return d


def leggi_kv(percorso):
    dati = {}
    if not os.path.exists(percorso):
        return dati
    for riga in open(percorso, encoding="utf-8-sig"):
        riga = riga.strip()
        if not riga or riga.startswith("#") or "=" not in riga:
            continue
        k, _, v = riga.partition("=")
        dati[k.strip()] = v.strip()
    return dati


def modello(nome):
    return open(os.path.join(MODELLI, nome), encoding="utf-8").read()


def riempi(testo, valori):
    def sost(m):
        k = m.group(1).strip()
        return str(valori.get(k, m.group(0)))
    return re.sub(r"\{\{\s*([a-z_]+)\s*\}\}", sost, testo)


def rel(p):
    try:
        return os.path.relpath(p, os.getcwd())
    except ValueError:
        return p


def scrivi(percorso, testo):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


# ---------------------------------------------------------------- dati cliente

CAMPI_CLIENTE = [
    ("ragione_sociale", "Nome legale dell'azienda (come in visura / fattura)"),
    ("nome_commerciale", "Nome con cui è conosciuta (insegna, marchio)"),
    ("indirizzo", "Sede legale: via, numero, CAP, comune, provincia"),
    ("piva", "Partita IVA"),
    ("cf", "Codice fiscale dell'azienda (spesso uguale alla P.IVA)"),
    ("referente", "Nome e cognome di chi firma / decide"),
    ("email", "Email a cui mandi accordo e ricevute"),
    ("telefono", "Telefono del referente"),
    ("sostituto_imposta", "si = azienda o professionista (trattiene il 20%); no = privato"),
    ("dominio", "Dominio definitivo, es. www.domoadami.com"),
    ("registrar_dominio", "Dove è registrato il dominio (Aruba, Register.it, ...) e chi ha l'accesso"),
    ("email_sul_dominio", "si se usano email @dominio (in quel caso NON toccare i record MX)"),
    ("prezzo", "Prezzo concordato in euro (listino: 590)"),
    ("acconto_percento", "Percentuale di acconto (listino: 50)"),
    ("pagine", "Pagine del sito definitivo, separate da virgola"),
    ("link_demo", "Link della demo approvata"),
    ("verificato", "Metti si solo dopo aver controllato TUTTI i campi con il cliente"),
]


def leggi_cliente(cliente, serve_verificato=True):
    p = os.path.join(cliente, "consegna", "cliente.txt")
    if not os.path.exists(p):
        sys.exit(f"Manca {rel(p)}: lancia prima  consegna.py avvia {rel(cliente)}")
    d = leggi_kv(p)
    if serve_verificato and d.get("verificato", "").lower() not in ("si", "sì", "yes"):
        sys.exit(f"In {rel(p)} manca  verificato=si.\n"
                 "Controlla i dati con il cliente (ragione sociale, P.IVA, indirizzo, sostituto d'imposta)\n"
                 "e solo dopo metti verificato=si.")
    return d


def demo_pagine(cliente):
    demo = os.path.join(cliente, "demo")
    return sorted(f for f in os.listdir(demo) if f.endswith(".html")) if os.path.isdir(demo) else []


def trova_link_demo(cliente):
    for f in sorted(glob.glob(os.path.join(cliente, "outreach", "**", "*.md"), recursive=True)):
        m = re.search(r"https://[a-z0-9-]+\.netlify\.app/?", open(f, encoding="utf-8").read())
        if m:
            return m.group(0)
    return ""


def avvia(cliente):
    dest = os.path.join(cartella_consegna(cliente), "cliente.txt")
    if os.path.exists(dest):
        print(f"{rel(dest)} esiste già: lo lascio com'è.")
    else:
        info = {}
        pj = os.path.join(cliente, "contenuti.json")
        if os.path.exists(pj):
            info = json.load(open(pj, encoding="utf-8"))
        contatti = info.get("contatti", {})
        sito = info.get("sito", "")
        host = urlparse(sito).hostname or ""
        valori = {
            "ragione_sociale": info.get("nome", ""),
            "indirizzo": (contatti.get("indirizzi") or [""])[0],
            "piva": (contatti.get("piva") or [""])[0],
            "cf": (contatti.get("piva") or [""])[0],
            "email": (contatti.get("email") or [""])[0],
            "telefono": (contatti.get("telefoni") or [""])[0],
            "sostituto_imposta": "si",
            "dominio": host if host.startswith("www.") else (f"www.{host}" if host else ""),
            "email_sul_dominio": "si" if host and any(host.replace("www.", "") in e
                                                       for e in contatti.get("email", [])) else "",
            "prezzo": "590",
            "acconto_percento": "50",
            "pagine": ", ".join(["homepage"] + [p.replace(".html", "") for p in demo_pagine(cliente)
                                                 if p != "index.html"] + ["privacy e cookie"]),
            "link_demo": trova_link_demo(cliente),
            "verificato": "no",
        }
        righe = ["# Dati del cliente per accordo, ricevute e messa online.",
                 "# Precompilati dall'Analista: CONTROLLALI TUTTI con il cliente, poi metti verificato=si.", ""]
        for k, spiega in CAMPI_CLIENTE:
            righe += [f"# {spiega}", f"{k}={valori.get(k, '')}", ""]
        scrivi(dest, "\n".join(righe))
        print(f"Creato {rel(dest)} (precompilato: da verificare).")

    lista = os.path.join(cliente, "consegna", "checklist.md")
    if not os.path.exists(lista):
        scrivi(lista, riempi(modello("checklist.md"), {"cliente": slug(cliente), "data": oggi().isoformat()}))
        print(f"Creato {rel(lista)}")
    print("\nProssimo passo: verifica cliente.txt con il cliente, poi  consegna.py accordo", rel(cliente))


# ---------------------------------------------------------------- accordo

def prestatore(serve=True):
    d = leggi_kv(DATI_PERSONALI)
    mancanti = [k for k in ("nome", "codice_fiscale", "indirizzo", "iban") if not d.get(k)]
    if serve and mancanti:
        sys.exit(f"Compila {rel(DATI_PERSONALI)} (copia dati-personali.esempio.txt). Mancano: {', '.join(mancanti)}")
    return d


def accordo(cliente):
    c = leggi_cliente(cliente)
    io = prestatore()
    prezzo = numero(c.get("prezzo", "590"))
    perc = numero(c.get("acconto_percento", "50"))
    acconto = round(prezzo * perc / 100, 2)
    ha_piva = bool(io.get("partita_iva"))
    if ha_piva:
        hosting = ("Canone: 15 € al mese per hosting, rinnovo del dominio, certificato HTTPS "
                   "e backup. Le modifiche non sono incluse nel canone.")
        fiscale = "Importi soggetti al regime fiscale indicato in fattura."
    else:
        hosting = ("Nessun canone. Il dominio è registrato e pagato direttamente da voi presso il vostro "
                   "fornitore. Il sito è ospitato su Netlify, piano gratuito, senza costi per voi. "
                   "Se in futuro servirà un servizio di gestione continuativa, ve lo proporrò a parte.")
        fiscale = ("Prestazione di lavoro autonomo occasionale, fuori campo IVA (art. 5 DPR 633/1972)."
                   + (" Essendo sostituto d'imposta, trattenete la ritenuta d'acconto del 20% e la versate "
                      "con F24; il bonifico è quindi dell'80% di ogni importo."
                      if c.get("sostituto_imposta", "si").lower().startswith("s") else ""))
    pagine = [p.strip() for p in c.get("pagine", "").split(",") if p.strip()]
    valori = c | {
        "data": oggi().strftime("%d/%m/%Y"),
        "prestatore_nome": io["nome"], "prestatore_email": io.get("email", ""),
        "prestatore_telefono": io.get("telefono", ""),
        "prezzo": euro(prezzo), "acconto": euro(acconto), "saldo": euro(prezzo - acconto),
        "acconto_percento": f"{perc:g}", "saldo_percento": f"{100 - perc:g}",
        "elenco_pagine": "\n".join(f"- {p}" for p in pagine),
        "hosting": hosting, "fiscale": fiscale,
        "nome_commerciale": c.get("nome_commerciale") or c.get("ragione_sociale", ""),
        "saluto": f"Buongiorno {c['referente']}" if c.get("referente") else "Buongiorno",
    }
    dest = os.path.join(cartella_consegna(cliente), f"accordo-{oggi().isoformat()}.md")
    if os.path.exists(dest):
        sys.exit(f"{rel(dest)} esiste già: modificalo a mano o cancellalo per rigenerarlo.")
    scrivi(dest, riempi(modello("accordo.md"), valori))
    print(f"Bozza accordo: {rel(dest)}  (Stato: bozza)")
    print("Va letta e approvata dall'utente, poi si invia come email (outreach.py gmail).")


# ---------------------------------------------------------------- ricevute

def leggi_ricevute():
    if not os.path.exists(REGISTRO_RICEVUTE):
        return []
    with open(REGISTRO_RICEVUTE, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def scrivi_ricevute(righe):
    with open(REGISTRO_RICEVUTE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI_RICEVUTE, delimiter=";")
        w.writeheader()
        for r in righe:
            w.writerow({k: r.get(k, "") for k in CAMPI_RICEVUTE})


def totale_anno(righe, anno):
    return sum(float(r["lordo"]) for r in righe if r["data"].startswith(str(anno)))


def ricevuta(cliente, tipo, importo=None, descrizione=None):
    c = leggi_cliente(cliente)
    io = prestatore()
    if io.get("partita_iva"):
        sys.exit("Hai indicato una partita IVA in dati-personali.txt: da ora si emette fattura elettronica "
                 "(dal tuo commercialista o dal software della P.IVA), non la ricevuta occasionale.")
    prezzo = numero(c.get("prezzo", "590"))
    perc = numero(c.get("acconto_percento", "50"))
    if importo is None:
        if tipo == "acconto":
            importo = round(prezzo * perc / 100, 2)
        elif tipo == "saldo":
            importo = round(prezzo - prezzo * perc / 100, 2)
        else:
            sys.exit("Per --tipo altro indica --importo e --descrizione.")
    nome_sito = c.get("dominio") or c.get("nome_commerciale") or c["ragione_sociale"]
    if not descrizione:
        descrizione = {
            "acconto": f"Realizzazione del sito web {nome_sito}: acconto del {perc:g}% all'accettazione",
            "saldo": f"Realizzazione del sito web {nome_sito}: saldo alla pubblicazione",
        }.get(tipo, f"Prestazione relativa al sito web {nome_sito}")

    righe = leggi_ricevute()
    anno = oggi().year
    gia = totale_anno(righe, anno)
    if gia + importo > SOGLIA_INPS:
        sys.exit(f"Con questa ricevuta superi {euro(SOGLIA_INPS)} di compensi occasionali nel {anno} "
                 f"({euro(gia + importo)}).\nOltre questa soglia servono i contributi INPS (gestione separata) "
                 "e probabilmente è ora della partita IVA: parlane con il commercialista prima di emetterla.")
    n = 1 + max([int(r["numero"].split("/")[0]) for r in righe if r["numero"].endswith(f"/{anno}")] or [0])
    num = f"{n}/{anno}"
    sostituto = c.get("sostituto_imposta", "si").lower().startswith("s")
    ritenuta = round(importo * 0.20, 2) if sostituto else 0.0
    netto = round(importo - ritenuta, 2)
    bollo = importo > SOGLIA_BOLLO

    valori = {
        "numero": num, "data": oggi().strftime("%d/%m/%Y"), "luogo": io.get("comune", ""),
        "p_nome": io["nome"], "p_cf": io["codice_fiscale"], "p_indirizzo": io["indirizzo"],
        "p_email": io.get("email", ""), "p_telefono": io.get("telefono", ""),
        "p_iban": io["iban"], "p_banca": io.get("intestatario_iban", io["nome"]),
        "c_nome": c["ragione_sociale"], "c_indirizzo": c.get("indirizzo", ""),
        "c_piva": c.get("piva", ""), "c_cf": c.get("cf", "") or c.get("piva", ""),
        "descrizione": html.escape(descrizione),
        "lordo": euro(importo), "ritenuta": euro(ritenuta), "netto": euro(netto),
        "riga_ritenuta": (f"<tr><td>Ritenuta d'acconto 20% (art. 25 DPR 600/1973), a cura del committente</td>"
                          f"<td class='num'>− {euro(ritenuta)}</td></tr>") if sostituto else "",
        "nota_ritenuta": ("La ritenuta d'acconto viene trattenuta e versata dal committente con modello F24 "
                          "(codice tributo 1040)." if sostituto else
                          "Committente privato: nessuna ritenuta d'acconto."),
        "nota_bollo": ("Imposta di bollo di € 2,00 assolta sull'originale (contrassegno n. ____________________)."
                       if bollo else "Importo non superiore a € 77,47: imposta di bollo non dovuta."),
        "anno": str(anno),
    }
    dest_dir = os.path.join(cartella_consegna(cliente), "ricevute")
    nome_file = f"ricevuta-{anno}-{n:02d}-{tipo}.html"
    dest = os.path.join(dest_dir, nome_file)
    scrivi(dest, riempi(modello("ricevuta.html"), valori))
    righe.append({"numero": num, "data": oggi().isoformat(), "cliente": c["ragione_sociale"],
                  "cartella": os.path.relpath(cliente, RADICE).replace("\\", "/"), "tipo": tipo,
                  "descrizione": descrizione, "lordo": f"{importo:.2f}", "ritenuta": f"{ritenuta:.2f}",
                  "netto": f"{netto:.2f}", "file": os.path.relpath(dest, RADICE).replace("\\", "/"),
                  "incassato_il": ""})
    scrivi_ricevute(righe)

    print(f"Ricevuta n. {num}: {rel(dest)}")
    print(f"  Compenso lordo {euro(importo)}"
          + (f" · ritenuta {euro(ritenuta)} · bonifico atteso {euro(netto)}" if sostituto else ""))
    if bollo:
        print("  Sopra 77,47 €: compra una marca da bollo da 2 € (tabaccaio), incollala sull'originale firmato")
        print("  e scrivi il numero del contrassegno sulla ricevuta prima di mandare la scansione.")
    print("  Aprila nel browser → Stampa → Salva come PDF (o stampa, firma e scansiona).")
    clienti_anno = {r["cliente"] for r in righe if r["data"].startswith(str(anno))}
    if len(clienti_anno) >= 3:
        print(f"\n  ! {len(clienti_anno)} clienti diversi quest'anno: l'attività sta diventando abituale. "
              "È il momento di parlare con il commercialista della partita IVA.")
    print(f"\n  Totale compensi occasionali {anno}: {euro(gia + importo)} su {euro(SOGLIA_INPS)}")


def incassato(num, data=None):
    righe = leggi_ricevute()
    for r in righe:
        if r["numero"] == num:
            r["incassato_il"] = data or oggi().isoformat()
            scrivi_ricevute(righe)
            print(f"Ricevuta {num} segnata come incassata il {r['incassato_il']}.")
            return
    sys.exit(f"Ricevuta {num} non trovata nel registro.")


def riepilogo():
    righe = leggi_ricevute()
    if not righe:
        print("Nessuna ricevuta ancora.")
        return
    anni = sorted({r["data"][:4] for r in righe})
    for anno in anni:
        sel = [r for r in righe if r["data"].startswith(anno)]
        print(f"\n{anno}")
        for r in sel:
            stato = f"incassata {r['incassato_il']}" if r["incassato_il"] else "DA INCASSARE"
            print(f"  {r['numero']:>7}  {r['data']}  {r['cliente'][:28]:<28} {r['tipo']:<8} "
                  f"{euro(float(r['lordo'])):>12}  {stato}")
        lordo = sum(float(r["lordo"]) for r in sel)
        rit = sum(float(r["ritenuta"]) for r in sel)
        print(f"  Totale lordo {euro(lordo)} · ritenute già versate dai clienti {euro(rit)} "
              f"· soglia INPS {euro(SOGLIA_INPS)} (restano {euro(max(0, SOGLIA_INPS - lordo))})")
    print("\nNel 730 questi compensi vanno nei 'redditi diversi' (quadro D, rigo D5) con le ritenute: "
          "chiedi le Certificazioni Uniche ai clienti che hanno trattenuto il 20%.")


# ---------------------------------------------------------------- produzione

def dest_sito(cliente, dest=None):
    return os.path.abspath(dest) if dest else os.path.join(SITI_CLIENTI, f"sito-{slug(cliente)}")


def togli_demo(testo):
    testo = re.sub(r'[ \t]*<meta\s+name="robots"[^>]*>\s*\n?', "", testo, flags=re.I)
    testo = re.sub(r'[ \t]*<div class="demo-tag"[^>]*>.*?</div>\s*\n?', "", testo, flags=re.I | re.S)
    return testo


def aggiungi_canonical(testo, url):
    testo = re.sub(r'[ \t]*<link rel="canonical"[^>]*>\s*\n?', "", testo)
    return re.sub(r"(</title>\s*\n)", rf'\1  <link rel="canonical" href="{url}">\n', testo, count=1)


def link_privacy_footer(testo):
    if "privacy.html" in testo:
        return testo
    voce = '<a href="privacy.html">Privacy e cookie</a>'
    nuovo, n = re.subn(r'(<div class="footer-legal">.*?)(\s*</div>)', rf"\1\n        <span>{voce}</span>\2",
                       testo, count=1, flags=re.S)
    if n:
        return nuovo
    return re.sub(r"(\s*</footer>)", rf'\n  <p class="wrap">{voce}</p>\1', testo, count=1)


def pagina_da_scheletro(base, titolo, descrizione, corpo):
    t = re.sub(r"<title>.*?</title>", f"<title>{html.escape(titolo)}</title>", base, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{html.escape(descrizione)}">', t, count=1)
    t = re.sub(r'[ \t]*<link rel="preload"[^>]*>\s*\n?', "", t)
    t = t.replace("</head>", '  <link rel="stylesheet" href="assets/css/legale.css">\n</head>', 1)
    m = re.search(r"<main\b.*?</main>", t, flags=re.S)
    blocco = f'<main id="contenuto" class="legale wrap">\n{corpo}\n  </main>'
    if m:
        return t[:m.start()] + blocco + t[m.end():]
    return re.sub(r"(</header>)", r"\1\n  " + blocco.replace("\\", "\\\\"), t, count=1)


def produzione(cliente, dominio, dest=None, forza=False):
    c = leggi_cliente(cliente)
    demo = os.path.join(cliente, "demo")
    if not demo_pagine(cliente):
        sys.exit("Nessuna pagina nella demo.")
    dominio = dominio or c.get("dominio", "")
    if not dominio:
        sys.exit("Indica --dominio (es. www.domoadami.com) o compila dominio= in cliente.txt")
    dominio = re.sub(r"^https?://", "", dominio).strip("/")
    base_url = f"https://{dominio}/"
    out = dest_sito(cliente, dest)
    if os.path.exists(out) and any(f for f in os.listdir(out) if f != ".git"):
        if not forza:
            sys.exit(f"{out} esiste già (forse il sito è già online e ci sono modifiche).\n"
                     "Usa --forza solo se vuoi rigenerarlo dalla demo: le modifiche fatte lì andrebbero perse.")
        for f in os.listdir(out):
            if f == ".git":
                continue
            p = os.path.join(out, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(out, exist_ok=True)

    salta = {".stile", "immagini.json", "robots.txt", "_headers"}
    for radice, dirs, files in os.walk(demo):
        for f in files:
            if f in salta:
                continue
            src = os.path.join(radice, f)
            dst = os.path.join(out, os.path.relpath(src, demo))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    shutil.copy2(os.path.join(MODELLI, "legale.css"), os.path.join(out, "assets", "css", "legale.css"))

    pagine = sorted(f for f in os.listdir(out) if f.endswith(".html"))
    usa_mappa = usa_form = False
    for pg in pagine:
        p = os.path.join(out, pg)
        t = open(p, encoding="utf-8").read()
        usa_mappa |= "data-mappa" in t
        usa_form |= "<form" in t
        t = togli_demo(t)
        t = aggiungi_canonical(t, base_url + ("" if pg == "index.html" else pg))
        t = link_privacy_footer(t)
        scrivi(p, t)

    scheletro = open(os.path.join(out, "index.html"), encoding="utf-8").read()
    nome = c.get("nome_commerciale") or c["ragione_sociale"]
    paragrafi_extra = []
    if usa_mappa:
        paragrafi_extra.append(modello("privacy-mappa.html"))
    if usa_form:
        paragrafi_extra.append(modello("privacy-modulo.html"))
    corpo_privacy = riempi(modello("privacy.html"), {
        "ragione_sociale": html.escape(c["ragione_sociale"]), "indirizzo": html.escape(c.get("indirizzo", "")),
        "piva": c.get("piva", ""), "email": c.get("email", ""), "dominio": dominio,
        "aggiornamento": oggi().strftime("%d/%m/%Y"), "extra": "\n".join(paragrafi_extra),
    })
    privacy = pagina_da_scheletro(scheletro, f"Privacy e cookie — {nome}",
                                  f"Informativa privacy e cookie del sito {dominio}.", corpo_privacy)
    privacy = aggiungi_canonical(privacy, base_url + "privacy.html")
    scrivi(os.path.join(out, "privacy.html"), privacy)
    pagina404 = pagina_da_scheletro(scheletro, f"Pagina non trovata — {nome}", "Pagina non trovata.",
                                    modello("404.html"))
    pagina404 = re.sub(r'[ \t]*<link rel="canonical"[^>]*>\s*\n?', "", pagina404)
    pagina404 = pagina404.replace("<head>", '<head>\n  <base href="/">', 1)
    scrivi(os.path.join(out, "404.html"), pagina404)

    tutte = sorted(pagine + ["privacy.html"], key=lambda p: (p != "index.html", p))
    scrivi(os.path.join(out, "robots.txt"), f"User-agent: *\nAllow: /\n\nSitemap: {base_url}sitemap.xml\n")
    voci = "\n".join(
        f"  <url><loc>{base_url}{'' if pg == 'index.html' else pg}</loc><lastmod>{oggi().isoformat()}</lastmod></url>"
        for pg in tutte)
    scrivi(os.path.join(out, "sitemap.xml"),
           f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{voci}\n</urlset>\n')
    scrivi(os.path.join(out, "_headers"), modello("_headers"))

    print(f"Sito definitivo creato in: {out}")
    print(f"  pagine: {', '.join(tutte)} + 404.html, robots.txt, sitemap.xml, _headers")
    print("  tolti: avviso 'Anteprima di proposta', noindex, blocco dei motori di ricerca\n")
    ok = verifica(cliente, dest)
    print("\nRicorda: la privacy è un testo base. Il titolare è il cliente: fagliela leggere e, se ha un "
          "suo consulente privacy, fagliela controllare.")
    return ok


# ---------------------------------------------------------------- verifica

def verifica(cliente, dest=None):
    out = dest_sito(cliente, dest)
    if not os.path.isdir(out):
        sys.exit(f"Sito definitivo non trovato in {out}: lancia prima il comando produzione.")
    errori, avvisi = [], []
    pagine = sorted(f for f in os.listdir(out) if f.endswith(".html"))
    for pg in pagine:
        t = open(os.path.join(out, pg), encoding="utf-8").read()
        e = lambda m: errori.append(f"{pg}: {m}")
        w = lambda m: avvisi.append(f"{pg}: {m}")
        if re.search(r'<meta\s+name="robots"[^>]*noindex', t, re.I):
            e("c'è ancora il noindex: Google non lo indicizzerebbe")
        if "demo-tag" in t or "Anteprima di proposta" in t:
            e("c'è ancora l'avviso di anteprima")
        if pg != "404.html" and 'rel="canonical"' not in t:
            w("manca il link canonical")
        if pg not in ("privacy.html",) and "privacy.html" not in t:
            e("manca il link alla privacy nel footer")
        for s in re.findall(r"\[DA COMPLETARE[^\]]*\]|\{\{[^}]{0,40}\}\}|lorem ipsum|TODO", t, re.I):
            e(f"da completare: {s[:60]}")
        if pg == "index.html" and not re.search(r"P\.?\s?IVA|Partita IVA", t, re.I):
            e("nel footer manca la partita IVA dell'azienda (obbligatoria sul sito)")
        if not re.search(r"<title>[^<]{5,}</title>", t):
            e("titolo della pagina mancante")
        if pg not in ("404.html",) and not re.search(r'<meta name="description" content="[^"]{50,}"', t):
            w("meta description mancante o corta")
        for m in re.findall(r'(?:src|href)="(http://[^"]+)"', t):
            e(f"risorsa non sicura (http): {m}")
        for m in re.findall(r'(?:src|href|data-lightbox)="([^"]+)"', t) + \
                [x.strip().split(" ")[0] for s in re.findall(r'srcset="([^"]+)"', t) for x in s.split(",")]:
            u = urlparse(m)
            if u.scheme or m.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "/")):
                continue
            if not os.path.exists(os.path.join(out, unquote(u.path))):
                e(f"file mancante: {m}")
    robots = os.path.join(out, "robots.txt")
    if not os.path.exists(robots) or re.search(r"^Disallow:\s*/\s*$", open(robots).read(), re.M):
        errori.append("robots.txt blocca i motori di ricerca (o manca)")
    if not os.path.exists(os.path.join(out, "sitemap.xml")):
        errori.append("manca sitemap.xml")
    h = os.path.join(out, "_headers")
    if os.path.exists(h) and "noindex" in open(h).read():
        errori.append("_headers contiene ancora X-Robots-Tag: noindex")
    if not os.path.exists(os.path.join(out, "privacy.html")):
        errori.append("manca privacy.html")

    for x in errori:
        print("  ✗ " + x)
    for x in avvisi:
        print("  ! " + x)
    if not errori and not avvisi:
        print("  ✓ Sito definitivo a posto.")
    print(f"\n{len(errori)} errori, {len(avvisi)} avvisi.")
    return not errori


# ---------------------------------------------------------------- repo

def git(cartella, *args, check=True):
    r = subprocess.run(["git", "-C", cartella, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} non riuscito:\n{r.stderr.strip()}")
    return r.stdout.strip()


def repo(cliente, dest=None):
    out = dest_sito(cliente, dest)
    if not os.path.isdir(out):
        sys.exit(f"Sito definitivo non trovato in {out}: lancia prima il comando produzione.")
    if not verifica(cliente, dest):
        sys.exit("\nCorreggi gli errori prima di creare il repo.")
    nome = git(RADICE, "config", "--local", "user.name", check=False)
    email = git(RADICE, "config", "--local", "user.email", check=False)
    if not (nome and email):
        sys.exit("Nel repo scout-to-site non trovo user.name/user.email LOCALI (quelli personali).\n"
                 "Impostali lì (vedi README, sezione Git) così non uso per sbaglio quelli di Sydema.")
    nuovo = not os.path.isdir(os.path.join(out, ".git"))
    if nuovo:
        git(out, "init")
        git(out, "checkout", "-b", "main")
    git(out, "config", "user.name", nome)
    git(out, "config", "user.email", email)
    git(out, "add", "-A")
    if git(out, "status", "--porcelain"):
        git(out, "commit", "-m", "Sito pronto per la pubblicazione" if nuovo else "Aggiornamento sito")
        print(f"Commit fatto in {out} (autore: {nome} <{email}>)")
    else:
        print("Niente da committare: il repo è già aggiornato.")
    remoto = git(out, "remote", "get-url", "origin", check=False)
    nome_repo = f"sito-{slug(cliente)}"
    if remoto:
        print(f"Remoto: {remoto}\nPer pubblicare le modifiche:  git -C \"{out}\" push")
        return
    print(f"""
Ultimi passi (una volta sola):
 1. GitHub → New repository → nome  {nome_repo}  → Private → NIENTE README/.gitignore → Create.
 2. Poi qui:
      cd "{out}"
      git remote add origin https://github.com/<tuo-utente>/{nome_repo}.git
      git push -u origin main
    (password = il token GitHub, come per scout-to-site)
 3. Netlify → Add new project → Import an existing project → GitHub → {nome_repo}
    Build command: vuoto · Publish directory: .   → Deploy.
 4. Netlify → Project configuration → General → Visitor access: production PUBBLICA.
 5. Domain management → Add a domain → il dominio del cliente → segui  consegna.py dns
Da quel momento ogni  git push  ripubblica il sito da solo.""")


# ---------------------------------------------------------------- dns

def interroga(nome, tipo):
    import requests
    try:
        import truststore  # type: ignore
        truststore.inject_into_ssl()
    except Exception:
        pass
    r = requests.get("https://dns.google/resolve", params={"name": nome, "type": tipo}, timeout=15,
                     headers={"Accept": "application/dns-json"})
    r.raise_for_status()
    codici = {1: "A", 5: "CNAME", 2: "NS", 15: "MX", 16: "TXT", 28: "AAAA"}
    return sorted({(codici.get(a["type"], str(a["type"])), a["data"].strip('"'))
                   for a in r.json().get("Answer", []) if codici.get(a["type"]) == tipo})


def dns(dominio, cliente=None):
    dominio = re.sub(r"^https?://", "", dominio).strip("/")
    nudo = dominio[4:] if dominio.startswith("www.") else dominio
    www = f"www.{nudo}"
    richieste = [(nudo, "NS"), (nudo, "A"), (nudo, "AAAA"), (www, "CNAME"), (www, "A"),
                 (nudo, "MX"), (nudo, "TXT")]
    risultati = {}
    for nome, tipo in richieste:
        try:
            risultati[f"{tipo} {nome}"] = [v for _, v in interroga(nome, tipo)]
        except Exception as ex:
            sys.exit(f"Non riesco a interrogare il DNS ({ex}). Riprova o usa  nslookup -type={tipo} {nome}")
    righe = [f"# DNS di {nudo} — {datetime.datetime.now():%Y-%m-%d %H:%M}", ""]
    for k, v in risultati.items():
        righe.append(f"- **{k}**: {', '.join(v) if v else '(nessuno)'}")
    testo = "\n".join(righe)
    print(testo.replace("**", ""))

    print()
    a_nudo = risultati[f"A {nudo}"]
    cname = " ".join(risultati[f"CNAME {www}"])
    if NETLIFY_IP in a_nudo or "netlify" in cname:
        print("  ✓ Il dominio punta già a Netlify" + ("" if "netlify" in cname else " (controlla anche il www)"))
    else:
        print("  → Il dominio NON punta ancora a Netlify. Quando colleghi il dominio, nel pannello del registrar"
              " cambia SOLO:")
        print(f"      record A   di {nudo}  →  {NETLIFY_IP}")
        print(f"      record CNAME di {www} →  <nome-progetto>.netlify.app")
        print("    (oppure segui esattamente quello che ti indica Netlify in Domain management).")
    mx = risultati[f"MX {nudo}"]
    if mx:
        print(f"  ! Il dominio riceve posta ({', '.join(mx)}): NON toccare i record MX né i TXT (SPF, DKIM).")
        print("    Non spostare i nameserver (NS) a Netlify: cambia solo A e CNAME del sito.")

    if cliente:
        cart = cartella_consegna(cartella_cliente(cliente))
        precedenti = sorted(glob.glob(os.path.join(cart, "dns-*.md")))
        dest = os.path.join(cart, f"dns-{datetime.datetime.now():%Y%m%d-%H%M}.md")
        scrivi(dest, testo + "\n")
        print(f"\nFoto del DNS salvata in {rel(dest)}")
        if precedenti:
            primo = open(precedenti[0], encoding="utf-8").read()
            for chiave in (f"MX {nudo}", f"TXT {nudo}", f"NS {nudo}"):
                prima = re.search(rf"- \*\*{re.escape(chiave)}\*\*: (.*)", primo)
                if prima and prima.group(1) != (", ".join(risultati[chiave]) or "(nessuno)"):
                    print(f"  ✗ ATTENZIONE: {chiave} è cambiato rispetto a {os.path.basename(precedenti[0])}!")
                    print(f"      prima: {prima.group(1)}\n      ora:   {', '.join(risultati[chiave]) or '(nessuno)'}")
                    if chiave.startswith("MX"):
                        print("      La posta del cliente potrebbe non arrivare più: rimetti subito i valori di prima.")


# ---------------------------------------------------------------- documento

def documento(cliente, dest=None):
    c = leggi_cliente(cliente)
    io = prestatore(serve=False)
    out = dest_sito(cliente, dest)
    remoto = git(out, "remote", "get-url", "origin", check=False) if os.path.isdir(os.path.join(out, ".git")) else ""
    pagine = sorted((f for f in os.listdir(out) if f.endswith(".html") and f != "404.html"),
                    key=lambda p: (p != "index.html", p)) if os.path.isdir(out) else []
    valori = c | {
        "data": oggi().strftime("%d/%m/%Y"),
        "nome_commerciale": c.get("nome_commerciale") or c["ragione_sociale"],
        "saluto": f"Buongiorno {c['referente']}" if c.get("referente") else "Buongiorno",
        "prestatore_nome": io.get("nome", "Federico Manetta"), "prestatore_email": io.get("email", ""),
        "prestatore_telefono": io.get("telefono", ""),
        "elenco_pagine": "\n".join(f"- https://{c.get('dominio', '')}/{'' if p == 'index.html' else p}"
                                   for p in pagine),
        "hosting": ("Netlify (piano gratuito), gestito da me" if not io.get("partita_iva")
                    else "Netlify, incluso nel canone"),
    }
    dest_doc = os.path.join(cartella_consegna(cliente), "documento-consegna.md")
    scrivi(dest_doc, riempi(modello("documento-consegna.md"), valori))
    print(f"Documento di consegna: {rel(dest_doc)}  (bozza da rileggere prima di inviarla)")
    print(f"Promemoria interno (non va al cliente): repo del sito = {remoto or 'non ancora collegato'}")


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description="Consegna: accordo, ricevute, sito definitivo, dominio.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome, aiuto in (("avvia", "Crea consegna/cliente.txt e la checklist"),
                        ("accordo", "Bozza dell'accordo da mandare al cliente")):
        sub.add_parser(nome, help=aiuto).add_argument("cliente")
    s = sub.add_parser("ricevuta", help="Ricevuta di prestazione occasionale (HTML da salvare in PDF)")
    s.add_argument("cliente")
    s.add_argument("--tipo", choices=["acconto", "saldo", "altro"], required=True)
    s.add_argument("--importo", type=float)
    s.add_argument("--descrizione")
    s = sub.add_parser("incassato", help="Segna una ricevuta come pagata")
    s.add_argument("numero", help="es. 1/2026")
    s.add_argument("--data", help="AAAA-MM-GG (default oggi)")
    sub.add_parser("riepilogo", help="Ricevute e totali per anno")
    s = sub.add_parser("produzione", help="Crea il sito definitivo dalla demo")
    s.add_argument("cliente")
    s.add_argument("--dominio")
    s.add_argument("--dest", help="Cartella di destinazione (default ../siti-clienti/sito-<cliente>)")
    s.add_argument("--forza", action="store_true")
    for nome, aiuto in (("verifica", "Controlla il sito definitivo"), ("repo", "Crea/aggiorna il repo git del sito"),
                        ("documento", "Documento di consegna per il cliente")):
        s = sub.add_parser(nome, help=aiuto)
        s.add_argument("cliente")
        s.add_argument("--dest")
    s = sub.add_parser("dns", help="Fotografa i DNS del dominio (prima e dopo il collegamento)")
    s.add_argument("dominio")
    s.add_argument("--salva", metavar="CLIENTE", help="Salva la foto in clienti/<x>/consegna e confronta")

    a = p.parse_args()
    if a.cmd == "riepilogo":
        return riepilogo()
    if a.cmd == "incassato":
        return incassato(a.numero, a.data)
    if a.cmd == "dns":
        return dns(a.dominio, a.salva)
    cliente = cartella_cliente(a.cliente)
    if a.cmd == "avvia":
        avvia(cliente)
    elif a.cmd == "accordo":
        accordo(cliente)
    elif a.cmd == "ricevuta":
        ricevuta(cliente, a.tipo, a.importo, a.descrizione)
    elif a.cmd == "produzione":
        sys.exit(0 if produzione(cliente, a.dominio, a.dest, a.forza) else 1)
    elif a.cmd == "verifica":
        sys.exit(0 if verifica(cliente, a.dest) else 1)
    elif a.cmd == "repo":
        repo(cliente, a.dest)
    elif a.cmd == "documento":
        documento(cliente, a.dest)


if __name__ == "__main__":
    main()
