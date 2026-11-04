# Guida: quando un prospect ti chiama (o lo chiami tu)

Lo scopo della prima chiamata **non è vendere**: è ascoltare, capire cosa gli serve davvero e
fissare il passo successivo. Prezzi e dettagli si mettono per iscritto dopo, con calma.
Per ogni cliente l'agent Outreach prepara anche `clienti/<azienda>/outreach/chiamata.md` con le
domande specifiche.

## Prima (tienilo a portata)

* La demo aperta sul telefono o sul PC.
* I numeri di `outreach/listino.md`: 590 €, metà subito e metà alla pubblicazione, 2 giri di
modifiche, circa 2 settimane da quando arrivano i materiali.
* Un foglio per gli appunti.

## Apertura

> "Buongiorno, grazie di avermi richiamato! Avete avuto modo di guardare la proposta? Cosa ve ne è sembrato?"

Poi **lascia parlare loro**. Quello che dicono adesso (cosa piace, cosa cambierebbero) è la cosa più utile di tutta la chiamata.

## Domande da fare (quelle che vengono naturali, non un interrogatorio)

1. "Chi si occupa oggi del sito? Lo aggiornate voi?"
2. "Cosa vi serve aggiornare spesso?" (menu, orari, eventi, prodotti, offerte)
3. "Chi vi ha fatto il sito attuale? Avete un contratto o un canone con qualcuno?"
4. "Avete foto più recenti o più grandi?"
5. "I dati sul sito sono ancora giusti?" (orari, indirizzo, telefoni)
6. "Chi decide per il sito?" (se non è chi sta parlando, serve anche il suo sì)
7. "Per quando vi piacerebbe averlo?"

## Se chiedono il prezzo

> "Il sito completo come quello che avete visto costa 590 euro, una volta sola: metà all'inizio e
> metà quando è online. Il dominio resta intestato a voi e non ci sono canoni."

Ritenuta, ricevuta, dettagli fiscali: "Vi mando tutto per iscritto nel riepilogo."

## Se chiedono cose che non hai deciso

> "Sì, si può fare in più modi. Vi preparo una proposta precisa insieme al riepilogo."

Meglio una risposta pensata domani che una promessa sbagliata oggi.

## Cosa NON promettere

* Di comparire primi su Google.
* Date precise prima di avere i materiali.
* Funzioni non previste dal listino (prenotazioni online, shop, newsletter, area riservata).
* Sconti: "ci penso e vi faccio sapere" (massimo 10%, e solo se decidi tu dopo).

## Se chiedono di te

Semplice e sincero:

> "È un'attività che sto avviando nella mia zona: la demo che avete visto è proprio un esempio di come lavoro."

Non serve parlare del lavoro da dipendente. Mai inventare clienti o anni di esperienza nel settore.

## Domande difficili

* **"Abbiamo già qualcuno che ci segue."** → "Nessun problema: se volete tenete la demo come idea, e se un giorno cambiate mi trovate qui."
* **"Ci pensiamo."** → "Certo. Vi mando comunque il riepilogo per iscritto così avete tutto sotto mano. Va bene se vi risento tra una settimana?"
* **"Costa troppo."** → "Capisco. Cosa vi sembrerebbe giusto, e cosa togliereste?" (ascolta, non scontare al telefono)
* **"Come avete avuto il nostro indirizzo?"** → "Dal vostro sito, dalla pagina contatti."
* **"Possiamo vederci?"** → Sì, sempre: proponi due giorni e un orario.

## Chiusura: fissa sempre il passo dopo

> "Allora vi mando per email un riepilogo con cosa comprende, prezzo e tempi, così lo avete per
> iscritto. L'indirizzo giusto è …?"

## Dopo la chiamata

1. Scrivi subito gli appunti in `clienti/<azienda>/outreach/ricevute/AAAA-MM-GG-telefonata.md`
(o incollali a Claude).
2. Registra il contatto con le loro parole come consenso:
`outreach.py registra "<nome>" --stato interessato --canale telefono --consenso "telefonata del GG/MM: ..."`
3. L'agent prepara l'email di riepilogo: la rileggi, la approvi, la mandi tu.

