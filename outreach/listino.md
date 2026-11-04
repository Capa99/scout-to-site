# Listino e regole commerciali

Fonte unica per prezzi e condizioni: l'agent Outreach non può promettere nulla che non sia qui.
Per cambiare un prezzo modifica questo file (e fai il push).

## Prezzi (senza IVA: prestazione occasionale)

| Voce | Prezzo | Cosa include |
|---|---|---|
| **Sito completo** | **590 €** una tantum | Homepage + fino a 5 pagine interne, nello stile della demo; adattato a telefono e tablet; testi e foto del cliente (riordinati e corretti); link diretti a telefono, email e WhatsApp (modulo contatti su richiesta); mappa; HTTPS; ottimizzazione velocità; base SEO (titoli, descrizioni, Google Search Console); 2 giri di modifiche prima della pubblicazione; messa online sul loro dominio. |
| **Canone** (solo con partita IVA) | **15 €/mese** | Hosting, certificato HTTPS, backup. Il dominio resta a carico del cliente. **Le modifiche non sono incluse.** |
| **Modifiche dopo la pubblicazione** | 30 € per mezz'ora, a preventivo | Cambi di testi, foto, orari, nuove voci. Preventivo sempre prima di iniziare. |
| **Pagina in più** | 60 € a pagina | Oltre le 5 incluse. |
| **Statistiche delle visite (senza cookie)** | **40 €** una tantum | Cloudflare Web Analytics sul sito, account intestato al cliente, privacy aggiornata, 10 minuti per mostrare come leggere i numeri (visite, pagine più viste, da dove arrivano). Niente banner dei cookie. **Mai Google Analytics** (serve il banner con il consenso). |

## Finché non c'è la partita IVA
- **Niente canone.** Il dominio lo registra e lo paga il cliente; il sito sta su Netlify (piano gratuito).
- Modifiche dopo la pubblicazione solo a preventivo, una tantum.
- L'agent Consegna lo sa: con `partita_iva=` vuoto in `consegna/dati-personali.txt` l'accordo esce senza canone.

## Pagamento
- **50% all'accettazione, 50% alla pubblicazione.**
- **Prestazione occasionale con ritenuta d'acconto del 20%:** se il cliente è un'azienda o un
  professionista (sostituto d'imposta), trattiene il 20% e lo versa con F24. Esempio: su 590 € il
  cliente bonifica 472 € e versa 118 € di ritenuta. Il prezzo che si comunica resta **590 €**.
- Niente IVA da aggiungere. In email si scrive "590 € (prestazione occasionale, senza IVA)".

## Regole fisse
- **Il dominio si registra a nome del cliente:** resta suo anche se un giorno cambia fornitore.
- **Sconto massimo 10%** e solo se l'utente lo autorizza caso per caso. Mai sconti spontanei.
- **Tempi:** demo già pronta; sito completo online in circa 2 settimane da quando arrivano testi e foto.
- **Niente promesse** su posizionamento in Google, numero di clienti o vendite.
- Domande contrattuali, legali o fiscali specifiche: si risponde "le faccio sapere" e si gira all'utente.

## Hosting e canone
- **Senza canone** (oggi): i siti stanno sul Netlify gratuito dell'utente. Netlify lo permette anche per
  siti di clienti, purché **l'hosting non venga fatto pagare**.
- **Con il canone** (dopo la partita IVA): far pagare l'hosting è "rivendita", e Netlify chiede un
  **piano a pagamento**. Il suo costo va coperto dai canoni: conviene da 4-5 clienti in su.
  Alternativa gratuita che consente l'uso commerciale: Cloudflare Pages.
- In ogni caso ogni sito ha il suo repo su GitHub: se Netlify chiude o cambia regole, si ripubblica
  altrove e si cambiano due righe del DNS del cliente.

## Da chiarire con il commercialista (promemoria per l'utente)
- I canoni mensili sono entrate ricorrenti: con più clienti l'attività diventa "abituale" e serve la
  partita IVA (regime forfettario). Da verificare ai primi 2-3 clienti.
- Verificare il contratto di lavoro con Sydema (esclusiva / non concorrenza) prima del primo incasso.
