# Telefonata con Luper — traccia

Guida generale: `outreach/guida-telefonata.md`. Qui solo quello che vale per loro.

## Dove chiamare

* **0381 20019**, Corso Novara 135 (angolo Corso Ugo La Malfa), Vigevano.
* Orari non noti: chiama in orario d'ufficio, evitando l'ora di pranzo.

## Chi potresti sentire

* Il catalogo spazzole dice che lo spazzolificio fu fondato nel 1973 dai coniugi Persendi e che oggi collaborano i figli Ambrogio e Andrea; i registri danno "Luper s.n.c. di Ambrogio e Andrea Persendi", il sito "di Magnaga Giuseppina & C.". Probabilmente decide uno dei due fratelli, ma non darlo per scontato: chiedi "Con chi parlo? Chi si occupa del sito?"

## Apertura

> "Buongiorno, sono Federico Manetta, vi avevo scritto per la proposta del nuovo sito. Grazie di avermi richiamato! L'avete vista? Cosa ve ne è sembrato?"

Lascia parlare. Se dicono "le schede dei prodotti sono comode" o "dal telefono si legge", segnatelo: è su quello che si costruisce.

## Le domande per loro

1. **La domanda più importante:** "Chi vi ha fatto il sito attuale? Avete un contratto o un canone con qualcuno?" (dominio e posta sono su register.it; il sito è fermo al 2019 e il certificato https non è del loro dominio)
2. "Qual è la ragione sociale giusta da scrivere nel sito?" (sito: "di Magnaga Giuseppina & C."; registri: "di Ambrogio e Andrea Persendi")
3. "Il negozio Luper Style and Cuir esiste ancora?" (i suoi due siti non esistono più; nella demo non c'è)
4. "Usate ancora il fax? Quale numero?" (sito 0381 325175, cataloghi 0381 310732; nella demo non c'è)
5. "Che orari fate?" (nella demo c'è solo "Chiamateci per orari e disponibilità")
6. "La casella info@luper.eu la leggete?"
7. "Le schede dei prodotti vanno bene così? Ci sono articoli che non fate più o novità?" I cataloghi PDF non hanno data. In particolare: le foto del crine doppio super (con e senza pelo di capra) e le misure degli Smerigliatori Automatic (il catalogo dice sia 140 sia 142 mm).
8. "Siete ancora distributori di zona di Kenda Farben e Barbour Campbell?" (nella demo i marchi non ci sono; se sì e lo vogliono, si aggiungono)
9. "Spedite ancora all'estero?" (il catalogo dice "in tutti i paesi del mondo"; nella demo non c'è)
10. "Avete il logo in un file originale?" Quello della demo è una ricostruzione. "Avete foto recenti in alta risoluzione della sede o del laboratorio?" (senza persone, o con il loro consenso)
11. "Per quando vi piacerebbe averlo?"

## Se chiedono il prezzo

> "Il sito completo come quello che avete visto costa 590 euro, una volta sola: metà all'inizio e metà quando è online. Il dominio resta vostro e non ci sono canoni."

Fino a 5 pagine interne sono incluse; la pagina Prodotti conta come una. Pagine in più: 60 € l'una (dal listino).

Sono una s.n.c., quindi sostituto d'imposta: trattengono la ritenuta del 20% (su 590 € bonificano 472 € e versano 118 € con F24). Al telefono basta "vi mando tutto per iscritto nel riepilogo".

## Cose da NON promettere a loro

* Catalogo online con prezzi, ordini o area riservata per i clienti.
* Versione inglese o in altre lingue (i cataloghi sono in IT/EN/FR/ES): se la chiedono, "vi preparo una proposta precisa".
* Di sistemare la posta o il dominio su register.it senza le loro credenziali.
* Date precise prima di avere logo, foto e conferme sulle schede.

## Chiusura

> "Allora vi mando per email il riepilogo con cosa comprende, prezzo e tempi. Lo mando a info@luper.eu o c'è un indirizzo più adatto?"

Se preferiscono vedervi: Corso Novara 135. Proponi due giorni feriali e un orario.

## Dopo

```
.venv\Scripts\python.exe outreach\outreach.py registra "Luper s.n.c." --stato interessato --canale telefono --consenso "telefonata del GG/MM: ..."
```

e incolla a Claude i tuoi appunti.
