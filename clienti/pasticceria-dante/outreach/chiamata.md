# Telefonata con Pasticceria Dante — traccia

Guida generale: `outreach/guida-telefonata.md`. Qui solo quello che vale per loro.

## Dove chiamare

* **Via Dante 6:** 0381 83776, il numero scritto sulla pagina "Sito in manutenzione". Chiuso martedì e giovedì (da PagineGialle).
* **Via Madonna Sette Dolori 11:** 0381 73800. Chiuso il martedì.
* Al banco c'è gente: evita le ore della colazione e dell'aperitivo. Meglio metà mattina o primo pomeriggio.

## Chi potresti sentire

* Il registro LEI riporta "Pasticceria Dante di Milanesi Annamaria e C. S.a.s.": la titolare potrebbe essere lei. Il vecchio sito invece parlava di "famiglia Rizzi". Non dare per scontato nessun nome: chiedi "Con chi parlo? Chi si occupa del sito?"
* Se decide qualcun altro, serve il suo sì.

## Apertura

> "Buongiorno, sono Federico Manetta, vi avevo scritto per la proposta del nuovo sito. Grazie di avermi richiamato! L'avete vista? Cosa ve ne è sembrato?"

Lascia parlare. Se dicono "le torte si vedono bene" o "finalmente ci sono gli orari", segnatelo: è su quello che si costruisce.

## Le domande per loro

1. **La domanda più importante:** "Perché il sito è rimasto in manutenzione? Chi ve lo gestiva?"
   * Se c'è ancora qualcuno con un contratto o un canone, segnalo: il dominio e l'hosting vanno recuperati da lì.
   * Se "non sappiamo più chi l'ha fatto": va capito chi ha in mano il dominio dantevigevano.it e la posta (le email info@ passano dallo stesso server del sito).
2. "La casella info@dantevigevano.it la leggete ancora?" (era sul vecchio sito, oggi non compare da nessuna parte)
3. "Gli orari sono questi?" Via Dante: chiuso martedì e giovedì, gli altri giorni 7:30-20:00. Via Madonna Sette Dolori: chiuso il martedì, gli altri giorni 7:30-20:30. Tutti da PagineGialle: vanno confermati, chiusure per ferie comprese.
4. "Fate ancora panettoni, colombe e i box regalo Dante?" (sono nella demo, presi dal sito del 2023)
5. "Fate ancora catering, pranzo, consegne o lo shop online?" Nella demo non ci sono perché non sapevamo se fossero ancora attivi. Se sì, si aggiungono.
6. "Avete foto recenti di torte e vetrine?" Quelle della demo sono del vostro sito del 2017-2022 e le torte sono piccole (640 px).
7. "Avete il logo in un file originale (PDF, AI, SVG)?" Quello della demo è il piccolo PNG del sito attuale.
8. "Il testo sul Dolceriso va bene così?" Nella demo l'abbiamo riscritto in breve: i testi del libro «Sulla punta della lingua» non si possono ripubblicare senza permesso. Se hanno i diritti del libro, si può valutare di riprenderne una parte.
9. "Per quando vi piacerebbe averlo? Prima di Natale, per panettoni e box regalo?"

## Se chiedono il prezzo

> "Il sito completo come quello che avete visto costa 590 euro, una volta sola: metà all'inizio e metà quando è online. Il dominio resta vostro e non ci sono canoni."

Sono una S.a.s., quindi sostituto d'imposta: trattengono la ritenuta del 20% (su 590 € bonificano 472 € e versano 118 € con F24). Al telefono basta "vi mando tutto per iscritto nel riepilogo".

## Cose da NON promettere a loro

* Shop online, ordini o pagamenti delle torte dal sito.
* Che il sito sia online per Natale se testi, foto e accesso al dominio non arrivano entro metà novembre.
* Di recuperare da soli il dominio o la posta senza le credenziali del vecchio fornitore.
* Di gestire i loro social.

## Chiusura

> "Allora vi mando per email il riepilogo con cosa comprende, prezzo e tempi. Lo mando a info@dantevigevano.it o c'è un indirizzo che leggete di più?"

Se preferiscono vedervi: passa al banco in via Dante, meglio di mattina tardi, evitando martedì e giovedì.

## Dopo

```
.venv\Scripts\python.exe outreach\outreach.py registra "Pasticceria Dante" --stato interessato --canale telefono --consenso "telefonata del GG/MM: ..."
```

e incolla a Claude i tuoi appunti.
