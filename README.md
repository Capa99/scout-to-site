# Lavori x soldini: pipeline siti "demo prima"

Agent 1 di 5: **Scout**. Trova le aziende di una zona che hanno un sito vecchio,
morto o assente e prepara una lista di prospect verificati da chiamare.

```
lavori-soldini/
├── .claude/agents/scout.md   ← definizione dell'agent per Claude Code
├── scout/                    ← script + installazione
│   ├── scout.py
│   ├── requirements.txt
│   ├── setup.bat             ← Windows
│   └── setup.sh              ← macOS / Linux
└── prospect/                 ← qui finiscono CSV e report
```

## Installazione (PC aziendale Windows, senza permessi di amministratore)

1. **Python**: se non c'è, installalo dal Microsoft Store o da python.org scegliendo
   "Install for current user only" (non serve l'amministratore).
2. Estrai la cartella `lavori-soldini` dove vuoi, per esempio in `Documenti`.
3. Doppio clic su `scout\setup.bat`. Crea `scout\.venv` e installa le dipendenze.
4. **Se sei dietro un proxy aziendale** e l'installazione fallisce, apri un prompt
   dei comandi nella cartella `scout` e lancia:
   ```
   set HTTPS_PROXY=http://indirizzo-proxy:porta
   set HTTP_PROXY=http://indirizzo-proxy:porta
   setup.bat
   ```
   In Git Bash (quello usato da Claude Code) si usa invece
   `export HTTPS_PROXY=http://indirizzo-proxy:porta`.
   Gli errori di certificato dovuti all'ispezione SSL aziendale li risolve già il
   pacchetto `truststore`, installato in automatico.

## Uso con Claude Code

Apri Claude Code nella cartella `lavori-soldini` e scrivi per esempio:

> usa lo scout su Vigevano e Mortara, settore manifattura e carpenteria, voglio 10 prospect

Il risultato è il report `prospect/vigevano-AAAA-MM-GG.md`, con la tabella dei
prospect e una frase d'aggancio per ogni telefonata.

Se crei `prospect/contattati.csv` (stesse colonne: `nome;sito;categoria;comune;telefono`),
lo Scout salta le aziende che hai già sentito.

## Uso manuale (senza Claude)

```
cd scout
.venv\Scripts\python.exe scout.py tutto --comune Vigevano --tipi craft,industrial,office -o ..\prospect\vigevano.csv
```
Il CSV si apre direttamente in Excel o si importa in Google Sheets.

**Rilanci sulla stessa città:** se il file esiste già, lo script aggiunge solo le
aziende nuove, senza doppioni (stesso dominio, o stesso nome se non hanno sito), e non
rivaluta quelle già presenti. Le colonne che aggiungi tu in Excel (es. `note`,
`chiamato`) restano. La colonna `trovato_il` dice quando è entrata ogni azienda.
Per ripartire da zero usa `--sovrascrivi`. Prima di rilanciare chiudi il file in Excel.

Opzioni utili: `--min 35` tiene solo i siti messi peggio; `--pagespeed` aggiunge
il punteggio Google PageSpeed (più lento; con molti siti conviene una chiave API
gratuita nella variabile `PAGESPEED_API_KEY`).

## Come funziona il punteggio (0-100, più alto = sito messo peggio)

| Segnale | Punti |
|---|---|
| Non leggibile da cellulare (manca il viewport) | +25 |
| Niente HTTPS o certificato non valido | +20 |
| Copyright fermo da 6+ anni / 3-5 anni / 2 anni | +20 / +10 / +5 |
| Flash, oppure frame | +15 ciascuno |
| Impaginazione a tabelle; tag obsoleti (font, center, marquee) | +10 ciascuno |
| jQuery < 1.9; strumento datato (FrontPage, Dreamweaver, Joomla 1-2, WordPress < 5) | +10 ciascuno |
| PageSpeed mobile < 50 (solo con `--pagespeed`) | +10 |
| Risposta lenta (> 4 s); http che non reindirizza su https | +5 ciascuno |
| P.IVA non visibile in homepage | +3 |

Priorità: **ALTA** da 60 in su, **MEDIA** 35-59, **BASSA** sotto 35.
Casi speciali: **MORTO** (sito irraggiungibile, 90), **SITO VUOTO** (dominio
parcheggiato o in costruzione, 85), **SOLO SOCIAL** (solo pagina Facebook/Instagram, 80).

## Usarlo anche sul PC di casa

La cartella è portabile: copiala e rilancia il setup (`setup.bat` su Windows,
`setup.sh` su Mac/Linux). L'ambiente `.venv` non va copiato, si ricrea.
Per tenere sincronizzati i due PC conviene un **repository GitHub privato**:
il file `.gitignore` esclude già `.venv`.

## Prossimi agent
2. Analista (estrae i contenuti dal sito vecchio) · 3. Builder (crea la demo da
template di settore) · 4. Outreach (script per la chiamata) · 5. Assistenza
(bozze di risposta e modifiche, con approvazione umana).
