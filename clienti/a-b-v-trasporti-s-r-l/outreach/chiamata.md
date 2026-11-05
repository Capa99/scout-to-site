# Telefonata con A.B.V. Trasporti — traccia

Guida generale: `outreach/guida-telefonata.md`. Qui solo quello che vale per loro.

## Chi potresti sentire

* Non abbiamo nomi: il sito non cita titolare, soci o referenti, e l'unica email è operativo@abvtrasporti.it (probabilmente l'ufficio che organizza i viaggi).
* Chiedi presto: "Con chi parlo? Chi si occupa del sito?" Se decide il titolare o l'amministratore, serve il suo sì.

## Apertura

> "Buongiorno, sono Federico Manetta, vi avevo scritto per la proposta del nuovo sito. Grazie di avermi richiamato! L'avete vista? Cosa ve ne è sembrato?"

Lascia parlare. Se dicono "il servizio con gru si vede bene" o "dal telefono è comodo", segnatelo: è su quello che si costruisce.

## Le domande per loro

1. **La domanda più importante:** "Qual è il numero giusto da mettere sul sito?"
   * Sul loro sito c'è +39 0381 39470 (gli manca una cifra, forse un refuso).
   * PagineGialle riporta 0381 348970, 0381 42247 e 0381 43100. Lo 0381 42247 sembra anche scritto sulla fiancata del camion blu in foto.
   * La demo usa lo 0381 348970: se è sbagliato, va cambiato subito.
2. "Chi vi ha fatto il sito attuale? Avete un contratto o un canone con qualcuno?" (oggi è fatto con WebSite X5, un programma di circa 15 anni fa)
3. "Cosa intendete con 'Toscana diretta'? È una linea regolare? Ogni quanto e verso quali città?" (sul sito c'è solo lo slogan)
4. "I servizi fieristici li fate ancora?" (nel loro elenco ci sono, ma nella demo li abbiamo tolti perché l'unico riferimento è a Expo 2015)
5. "La sede legale è ancora in Corso Pavia 28 e quella operativa in Via Perugino 48/50?"
6. "Le foto del sito sono vostre? Ne avete di più grandi o più recenti?" Quelle attuali sono piccole (circa 450 px) e alcune sono scansioni: servono foto nuove di flotta, deposito e gru al lavoro.
7. "Avete il logo in un file originale (PDF, AI, SVG)?" Nella demo è una nostra ricostruzione.
8. "Per quando vi piacerebbe averlo?"

## Se chiedono il prezzo

> "Il sito completo come quello che avete visto costa 590 euro, una volta sola: metà all'inizio e metà quando è online. Il dominio resta vostro e non ci sono canoni."

Sono una S.r.l., quindi sostituto d'imposta: trattengono la ritenuta del 20% (su 590 € bonificano 472 € e versano 118 € con F24). Al telefono basta "vi mando tutto per iscritto nel riepilogo".

## Cose da NON promettere a loro

* Un calcolo automatico dei preventivi o un archivio delle richieste. Un semplice modulo contatti invece è nel listino "su richiesta": se lo chiedono, "si può fare, lo metto nel riepilogo".
* La versione inglese (nella demo non c'è: se la chiedono, "vi preparo una proposta precisa").
* Tracciamento delle spedizioni o un'area clienti.
* Dati sui mezzi (portata delle gru, numero di camion, certificazioni) finché non ce li danno loro.

## Chiusura

> "Allora vi mando per email il riepilogo con cosa comprende, prezzo e tempi. Lo mando a operativo@abvtrasporti.it o c'è un indirizzo più adatto?"

Se preferiscono vedervi: la sede operativa è in Via Perugino 48/50 a Vigevano. Proponi due giorni feriali e un orario.

## Dopo

```
.venv\Scripts\python.exe outreach\outreach.py registra "A.B.V. Trasporti S.r.l." --stato interessato --canale telefono --consenso "telefonata del GG/MM: ..."
```

e incolla a Claude i tuoi appunti.
