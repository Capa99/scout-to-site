# Stile TRATTORIA

**Settori:** ristoranti, trattorie, agriturismi, bar e caffè, pasticcerie, gelaterie, cantine,
B&B e piccoli hotel.
**Sensazione:** entrare nel locale. Calore, materia, profumo di cucina. Facile prenotare.

## Caratteri
- Titoli: **Fraunces** 600 (il corsivo per una parola calda: *casa*, *tradizione*, *stagione*).
- Testo: **Work Sans** 400.

## Colori
- Sfondo carta `#f7f1e8`, testo bruno `#2b2118`, primario mattone `#6b2d1f`, accento terracotta `#a8452c`.
  Se il locale ha colori propri (insegna, tovaglie, logo), usali in `tema.css`.

## Regole
- **Il bottone "Prenota" è sempre visibile** (testata) e porta a telefono/WhatsApp o modulo.
  Su mobile il telefono è un link `tel:` cliccabile.
- **Menu in HTML vero** (`.menu-list` con `.menu-item` e `.price`), mai PDF o foto del menu.
  Prezzi solo se presenti nel brief.
- **Orari** sempre in vista (`.hours`), anche nel footer.
- **Foto:** piatti dall'alto o a 45°, sala, persone al lavoro, territorio. Formato quadrato per i piatti.
- **Angoli morbidi** e bottoni a pillola; un tocco grafico ammesso (`.stamp` con "dal 1985", "km 0"...)
  solo se il fatto è nel brief.
- **Niente:** sfondi neri da fine dining se il locale è una trattoria; foto stock di piatti.

## Homepage tipo
1. Testata con logo, menu (Il locale, Menu, Camere se c'è, Dove siamo) e bottone "Prenota".
2. Hero a immagine grande (piatto o sala) con titolo caldo e orari/telefono sotto.
3. La storia in due righe + foto dei titolari o della cucina.
4. Il menu: 4-8 piatti simbolo con descrizione.
5. Galleria quadrata (`.strip`).
6. Recensioni solo se presenti nelle fonti (mai inventate).
7. Dove siamo: indirizzo, orari, mappa su richiesta, parcheggio.
