# Lavori x soldini: pipeline siti "demo prima"

Agent pronti: **1. Scout** (trova i prospect), **2. Analista** (estrae il materiale dal loro
sito e scrive il brief), **3. Builder** (costruisce la demo e la impacchetta per Netlify) e
**4. Outreach** (email approvate da te, registro contatti, agenda dei richiami).

```
lavori-soldini/
├── .claude/agents/          ← definizioni degli agent per Claude Code
│   ├── scout.md
│   ├── analista.md
│   ├── builder.md
│   └── outreach.md
├── scout/scout.py           ← trova aziende e dà un punteggio ai siti
├── analista/analista.py     ← estrae testi, contatti, logo, colori, immagini
├── builder/builder.py       ← prepara, controlla, fotografa e impacchetta le demo
├── outreach/                ← outreach.py, listino.md, regole-contatto.md, risposte-tipo.md
├── stili/                   ← i 5 stili grafici di base (atelier, industria, trattoria, studio, bottega)
├── prospect/                ← CSV e report dello Scout
├── clienti/<azienda>/       ← contenuti.md, brief.md, img/, demo/, screenshot/, zip per Netlify
├── requirements.txt
├── setup.bat                ← installazione Windows
└── setup.sh                 ← installazione macOS / Linux
```

## Installazione (PC aziendale Windows, senza permessi di amministratore)

1. **Python**: se non c'è, installalo dal Microsoft Store o da python.org scegliendo
   "Install for current user only" (non serve l'amministratore).
2. Doppio clic su **`setup.bat`** nella cartella principale. Crea `.venv`, l'ambiente
   Python condiviso da tutti gli agent, e installa le dipendenze. Se trova il vecchio
   `scout\.venv` lo cancella, perché non serve più.
3. **Se sei dietro un proxy aziendale** e l'installazione fallisce, apri un prompt
   dei comandi nella cartella principale e lancia:
   ```
   set HTTPS_PROXY=http://indirizzo-proxy:porta
   set HTTP_PROXY=http://indirizzo-proxy:porta
   setup.bat
   ```
   In Git Bash (quello usato da Claude Code) si usa invece
   `export HTTPS_PROXY=http://indirizzo-proxy:porta`.
   Gli errori di certificato dovuti all'ispezione SSL aziendale li risolve già il
   pacchetto `truststore`, installato in automatico.

Quando arriva un agent nuovo che richiede altre librerie, basta rilanciare `setup.bat`.

**Tutti i comandi si lanciano dalla cartella principale** `lavori-soldini`.

## Uso con Claude Code

Apri Claude Code nella cartella `lavori-soldini` e scrivi per esempio:

> usa lo scout su Vigevano e Mortara, settore manifattura e carpenteria, voglio 10 prospect

> usa l'analista su SUGAR s.a.s. dal CSV di Vigevano

> usa il builder sulla demo di SUGAR

> outreach: prepara il primo contatto per SUGAR   ·   outreach: ha risposto così: "..."   ·   outreach: agenda

Lo Scout produce il report `prospect/vigevano-AAAA-MM-GG.md`, con la tabella dei
prospect e una frase d'aggancio per ogni telefonata. L'Analista produce
`clienti/<azienda>/brief.md`, da cui partirà il Builder.

Se crei `prospect/contattati.csv` (stesse colonne: `nome;sito;categoria;comune;telefono`),
lo Scout salta le aziende che hai già sentito.

## Scout: uso manuale (senza Claude)

```
.venv\Scripts\python.exe scout\scout.py tutto --comune Vigevano -o prospect\vigevano.csv
```
Il CSV si apre direttamente in Excel o si importa in Google Sheets.

**Rilanci sulla stessa città:** se il file esiste già, lo script aggiunge solo le
aziende nuove, senza doppioni (stesso dominio, o stesso nome se non hanno sito), e non
rivaluta quelle già presenti. Le colonne che aggiungi tu in Excel (es. `note`,
`chiamato`) restano. La colonna `trovato_il` dice quando è entrata ogni azienda.
Per ripartire da zero, o rivalutare tutto con regole nuove, usa `--sovrascrivi`.
Prima di rilanciare chiudi il file in Excel.

**Aziende aggiunte a mano** (trovate su Google Maps): scrivile in un CSV con le colonne
`nome;sito;categoria;comune;telefono` e lancia
`.venv\Scripts\python.exe scout\scout.py valuta prospect\vigevano-manuali.csv -o prospect\vigevano.csv`
(senza `--sovrascrivi`): vengono aggiunte al file principale.

Opzioni utili: `--min 35` tiene solo i siti messi peggio; `--pagespeed` aggiunge
il punteggio Google PageSpeed (più lento; con molti siti conviene una chiave API
gratuita nella variabile `PAGESPEED_API_KEY`).

## Analista: uso manuale (senza Claude)

```
.venv\Scripts\python.exe analista\analista.py da-csv prospect\vigevano.csv --nome "SUGAR"
.venv\Scripts\python.exe analista\analista.py da-csv prospect\vigevano.csv --primi 3
.venv\Scripts\python.exe analista\analista.py analizza www.sito-azienda.it --nome "Rossi Srl"
```
Visita la homepage e fino a 10 pagine, scegliendo prima le più utili (chi siamo,
servizi, prodotti, contatti) e seguendo anche i siti a frame. In `clienti\<azienda>\`
trovi:
- `contenuti.md`: contatti, colori (dal sito e dal logo), logo, testi pagina per pagina
  (senza menu e footer ripetuti), elenco immagini con risoluzione e note per il Builder;
- `img\`: immagini e logo scaricati, già senza icone e doppioni;
- `sorgente\`: l'HTML originale di ogni pagina (utile per recuperare dettagli).

Il **brief** (`brief.md`) invece lo scrive l'agent in Claude Code, leggendo questi file.

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
| Segnaposto del template mai sostituiti (lorem ipsum, @example.com, 0000000) | +20 |
| P.IVA non visibile in homepage | +3 |

Priorità: **ALTA** da 60 in su, **MEDIA** 35-59, **BASSA** sotto 35.
Casi speciali:
- **SITO VUOTO** (85): dominio parcheggiato o pagina "in costruzione".
- **SOLO SOCIAL** (80): ha solo una pagina Facebook/Instagram.
- **SOLO SCHEDA** (75): ha solo una scheda su Booking, Google, TripAdvisor,
  PagineGialle e simili. Per hotel e agriturismi l'aggancio è forte: con un sito
  proprio pagherebbero meno commissioni.
- **MORTO** (70): sito irraggiungibile. Spesso è un dominio scaduto, ma l'azienda
  potrebbe aver chiuso o cambiato sito: va verificato.
- **VERIFICA** (50): il server risponde con un errore (es. 403). Il sito esiste ma
  blocca i bot, oppure lo blocca il filtro web aziendale: aprilo nel browser.
- **SCARTA**: pagine che non sono dell'attività (Wikipedia, portali) e pagine-filiale di catene.

Di default la scoperta esclude musei, teatri, enti pubblici, associazioni, centri
commerciali e catene. Per includerli usa `--tutti` (e `--catene`).

## Git: lavorare da ufficio e da casa

Repository privato: **https://github.com/Capa99/scout-to-site**

La regola d'oro: **`git pull` quando inizi, `git push` quando finisci**, su
qualsiasi PC. Così trovi sempre l'ultima versione e non crei conflitti.

### Ogni volta che inizi (ufficio o casa)

Apri il cmd nella cartella del progetto (barra dell'indirizzo → `cmd` → Invio):
```
git pull
```

### Ogni volta che finisci (ufficio o casa)

```
git add .
git commit -m "breve descrizione di cosa hai fatto"
git push
```
Se `git push` viene rifiutato con `rejected` / `fetch first`, vuol dire che
sull'altro PC hai caricato qualcosa che qui non hai: lancia `git pull` e poi di
nuovo `git push`.

Prima di `git pull` o `git add`, **chiudi i CSV aperti in Excel**.

### PC di casa: la prima volta

1. Installa Git (https://git-scm.com) e Python, se non ci sono.
2. Apri il cmd nella cartella dove vuoi il progetto e lancia:
   ```
   git clone https://github.com/Capa99/scout-to-site.git
   cd scout-to-site
   git config user.name "Federico Manetta"
   git config user.email "federicomanetta1999@gmail.com"
   ```
3. Doppio clic su `setup.bat` per ricreare `.venv`, che non viaggia con Git.
4. Al primo `git push` si apre il login di GitHub: entra con **Capa99**. Con un
   Git recente basta il browser; se invece chiede una password, usa un token
   (vedi sotto).

### PC aziendale: cose da sapere

- La cartella è `C:\Users\manetta\Desktop\progettini\lavori-soldini`, già
  collegata a GitHub. Nome ed email personali sono impostati **solo per questa
  cartella**: i progetti Sydema continuano a usare `f.manetta@sydema.it`.
- **Non usare mai `--global`** con `git config` per questo progetto, perché
  cambierebbe le impostazioni anche dei repository di lavoro.
- Il Git dell'ufficio è vecchio (2.22): `git init -b` non esiste, e al push non
  si apre il browser. Come password si usa il **token** (vedi sotto), che Windows
  ricorda fino alla scadenza.
- Per controllare con che email stai facendo commit:
  `git log -1 --format="%an <%ae>"`.

### Token GitHub (quando scade o su un PC nuovo)

GitHub non accetta la password dell'account per Git: serve un token.
1. github.com → foto profilo → **Settings** → **Developer settings** →
   **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**.
2. Note: nome del PC (es. `pc-ufficio`), scadenza 90 giorni, spunta solo **`repo`**.
3. **Generate token** e copialo subito (inizia con `ghp_`): non lo rivedrai.
4. Al prossimo `git push`, quando chiede la password, incollalo con il tasto
   destro del mouse (non compare nulla mentre incolli: è normale) e premi Invio.

Se il token è scaduto e Windows continua a usare quello vecchio: **Pannello di
controllo** → **Gestione credenziali** → **Credenziali di Windows** → elimina la
voce `git:https://Capa99@github.com`, poi rifai il push con il token nuovo.

### Cosa NON finisce su GitHub

`.venv` (si ricrea con il setup) e i file `__pycache__`, come da `.gitignore`.
Le cartelle in `clienti\` invece vengono caricate, immagini comprese.
I CSV in `prospect\` invece vengono caricati: così le note scritte in ufficio le
ritrovi a casa.

## Builder: uso manuale (senza Claude)

Il Builder ha due parti: le **pagine** le scrive l'agent in Claude Code seguendo il brief e lo
stile; lo **script** fa tutto il resto.

```
.venv\Scripts\python.exe builder\builder.py stili
.venv\Scripts\python.exe builder\builder.py prepara clienti\sugar-s-a-s --stile atelier --colori accento=#56684f
.venv\Scripts\python.exe builder\builder.py immagini clienti\sugar-s-a-s 07-201621-1.jpg 36-logoimg-8276-low-7.jpg
.venv\Scripts\python.exe builder\builder.py controlla clienti\sugar-s-a-s
.venv\Scripts\python.exe builder\builder.py anteprima clienti\sugar-s-a-s
.venv\Scripts\python.exe builder\builder.py screenshot clienti\sugar-s-a-s
.venv\Scripts\python.exe builder\builder.py pacchetto clienti\sugar-s-a-s
```
- **prepara**: crea `demo\` con lo stile, i colori del cliente (`tema.css`) e i caratteri
  scaricati in locale (niente Google Fonts: più veloce e senza cookie). Serve internet la prima
  volta per ogni carattere, poi restano in `.cache\`.
- **immagini**: converte le foto scelte in WebP da 800 e 1600 px (di solito 3-10 volte più leggere).
- **controlla**: viewport per il telefono, noindex, avviso "anteprima", alt delle immagini,
  file mancanti, segnaposto dimenticati, peso della pagina.
- **anteprima**: apre la demo nel browser (Ctrl+C per chiudere).
- **screenshot**: foto della demo da desktop e da telefono in `screenshot\`, utili anche da
  mandare al cliente su WhatsApp. È facoltativo e richiede Playwright, da installare una volta sola
  (circa 150 MB):
  ```
  .venv\Scripts\pip install playwright
  .venv\Scripts\playwright install chromium
  ```
- **pacchetto**: ricontrolla tutto e crea `clienti\<azienda>\demo-<azienda>-AAAAMMGG.zip`.

**Pubblicare la demo:** vai su https://app.netlify.com/drop e trascina la cartella
`clienti\<azienda>\demo`. Netlify ti dà un link: manda al cliente **solo il link**, mai i file.
Con un account Netlify gratuito puoi rinominare il link (es. `domo-adami-demo.netlify.app`) e
cancellare la demo quando non serve più.

Ogni demo contiene sempre `noindex` (Google non la mostra) e l'etichetta "Anteprima di proposta ·
non è il sito ufficiale": usi testi, foto e marchio del cliente, quindi non deve mai poter essere
scambiata per il sito vero.

## Outreach: contattare i prospect

**Nessuna email parte da sola.** L'agent scrive la bozza, te la mostra intera in chat e aspetta il
tuo ok; poi apre Gmail con l'email già compilata e **sei tu a premere Invia**.

- `outreach\listino.md`: prezzi e condizioni (590 € il sito, 15 €/mese il canone, ritenuta del 20%).
  L'agent non può promettere niente che non sia scritto lì: per cambiare un prezzo modifica il file.
- `outreach\regole-contatto.md`: metodo scelto (prima email, poi telefonate lampo) e limiti
  (massimo 5 email a freddo al giorno, 1 solo sollecito, frase per non essere ricontattati).
  **Attenzione:** per il Garante privacy l'email commerciale non richiesta è illecita anche verso
  le aziende; le regole servono a tenere il rischio basso, non lo azzerano.
- `outreach\risposte-tipo.md`: basi per le risposte più comuni (prezzo, "abbiamo già qualcuno"…).
- `prospect\contattati.csv`: il registro di tutti i contatti, con stato e data del prossimo
  richiamo. Lo Scout lo usa per non riproporti aziende già sentite.
- `clienti\<azienda>\outreach\`: bozze, risposte ricevute e storico (`registro.md`).

```
.venv\Scripts\python.exe outreach\outreach.py agenda
.venv\Scripts\python.exe outreach\outreach.py aggiungi "SUGAR s.a.s." --da-csv prospect\vigevano.csv --email info@domoadami.com --cartella clienti\sugar-s-a-s
.venv\Scripts\python.exe outreach\outreach.py gmail clienti\sugar-s-a-s\outreach\bozze\primo-contatto.md
.venv\Scripts\python.exe outreach\outreach.py registra "SUGAR" --stato email_inviata --canale email
```
Il comando `gmail` rifiuta le bozze che non hanno `Stato: approvata`, quelle a freddo senza la
frase per non essere ricontattati e le aziende che hanno chiesto di non essere scritte.
Se sul PC hai più account Google, scrivi il tuo Gmail personale in `outreach\config.txt`
(`gmail=...`) così le bozze si aprono nell'account giusto.

## Stili disponibili
| Stile | Per chi |
|---|---|
| **atelier** | moda, sposa, gioielli, bellezza, design, fotografi, wedding |
| **industria** | manifattura, automazione, carpenteria, officine, impianti |
| **trattoria** | ristoranti, agriturismi, bar, pasticcerie, B&B, cantine |
| **studio** | commercialisti, avvocati, assicurazioni, dentisti, immobiliari |
| **bottega** | artigiani, negozi di quartiere, parrucchieri, palestre, officine auto/moto |

Le regole di ognuno sono in `stili\<stile>\stile.md`. Per cambiare il "gusto della casa" su
tutte le demo future modifica `stili\base.css` o lo `stile.css` dello stile.

## Prossimo agent
5. Assistenza: dopo il sì del cliente, gestione delle modifiche alla demo, preventivo,
passaggio al sito definitivo sul suo dominio.
