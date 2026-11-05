# Vigevano: nuovi candidati con sito vecchio (2026-11-05)

Fonti di scoperta: OpenStreetMap (nessuna attività nuova rispetto a `vigevano.csv`), PagineGialle
(circa 100 categorie lette in sola lettura), WebSearch, prove sui domini.
Esclusi tutti i nomi, domini e telefoni già presenti in `prospect/vigevano.csv`,
`prospect/vigevano-manuali.csv` e `prospect/contattati.csv` (controllo fatto con grep: nessuna sovrapposizione).
Il codice HTML è stato letto con richieste dirette (Python requests/curl), non a occhio.
Nessun contatto preso con nessuno.

## Tabella riassuntiva (ordinata per solidità e gravità del problema)

| # | Nome | Settore | Telefono | Sito | Problema principale | Solidità | Attività confermata? |
|---|------|---------|----------|------|---------------------|----------|----------------------|
| 1 | A.B.V. Trasporti S.r.l. | autotrasporti | 0381 348970 | https://www.abvtrasporti.it | manca il viewport, WebSite X5 v8, `<marquee>` | 3 | sì (bilancio 2023, sito toccato ad apr 2026) |
| 2 | Luper s.n.c. (spazzolificio) | forniture per calzaturifici | 0381 20019 | http://www.luper.eu | niente viewport, certificato non valido, tabelle, HTML 4.01 | 2-3 | probabile (scheda Yelp aggiornata a giu 2025, 5 dipendenti nel 2025) |
| 3 | Pasticceria Dante | pasticceria/bar | 0381 83776 | http://dantevigevano.it | in homepage solo "Sito in manutenzione" da apr 2024 | 2 | sì (recensione Tripadvisor ott 2025) |
| 4 | Studio Dentistico Dott. Lorenzo Capra | dentista | 0381 84312 | https://www.studiodentisticocapra.it | WordPress 4.7.29, jQuery 1.7.2, ©2018, http non va su https | 2 | probabile (scheda aggiornata a nov 2025) |
| 5 | Pala, Paletta e Forchetta | gastronomia/bar | 0381 690716 | http://www.palapalettaeforchetta.it | sito rotto: "Please stand by while configuration is in progress", certificato autofirmato | 2 | probabile (risulta aperta, recensione Google di circa 2 anni fa) |
| 6 | Autoscuola Carrobbio di Marangon Enrico | autoscuola | 0381 76315 | https://www.autoscuolacarrobbio.it | niente viewport né doctype, `<font>` e tabelle, ©2004-2024 | 2 | debole (il sito è stato aggiornato il 22-11-2024) |
| 7 | Verticalport | tende, porte, serramenti | 0381 82331 | https://www.verticalport.it | niente viewport, jQuery 1.7.1, **ma esiste già un secondo sito** | 1-2 | probabile (orari su PG, certificati rinnovati) |
| 8 | Ambulatorio Veterinario Calcaterra & Ditrani | veterinario | 0381 348960 | www.veterinariocalcaterraditrani.it | **dominio morto** (il DNS non risponde) | 2 | probabile (orari completi su PagineGialle) |

Riserve con sito morto (dominio che non risolve), da usare se servono: Gioielleria Ferrari Aldo S.r.l.
(Piazza Ducale 39, 0381 70430, rivenditore Damiani, gioielleriaferrarialdo.com morto), Hotel Ducale
(Via Trivulzio 8, 0381 095211, hducale.com morto, ancora presente su Booking/Skyscanner).

---

## Schede

### 1. A.B.V. Trasporti S.r.l.
- **Settore:** autotrasporto merci conto terzi, deposito, traslochi industriali, ADR.
- **Indirizzo:** Via Perugino 48/50, 27029 Vigevano (PV) (il sito indica anche: sede legale Corso Pavia 28).
- **Telefono:** 0381 348970 / 0381 42247 / 0381 43100 (PagineGialle); il sito indica +39 0381 39470.
- **Email:** operativo@abvtrasporti.it (dal sito).
- **P.IVA:** 02501470187.
- **Prove che è aperta:**
  - reportaziende.it: impresa "Attiva", fatturato 2023 di 786,8 mila euro (2022: 864 mila) - https://www.reportaziende.it/abv_trasporti_srl_pv_02501470187
  - Europages: 20-49 dipendenti - https://www.europages.it/ABV-TRASPORTI-SRL/SEAC006283473-001.html
  - header HTTP `Last-Modified: Wed, 29 Apr 2026` sulla homepage: qualcuno ci ha messo mano quest'anno.
- **Problemi del sito (dal codice):**
  - viewport: **ASSENTE**.
  - http -> https: sì, reindirizza (301). Certificato **valido** (scade 25-01-2027).
  - copyright: **nessuna riga di copyright** in pagina.
  - `<meta name="Generator" content="Incomedia WebSite X5 Evolution 8.0.11">` (versione di circa 15 anni fa), doctype XHTML 1.0 Strict, un tag `<marquee>` (testo scorrevole, deprecato).
  - P.IVA non visibile in homepage.
- **Aggancio:** "Dal cellulare il vostro sito si vede rimpicciolito come su un PC, e l'elenco dei servizi scorre come nei siti del 2005: un cliente che cerca un trasportatore ADR a Vigevano non capisce subito cosa fate."

### 2. Luper s.n.c. (Spazzolificio Luper)
- **Settore:** produzione di spazzole, tamponi e ruote per la finitura; forniture complete per calzaturifici e pelletterie (fondata nel 1973 secondo un catalogo di settore).
- **Indirizzo:** Corso Novara 135 (angolo Corso Ugo La Malfa), 27029 Vigevano (PV).
- **Telefono:** 0381 20019 (fax 0381 325175).
- **Email:** info@luper.eu.
- **P.IVA:** 01165560184. La ragione sociale cambia a seconda della fonte ("di Magnaga Giuseppina & C." sul sito, "di Ambrogio e Andrea Persendi" nei registri): **da verificare**.
- **Prove che è aperta:**
  - Yelp: scheda "Updated June 2025" - https://www.yelp.com/biz/luper-di-magnaga-giuseppina-vigevano
  - ufficiocamerale.it: 5 dipendenti (dato 2025) - https://www.ufficiocamerale.it/4123/luper-di-ambrogio-e-andrea-persendi-snc
  - in elenco su PagineGialle con lo stesso telefono (consultato oggi).
  - Non ho trovato recensioni o post recenti con data: **segnale medio**.
- **Problemi del sito (dal codice):**
  - viewport: **ASSENTE**.
  - http -> https: **nessun redirect** (resta su http, Chrome scrive "Non sicuro"). Su https il certificato **non è valido** ("Hostname mismatch, certificate is not valid for 'www.luper.eu'").
  - copyright: **nessuna riga di copyright**; header `Last-Modified: Fri, 18 Oct 2019`.
  - doctype `HTML 4.01 Transitional`, impaginazione a tabelle (6 `<table>`), P.IVA in fondo alla pagina.
  - Extra: i due siti del negozio collegato (luperstyleandcuir.net, calzature-pelletteria-vigevano.it) **non risolvono più** (DNS morto).
- **Aggancio:** "Il sito luper.eu è fermo al 2019 e dal telefono non si legge; i due siti del negozio Luper Style and Cuir non si aprono proprio più."

### 3. Pasticceria Dante
- **Settore:** pasticceria e bar, due sedi.
- **Indirizzo:** Via Dante Alighieri 6, Vigevano (sede centrale); seconda sede in Via Madonna Sette Dolori 11 (tel. 0381 73800).
- **Telefono:** 0381 83776 (è anche quello scritto sulla pagina di manutenzione).
- **Email:** non trovata.
- **Prove che è aperta:**
  - Tripadvisor (sede di via Dante): recensioni di **ottobre 2025** e aprile 2025, mostrata come "aperto" - https://www.tripadvisor.it/Restaurant_Review-g1050288-d5264081-Reviews-or30-Pasticceria_Dante-Vigevano_Province_of_Pavia_Lombardy.html
  - Sluurpy (via Madonna Sette Dolori): scheda aggiornata a dic 2025, circa 1.491 voti - https://www.sluurpy.it/vigevano/ristorante/218343/pasticceria-dante
  - PagineGialle: orari completi (lun, mer, ven-dom 7:30-20:00) e 3 recensioni.
- **Problemi del sito (dal codice):**
  - l'intera homepage è questa, 372 byte:
    `<title>Pasticceria Dante - Vigevano</title> ... <h1>Sito in manutenzione</h1> <p>Per contattarci chiama il 0381 83776 ...`
  - header `Last-Modified: Tue, 09 Apr 2024`: **in manutenzione da circa 19 mesi**.
  - viewport: **ASSENTE**, doctype assente.
  - http -> https: **nessun redirect** (http risponde 200). Il certificato https è valido (scade 04-12-2026).
  - copyright: nessuno. Il link che PagineGialle mette per il sito (`/it`) dà **errore 404**.
- **Aggancio:** "Chi clicca 'sito web' da PagineGialle o Google trova 'Sito in manutenzione' da aprile 2024, oppure una pagina di errore: niente torte, niente orari, niente seconda sede."

### 4. Studio Dentistico Dott. Lorenzo Capra
- **Settore:** studio odontoiatrico (team con Dr. Lorenzo Capra, Dr. Gianluca Capra, Dr.ssa Roberta Arrigoni; sedi a Vigevano e Milano).
- **Indirizzo:** Via Gioacchino Rossini 8, 27029 Vigevano (PV).
- **Telefono:** 0381 84312.
- **Email:** info@studiodentisticocapra.it.
- **P.IVA:** 01900700186.
- **Prove che è aperto:**
  - trova-aperto.it: orari (gio 10-12 e 14:30-19:30, ven 10-12), scheda aggiornata il 21-11-2025 - https://trova-aperto.it/vigevano/dott-lorenzo-capra-2804979
  - DocDental: 5 stelle su 6 recensioni (senza data) - https://docdental.it/cliniche-dentali/vigevano/
  - PagineGialle e PagineBianche lo danno attivo, senza recensioni.
  - **Segnale medio:** non ho trovato recensioni con data recente.
- **Problemi del sito (dal codice):**
  - viewport: presente `<meta name="viewport" content="width=device-width, initial-scale=1.0">` (quindi il sito si adatta al cellulare).
  - http -> https: **nessun redirect** (http risponde 200). Certificato https valido (scade 29-01-2027).
  - copyright: "**©2018** Studio Dentistico Dott. Lorenzo Capra - P.IVA 01900700186".
  - `<meta name="generator" content="WordPress 4.7.29">` (ramo del 2016-17, senza aggiornamenti di sicurezza), jQuery **1.7.2** (2012).
- **Aggancio:** "Il sito dello studio gira su una versione di WordPress del 2017 che non riceve più aggiornamenti di sicurezza, e il copyright è fermo al 2018."
- Nota: è il candidato **meno grave sul piano visivo**; il problema è soprattutto tecnico.

### 5. Pala, Paletta e Forchetta
- **Settore:** gastronomia, panetteria e bar (anche menu vegetariano/vegano).
- **Indirizzo:** Via Cesare Battisti 7, 27029 Vigevano (PV).
- **Telefono:** 0381 690716.
- **Email:** non trovata. Ha una pagina Facebook: https://www.facebook.com/palapalettaeforchetta
- **Prove che è aperta:**
  - Restaurant Guru: "open", orari lun-ven 7:30-15:30, sab 7:30-15; ultima recensione Google di circa 2 anni fa - https://restaurantguru.com/Pala-Paletta-e-Forchetta-Vigevano
  - Altraopinione: 132 recensioni, orari regolari, nessuna chiusura - https://altraopinione.org/negozio/vigevano/pala-paletta-e-forchetta/
  - Tripadvisor: 3,7 su 134 recensioni.
  - **Segnale medio:** gli orari cambiano da una fonte all'altra; prima di chiamare conviene controllare su Google Maps.
- **Problemi del sito (dal codice):**
  - la homepage restituisce solo il testo `Please stand by while configuration is in progress.` (52 byte), con `Last-Modified: Mon, 05 Feb 2024`.
  - il link che PagineGialle mette per il sito (`/new/`) dà **404 Not Found** (nginx).
  - viewport: **ASSENTE**, doctype assente.
  - http -> https: **nessun redirect**; su https il certificato è **autofirmato** (Chrome mostra l'avviso rosso a tutta pagina).
  - copyright: nessuno.
- **Aggancio:** "Chi apre il vostro sito vede una riga in inglese, 'Please stand by', ferma da febbraio 2024; se ci arriva in https, Chrome lo avvisa che il sito non è sicuro."

### 6. Autoscuola Carrobbio di Marangon Enrico
- **Settore:** autoscuola.
- **Indirizzo:** Via Carrobbio 11, 27029 Vigevano (PV).
- **Telefono:** 0381 76315.
- **Email:** autocarrobbio@tiscalinet.it, autoscuolacarrobbio@gmail.com (dal sito).
- **Prove che è aperta:**
  - il sito stesso riporta "Ultimo aggiornamento: 22-11-24" e l'header `Last-Modified: Fri, 22 Nov 2024`.
  - PagineGialle la elenca (senza orari né recensioni) - https://www.paginegialle.it/vigevano-pv/marangon-enrico
  - **Segnale debole:** nessuna recensione con data, nessun profilo social trovato. Prima di chiamare va confermata su Google Maps.
- **Problemi del sito (dal codice):**
  - viewport: **ASSENTE**; **doctype assente** (il browser va in "quirks mode").
  - http -> https: la versione http **non reindirizza** (al primo controllo rispondeva 200 senza redirect). Certificato https valido (scade 07-12-2026).
  - copyright: "Copyright © 2004 - 20 2 4 Ultimo aggiornamento: 22-11-24" (l'anno è scritto spezzato a mano).
  - 11 tag `<font>`, impaginazione a tabelle: è il layout del 2004.
  - Nota tecnica: dopo qualche richiesta il server (IIS su Aruba) risponde "HTTP Error 999.0" per anti-flood. È normale, non è un guasto.
- **Aggancio:** "Il vostro sito è quello del 2004: dal cellulare, che è da dove vi cercano i ragazzi di 18 anni, si legge col pinch-zoom."

### 7. Verticalport
- **Settore:** vendita e posa di tende da sole, zanzariere, porte, serramenti, tapparelle.
- **Indirizzo:** Corso Genova 80, 27029 Vigevano (PV).
- **Telefono:** 0381 82331.
- **Email:** v.verticalport@alice.it (dal secondo sito).
- **P.IVA:** 01521090181.
- **Prove che è aperta:** orari su PagineGialle (lun-ven 9-12 e 15-19, sab 9-12) - https://www.paginegialle.it/verticalport ; certificati di entrambi i domini rinnovati (scadenza nov 2026). Una sola recensione (2/5, di oltre 2 anni fa). **Segnale medio-debole.**
- **Problemi del sito verticalport.it (dal codice):**
  - viewport: **ASSENTE**.
  - http -> https: sì, reindirizza; certificato valido.
  - copyright: "Copyright © 2026 - VerticalPort - P.I. 01521090181" (probabilmente generato in automatico).
  - jQuery **1.7.1** (2011).
- **Attenzione, possibile falso positivo:** PagineGialle rimanda a un **secondo sito, www.verticalportvigevano.com**, più recente (ha il viewport, jQuery 3.7.0, ma contiene ancora un `email@mail.com` del template). L'aggancio quindi è più debole: "Avete due siti, e quello vecchio senza versione mobile è ancora online e indicizzato."
- **Priorità bassa.**

### 8. Ambulatorio Veterinario dei Dottori Calcaterra & Ditrani (sito morto, non vecchio)
- **Settore:** ambulatorio veterinario (Dott.sse Alessandra Calcaterra e Paolina Ditrani).
- **Indirizzo:** Via Gambolina 15, 27029 Vigevano (PV).
- **Telefono:** 0381 348960.
- **Email:** non trovata.
- **Prove che è aperto:** PagineGialle con orari completi (lun-ven 10-12:30 e 15:30-19:30, sab 9:30-12:30) - https://www.paginegialle.it/vigevano-pv/veterinaria/ambulatorio-veterinario-dei-dottori-calcaterra-a-e-ditrani-p ; presente anche su veterinari.it e PagineBianche. Nessuna recensione con data: **segnale medio**.
- **Problemi del sito:** `www.veterinariocalcaterraditrani.it` **non risolve** (DNS fallito, nessuna risposta né su http né su https), ma PagineGialle e Google lo indicano ancora come sito ufficiale. Nessun HTML da analizzare.
- **Aggancio:** "Il sito che compare su PagineGialle e su Google non si apre più: chi vi cerca per un'urgenza trova una pagina di errore."

---

## Scartati (una riga ciascuno)
- Linea Contract, Lomellina Trasporti, Mlegno: il "frameset" segnalato dallo script è la pagina di cortesia di register.it, cioè dominio parcheggiato e non sito aziendale (**falso positivo dello script**).
- Falzoni.it, Euroimpianti.it, Treg.it, Rovesti.it, Tuttoinfissi.it, Solazzo.it: domini omonimi di aziende **non di Vigevano** (Ancona, geotecnica, cosmetici, 3G Electronics...).
- Casa Stopino: sito WordPress aggiornato e responsive, solo il copyright è fermo al 2022: troppo poco.
- Porte DueGi: CMS GuppY ma con viewport e https corretti; problema minore.
- Sabal, Avantium (ex Cerim), Bibo, Angeleri, OMAV, Volber, Falan, LGF Contrafforti, Tecno2, Atom, Dulio, Zago: siti moderni e in buono stato.
- Tipografia Casonato, Caffè Commercio, Prisma, Elettrocalor, Progetto Infissi: dominio parcheggiato/vuoto; serve prima una conferma che l'azienda sia attiva (non fatta).
- Glamhour, Estetica Gerry, Dentoral, Mondetti, Amici della Pizza, Barbulè, Gandolfi Costruzioni, Elettroimpianti BRM: dominio morto; attività non verificata in questo giro.
- Centro Medico Vigevanese: cmvigevano.it reindirizza su un altro sito (chirurgiaestetica.it), quindi non è un caso chiaro.
- Giviesse, Al Bulè, Robiplast, Itiemme, Tre Erre, Caribù, Kahnt, Asilo Mary Poppins: la rete da cui lavoro risponde "Web Filter Violation" (filtro aziendale), **da aprire a mano nel browser**.
- Moreschi (fallita), Gravati (in liquidazione), Officine Meccaniche Vigevanesi (in liquidazione): chiuse o in chiusura.

## Note di metodo
- Lo script `valuta` è stato eseguito solo su CSV temporanei nella scratchpad: `prospect/vigevano.csv` **non è stato toccato**.
- Il segnale "è ancora aperta" è affidabile per ABV (bilancio) e Dante (recensione di ott 2025); per gli altri è medio o debole e conviene un controllo veloce su Google Maps prima di chiamare.
