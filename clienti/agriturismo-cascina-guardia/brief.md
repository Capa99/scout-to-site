# Brief demo — Agriturismo Cascina Guardia

Prospect dallo Scout: **punteggio 75, ALTA**. Sito: http://www.agriturismocascinaguardia.it
Brief scritto il 2026-11-04 da `contenuti.md` e dai sorgenti in `sorgente/`.
Controllato a mano: nel sorgente **manca il meta viewport** (pagina non adattata al telefono),
footer "© 2017", 8 tag `<font>`. Il certificato HTTPS non valido viene dallo Scout (da riverificare
aprendo https://www.agriturismocascinaguardia.it).

## Chi sono
Agriturismo nel cuore della Lomellina, a Vigevano, a pochi passi dal Parco del Ticino.
L'azienda agricola nasce nel **1988** come allevamento di fagiani, poi di struzzi; l'agriturismo
apre il **15 novembre 1999**. Dal 2006 alleva bovini, suini, avicoli e selvaggina; dal 2009 un ettaro
è coltivato a ortaggi, piccoli frutti, erbe officinali e fiori. Titolare: Az. Agrituristica Cascina
Guardia di Goldin Roberto. Il sito è **molto attivo**: post di menu ed eventi ogni settimana (ottobre 2026),
firmati "Emma".

## Cosa offrono (con le loro parole)
- **Ristorante a km zero**: salumi di produzione propria, risotti, paste e dolci fatti in casa, vini dell'Oltrepò.
  Menù fisso degustazione 40 € (percorso leggero 30 € con acqua e calice), menù alla carta, menù piccoli ospiti 25 €.
- **Oasi naturale con animali** ("oasi faunistica"): daini, cigni neri, zebra, cammello, asini, cicogna,
  procione, tartaruga… Formula **"Ape-Nature"**: sabato e domenica 10:00–14:00, visita agli animali +
  aperitivo rinforzato, adulti 16 €, bambini fino a 11 anni 12 €.
- **Feste di compleanno per bambini** (aprile–ottobre, gio–dom 15:30–18:30, da 25 invitati, 25 € a persona).
- **Cerimonie 2027** (60 € adulti, 38 € bambini 3-10 anni, tutto incluso) e **matrimoni** (da 75 € a persona,
  anche con l'intera cascina in esclusiva, mini club per bambini, cake design).
- **Eventi**: Pranzo di Natale 25/12 (75 €), Cena di San Silvestro 31/12 (75 €), Halloween con gli animali.
- **Prodotti propri**: carni avicole, selvaggina, verdure trasformate, piccoli frutti e confetture, insaccati.

## A chi vendono
Famiglie con bambini (animali, mini club, feste), coppie e gruppi da Milano/Pavia/Novara, sposi e
famiglie per cerimonie (battesimi, comunioni), gruppi oltre 12 persone anche in settimana.

## Punti di forza (dalle fonti)
- Unico nel suo genere in zona: **ristorante + oasi con animali** in un solo posto.
- Filiera propria e km zero (allevamento, orto, salumi, confetture).
- Storia lunga e concreta: 1988 azienda agricola, 1999 agriturismo.
- Pensato per i bambini: mini club, animazione, menù dedicati. Cani piccoli e medi ammessi.

## Tono di voce consigliato
Caldo e familiare, concreto. Frasi brevi, niente punti esclamativi multipli né maiuscolo
(oggi ce ne sono molti, con refusi). Le parole chiave: *oasi*, *km zero*, *tradizione lombarda*,
*famiglie*, *animali*.

## Identità visiva
- **Logo:** `img/logo-01-logo-cascina-guardia-2015.png`, scritta corsiva grigia "Agriturismo Cascina Guardia",
  piccolo (250×70). Nella demo va ricomposto come testo (wordmark).
- **Colori del sito attuale:** turchese `#0695a6`, arancio `#ff7302`, giallo `#ffa902`: non legati al luogo.
  Proposta presa dalle foto: verde bosco `#2f4a2a` (parco), terracotta `#b4532a` (facciata e mattoni),
  carta `#f7f1e8`.

## Immagini per la demo
Foto vere e buone, ma in formato striscia 1024×400 (erano slide): si usano larghe e basse o ritagliate.
| Uso | File |
|---|---|
| Copertina | `05-slide1.jpg` (la cascina e il viale), alternativa `06-slide7.jpg` (daini al laghetto) |
| Cucina | `04-slide-cucina.jpg` (gnocchi), `18-slide6.jpg` (salumi), `02-slide-prodotti.jpg` (frutta) |
| Sala / cerimonie | `14-slide4.jpg` (sala apparecchiata), `03-ristorante-cascina-guardia.jpg`, `07-slide-matrimoni.jpg` |
| Oasi e animali | `06-slide7.jpg`, `10-slide8.jpg` (cerbiatto), `13-slide9.jpg` (procione), `15-slide11.jpg` (tartaruga), `17-slide12.jpg` (cigni neri), `22-slide15.jpg` (cicogna), `24-slide17.jpg` (zebra e cammello), `25-slide10.jpg` (asini), `23-slide16.jpg` (anatre mandarine) |
| Esterni | `12-slide3.jpg` (facciata con glicine), `20-stephane5.jpg` (viale, verticale) |

**Da scartare:** `08` (volantino Halloween), `11` (cartolina matrimonio), `09` (piccola), `16` (doppione di `04`),
`26-sfondo.jpg`, `19` e `21` (meno nitide).

## Struttura della demo
**Homepage:** testata con "Prenota" (telefono) → hero con la cascina e "Un'oasi naturale nel cuore della
Lomellina" + orari e telefono → storia in due righe (1988, 1999, km zero) → la cucina (menù del mese in HTML)
→ l'oasi e gli animali (galleria quadrata con lightbox + formula Ape-Nature) → feste e cerimonie (3 schede che
portano alla pagina interna) → dove siamo (indirizzo, orari, telefono/WhatsApp, mappa su richiesta).
**Pagina interna:** `feste.html` — cerimonie, matrimoni, compleanni bambini, Natale e Capodanno, con prezzi e condizioni.

## Cosa deve mostrare la demo
- Si legge bene dal telefono (oggi no): bottone "Chiama e prenota" sempre a portata di pollice.
- HTTPS valido (oggi il browser segnala il certificato).
- Menu e prezzi in testo vero, leggibili, non dentro post del blog.
- Orari chiari in un punto solo (oggi sono sparsi e in contrasto tra pagine).
- Le foto degli animali valorizzate: è il loro punto di forza unico.

## Da verificare
- **Orari:** la home dice pranzo sab/dom/festivi dalle 12:45 e mer-ven solo gruppi; il post del 29/10 dice
  anche cena venerdì, sabato e domenica e carta venerdì e sabato. Nella demo uniti, da confermare.
- **Indirizzo:** "Strada Cascina Guardia 78" nel footer, "Strada Cascine Barbavara" nella pagina contatti.
- **Telefoni:** 348 29 21 234 (prenotazioni), 339 783 4937; 328 910 36 17 compare solo per Halloween.
  Lo 0381 21451 della guida regionale non c'è sul sito.
- **Email:** info@agriturismocascinaguardia.it ed emmagold@me.com (personale: non usarla per il primo contatto).
- **Nuovo dominio?** il footer cita www.cascinaguardia.it: controllare se esiste un secondo sito.
- **Importante per la vendita:** pubblicano menu ed eventi ogni settimana da soli (WordPress). Un sito
  statico deve permettergli di continuare a farlo, altrimenti è un passo indietro: da affrontare prima
  dell'accordo (editor semplice per la pagina eventi, o modifiche incluse).

## Fonti
Pagine: `/`, `/home/`, `/azienda/`, `/prodotti/`, `/ristorante/`, `/cucina/`, `/parco/`, `/matrimoni/`,
`/contatti/`, post eventi di ottobre 2026 (vedi `contenuti.md`).
