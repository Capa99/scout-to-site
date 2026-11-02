#!/usr/bin/env python3
"""
Outreach - registro dei contatti e invio guidato delle email (sempre approvate a mano).

Niente parte da solo: questo script apre Gmail con l'email già compilata, l'invio lo fai tu.

Comandi (dalla cartella principale del progetto):
  python outreach/outreach.py aggiungi "SUGAR s.a.s." --da-csv prospect/vigevano.csv --email info@domoadami.com --cartella clienti/sugar-s-a-s
  python outreach/outreach.py registra "SUGAR" --stato email_inviata --canale email --nota "primo contatto"
  python outreach/outreach.py registra "SUGAR" --stato interessato --consenso "risposta email del 05/11: 'sì, mi mandi i prezzi'"
  python outreach/outreach.py agenda
  python outreach/outreach.py gmail clienti/sugar-s-a-s/outreach/bozze/2026-11-03-primo-contatto.md
  python outreach/outreach.py whatsapp clienti/sugar-s-a-s/outreach/bozze/... --numero 3468631692

Registro: prospect/contattati.csv (lo Scout lo usa per non riproporre aziende già contattate).
"""
import argparse
import csv
import datetime
import os
import re
import sys
import webbrowser
from urllib.parse import quote

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRO = os.path.join(RADICE, "prospect", "contattati.csv")
CONFIG = os.path.join(RADICE, "outreach", "config.txt")
CAMPI = ["nome", "sito", "categoria", "comune", "telefono", "email", "stato", "canale",
         "primo_contatto", "ultimo_contatto", "richiama_il", "consenso", "cartella", "note"]
STATI = {
    "da_contattare": "in lista, nessun contatto ancora",
    "email_inviata": "prima email inviata (a freddo)",
    "sollecito_inviato": "inviato l'unico sollecito previsto",
    "chiamato": "telefonata o visita fatta, in attesa",
    "risposto": "ha risposto, da gestire",
    "interessato": "vuole saperne di più: ha dato il consenso",
    "link_inviato": "demo inviata su richiesta",
    "preventivo": "preventivo inviato",
    "vinto": "cliente acquisito",
    "perso": "ha detto no",
    "freddo": "nessuna risposta dopo il sollecito: stop",
    "non_contattare": "ha chiesto di non essere ricontattato: mai più",
}
FINALI = {"vinto", "perso", "freddo", "non_contattare"}
LIMITE_EMAIL_FREDDO_GIORNO = 5
GIORNI_SOLLECITO = 6  # giorni lavorativi


def oggi():
    return datetime.date.today()


def piu_giorni_lavorativi(data, n):
    d = data
    while n > 0:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def leggi_registro():
    if not os.path.exists(REGISTRO):
        return []
    with open(REGISTRO, encoding="utf-8-sig", newline="") as f:
        righe = list(csv.DictReader(f, delimiter=";"))
    return [{c: (r.get(c) or "").strip() for c in CAMPI} | {k: v for k, v in r.items() if k not in CAMPI and k}
            for r in righe]


def scrivi_registro(righe):
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    extra = []
    for r in righe:
        for k in r:
            if k not in CAMPI and k not in extra:
                extra.append(k)
    try:
        with open(REGISTRO, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPI + extra, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(righe)
    except PermissionError:
        sys.exit("Non riesco a scrivere prospect/contattati.csv: è aperto in Excel? Chiudilo e rilancia.")


def trova(righe, nome):
    nome_l = nome.lower()
    esatti = [r for r in righe if r["nome"].lower() == nome_l]
    if esatti:
        return esatti[0]
    parziali = [r for r in righe if nome_l in r["nome"].lower()]
    if len(parziali) == 1:
        return parziali[0]
    if len(parziali) > 1:
        sys.exit(f"Più aziende corrispondono a '{nome}': " + ", ".join(r["nome"] for r in parziali))
    return None


def log_cliente(riga, testo):
    cartella = riga.get("cartella")
    if not cartella:
        return
    base = cartella if os.path.isabs(cartella) else os.path.join(RADICE, cartella)
    if not os.path.isdir(base):
        return
    dest = os.path.join(base, "outreach")
    os.makedirs(dest, exist_ok=True)
    p = os.path.join(dest, "registro.md")
    nuovo = not os.path.exists(p)
    with open(p, "a", encoding="utf-8") as f:
        if nuovo:
            f.write(f"# Registro contatti — {riga['nome']}\n\n")
        f.write(f"- **{datetime.datetime.now():%Y-%m-%d %H:%M}** — {testo}\n")


# ---------------------------------------------------------------- comandi

def aggiungi(nome, da_csv=None, email="", cartella="", telefono=""):
    righe = leggi_registro()
    if trova(righe, nome):
        sys.exit(f"'{nome}' è già nel registro. Usa 'registra' per aggiornarlo.")
    base = {c: "" for c in CAMPI}
    base.update(nome=nome, stato="da_contattare")
    if da_csv:
        with open(da_csv, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if nome.lower() in (r.get("nome") or "").lower():
                    for c in ("nome", "sito", "categoria", "comune", "telefono"):
                        base[c] = r.get(c, "") or base[c]
                    if not email:
                        email = r.get("email", "")
                    break
            else:
                print(f"  ! '{nome}' non trovato in {da_csv}: lo aggiungo solo con il nome.")
    if email:
        base["email"] = email
    if telefono:
        base["telefono"] = telefono
    if cartella:
        base["cartella"] = os.path.relpath(os.path.abspath(cartella), RADICE)
    righe.append(base)
    scrivi_registro(righe)
    log_cliente(base, "aggiunto al registro contatti")
    print(f"Aggiunto: {base['nome']} ({base['email'] or 'email mancante'})")


def registra(nome, stato, canale="", nota="", consenso="", richiama=""):
    if stato not in STATI:
        sys.exit("Stato sconosciuto. Possibili: " + ", ".join(STATI))
    righe = leggi_registro()
    r = trova(righe, nome)
    if not r:
        sys.exit(f"'{nome}' non è nel registro: prima usa 'aggiungi'.")
    if r["stato"] == "non_contattare" and stato not in ("non_contattare",):
        sys.exit(f"{r['nome']} ha chiesto di non essere ricontattato. Stato non modificabile.")
    oggi_s = oggi().isoformat()
    r["stato"] = stato
    if canale:
        r["canale"] = canale
    r["primo_contatto"] = r["primo_contatto"] or oggi_s
    r["ultimo_contatto"] = oggi_s
    if consenso:
        r["consenso"] = f"{oggi_s}: {consenso}"
    if richiama:
        if richiama.startswith("+"):
            r["richiama_il"] = piu_giorni_lavorativi(oggi(), int(richiama[1:])).isoformat()
        else:
            r["richiama_il"] = datetime.date.fromisoformat(richiama).isoformat()
    elif stato in ("email_inviata", "chiamato", "link_inviato", "preventivo"):
        r["richiama_il"] = piu_giorni_lavorativi(oggi(), GIORNI_SOLLECITO).isoformat()
    elif stato in FINALI:
        r["richiama_il"] = ""
    if nota:
        r["note"] = (r["note"] + " | " if r["note"] else "") + f"{oggi_s}: {nota}"
    scrivi_registro(righe)
    testo = f"stato → **{stato}**" + (f" via {canale}" if canale else "") + (f". {nota}" if nota else "")
    if consenso:
        testo += f". Consenso: {consenso}"
    log_cliente(r, testo)
    print(f"{r['nome']}: {stato} ({STATI[stato]})" + (f", da risentire il {r['richiama_il']}" if r["richiama_il"] else ""))
    if stato == "email_inviata":
        controlla_limiti(righe)


def email_freddo_inviate(righe, giorno=None):
    giorno = (giorno or oggi()).isoformat()
    return [r for r in righe if r["canale"] == "email" and not r["consenso"] and r["primo_contatto"] == giorno
            and r["stato"] in ("email_inviata", "sollecito_inviato", "risposto", "freddo", "perso", "non_contattare", "interessato")]


def controlla_limiti(righe):
    oggi_n = len(email_freddo_inviate(righe))
    if oggi_n >= LIMITE_EMAIL_FREDDO_GIORNO:
        print(f"\n  ! Oggi hai già inviato {oggi_n} email a freddo: per oggi basta (limite {LIMITE_EMAIL_FREDDO_GIORNO}).")
    a_freddo = [r for r in righe if r["canale"] == "email" and r["stato"] != "da_contattare"]
    if len(a_freddo) >= 10:
        risposte = [r for r in a_freddo if r["stato"] in ("risposto", "interessato", "link_inviato", "preventivo",
                                                          "vinto", "perso", "non_contattare")]
        if len(risposte) < 2:
            print(f"\n  ! {len(a_freddo)} email a freddo e solo {len(risposte)} risposte: "
                  "è il momento di passare alle telefonate lampo (vedi outreach/regole-contatto.md).")


def agenda():
    righe = leggi_registro()
    if not righe:
        print("Registro vuoto. Aggiungi un prospect con:  outreach.py aggiungi \"Nome\" --da-csv prospect/<comune>.csv")
        return
    o = oggi()
    da_fare = sorted((r for r in righe if r["richiama_il"] and r["stato"] not in FINALI
                      and datetime.date.fromisoformat(r["richiama_il"]) <= o), key=lambda r: r["richiama_il"])
    print(f"Agenda del {o:%d/%m/%Y}\n")
    if da_fare:
        print("Da risentire oggi o in ritardo:")
        for r in da_fare:
            cosa = {"email_inviata": "unico sollecito via email (poi stop)",
                    "sollecito_inviato": "nessuna risposta al sollecito → segna 'freddo'",
                    "chiamato": "richiamare o scrivere come concordato",
                    "link_inviato": "chiedere un parere sulla demo",
                    "preventivo": "chiedere se ha domande sul preventivo"}.get(r["stato"], "da gestire")
            print(f"  {r['richiama_il']}  {r['nome']:<30} {r['stato']:<18} → {cosa}")
    else:
        print("Niente da risentire oggi.")
    risposte = [r for r in righe if r["stato"] == "risposto"]
    if risposte:
        print("\nHanno risposto, da gestire: " + ", ".join(r["nome"] for r in risposte))
    conta = {}
    for r in righe:
        conta[r["stato"]] = conta.get(r["stato"], 0) + 1
    print("\nSituazione: " + ", ".join(f"{k} {v}" for k, v in sorted(conta.items())))
    print(f"Email a freddo inviate oggi: {len(email_freddo_inviate(righe))}/{LIMITE_EMAIL_FREDDO_GIORNO}")
    controlla_limiti(righe)


def leggi_bozza(percorso):
    testo = open(percorso, encoding="utf-8").read()
    if "\n---" not in testo:
        sys.exit("Bozza non valida: serve l'intestazione (A:, Oggetto:, Stato:) seguita da una riga '---'.")
    testa, corpo = testo.split("\n---", 1)
    campi = {}
    for riga in testa.splitlines():
        m = re.match(r"^\s*([A-Za-zà]+)\s*:\s*(.*)$", riga)
        if m:
            campi[m.group(1).lower()] = m.group(2).strip()
    return campi, corpo.strip("\n -").strip()


def verifica_invio(campi, percorso):
    if campi.get("stato", "").lower() != "approvata":
        sys.exit(f"La bozza non è approvata (Stato: {campi.get('stato') or 'mancante'}).\n"
                 "Rileggila e, se va bene, cambia la riga in 'Stato: approvata'.")
    nome = campi.get("cliente", "")
    if nome:
        r = trova(leggi_registro(), nome)
        if r and r["stato"] == "non_contattare":
            sys.exit(f"STOP: {r['nome']} ha chiesto di non essere ricontattato.")
        if r and campi.get("tipo", "") == "primo-contatto" and not r["consenso"]:
            righe = leggi_registro()
            if len(email_freddo_inviate(righe)) >= LIMITE_EMAIL_FREDDO_GIORNO:
                sys.exit(f"Limite di {LIMITE_EMAIL_FREDDO_GIORNO} email a freddo al giorno raggiunto: rimanda a domani.")
            print("  Nota: email a freddo (nessun consenso registrato). Ricorda la frase per non essere ricontattati.")
            if "ricontatt" not in open(percorso, encoding="utf-8").read().lower():
                sys.exit("La bozza a freddo non contiene la frase per chiedere di non essere ricontattati: aggiungila.")


def account_gmail():
    if os.path.exists(CONFIG):
        for riga in open(CONFIG, encoding="utf-8"):
            if riga.lower().startswith("gmail="):
                return riga.split("=", 1)[1].strip()
    return ""


def gmail(percorso, apri=True):
    campi, corpo = leggi_bozza(percorso)
    verifica_invio(campi, percorso)
    if not campi.get("a"):
        sys.exit("Manca il destinatario (riga 'A:').")
    url = ("https://mail.google.com/mail/?view=cm&fs=1"
           f"&to={quote(campi['a'])}&su={quote(campi.get('oggetto', ''))}&body={quote(corpo)}")
    acc = account_gmail()
    if acc:
        url += f"&authuser={quote(acc)}"
    print("\nApro Gmail con l'email già compilata. CONTROLLA e premi tu Invia.")
    print("Dopo l'invio registra il contatto, per esempio:")
    print(f'  outreach.py registra "{campi.get("cliente", "Nome")}" --stato '
          f'{"email_inviata" if campi.get("tipo") == "primo-contatto" else "<stato>"} --canale email\n')
    if apri:
        webbrowser.open(url)
    else:
        print(url)


def whatsapp(percorso, numero, apri=True):
    campi, corpo = leggi_bozza(percorso)
    verifica_invio(campi, percorso)
    cifre = re.sub(r"\D", "", numero)
    if not cifre.startswith("39"):
        cifre = "39" + cifre
    url = f"https://wa.me/{cifre}?text={quote(corpo)}"
    print("\nApro WhatsApp con il messaggio già scritto: controlla e invia tu.\n")
    if apri:
        webbrowser.open(url)
    else:
        print(url)


def main():
    p = argparse.ArgumentParser(description="Outreach: registro contatti e invio guidato.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("aggiungi", help="Aggiunge un prospect al registro")
    s.add_argument("nome")
    s.add_argument("--da-csv", help="CSV dello Scout da cui copiare sito, telefono, comune")
    s.add_argument("--email", default="")
    s.add_argument("--telefono", default="")
    s.add_argument("--cartella", default="", help="es. clienti/sugar-s-a-s")
    s = sub.add_parser("registra", help="Aggiorna lo stato di un contatto")
    s.add_argument("nome")
    s.add_argument("--stato", required=True, help="Uno di: " + ", ".join(STATI))
    s.add_argument("--canale", default="", choices=["", "email", "telefono", "persona", "whatsapp"])
    s.add_argument("--nota", default="")
    s.add_argument("--consenso", default="", help="Come e quando ha detto sì a ricevere email")
    s.add_argument("--richiama", default="", help="AAAA-MM-GG oppure +N giorni lavorativi")
    sub.add_parser("agenda", help="Chi risentire oggi e situazione generale")
    sub.add_parser("stati", help="Elenca gli stati possibili")
    s = sub.add_parser("gmail", help="Apre Gmail con una bozza approvata")
    s.add_argument("bozza")
    s.add_argument("--solo-link", action="store_true")
    s = sub.add_parser("whatsapp", help="Apre WhatsApp con una bozza approvata")
    s.add_argument("bozza")
    s.add_argument("--numero", required=True)
    s.add_argument("--solo-link", action="store_true")

    a = p.parse_args()
    if a.cmd == "aggiungi":
        aggiungi(a.nome, a.da_csv, a.email, a.cartella, a.telefono)
    elif a.cmd == "registra":
        registra(a.nome, a.stato, a.canale, a.nota, a.consenso, a.richiama)
    elif a.cmd == "agenda":
        agenda()
    elif a.cmd == "stati":
        for k, v in STATI.items():
            print(f"  {k:<18} {v}")
    elif a.cmd == "gmail":
        gmail(a.bozza, not a.solo_link)
    elif a.cmd == "whatsapp":
        whatsapp(a.bozza, a.numero, not a.solo_link)


if __name__ == "__main__":
    main()
