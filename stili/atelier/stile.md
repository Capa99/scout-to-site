# Stile ATELIER

**Settori:** moda, abiti da sposa e cerimonia, gioielli, calzature, bellezza, design d'interni,
fotografi, wedding planner, boutique hotel.
**Sensazione:** rivista di moda, lusso discreto. Il prodotto e le foto sono protagonisti, la
grafica si fa da parte.

## Caratteri
- Titoli: **Cormorant Garamond** 500 (il corsivo `<em>` si usa per una parola chiave per titolo, mai di più).
- Testo: **Jost** 300; per etichette e bottoni Jost 400 maiuscolo spaziato.

## Colori (predefiniti, da sostituire con quelli del cliente in `tema.css`)
- Sfondo avorio `#faf7f2`, superficie `#f1ebe2`, testo `#1d1d1b`, accento bronzo `#9c7c56`.
- Il colore del cliente va in `--c-accent`; il primario resta scuro (nero o inchiostro), a meno che
  il marchio non abbia un colore scuro forte (es. un verde bosco può diventare `--c-primary`).

## Regole
- **Spazio bianco abbondante:** le sezioni respirano (`--section` grande). Mai più di 2-3 elementi per riga su desktop.
- **Foto:** formato verticale 3:4 per i prodotti/abiti, strisce larghe per le atmosfere.
  Niente bordi, niente ombre, niente angoli arrotondati.
- **Titoli corti:** 3-7 parole. Sopra ogni titolo un'etichetta `.eyebrow` (es. "Collezioni").
- **Linee sottili** (`.rule`) al posto di decorazioni.
- **Bottoni:** rettangolari, maiuscolo spaziato, uno solo principale per schermata.
- **Logo:** se il logo è un lettering semplice e il PNG è piccolo, ricomponilo con `.wordmark`.
- **Niente:** gradienti colorati, icone, emoji, testo centrato lungo, più di 2 caratteri.

## Homepage tipo
1. Testata leggera (wordmark al centro o a sinistra, menu corto, bottone "Prenota un appuntamento").
2. Hero a immagine grande (`.hero--image`) oppure divisa (`.hero--split`) con foto verticale.
3. Introduzione: citazione o due righe di filosofia (`.quote`) + firma del fondatore.
4. Collezioni / servizi: griglia di schede verticali (`.grid--3` di `.card`).
5. Fascia scura (`.section--dark`) con racconto + foto (eventi, laboratorio, sartoria).
6. Atelier / contatti con mappa su richiesta e invito all'appuntamento.
7. Footer scuro.
