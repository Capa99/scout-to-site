# Guida pratica all'attività "siti demo-prima"

Tutto quello che serve sapere oltre al codice: tecnica di base, fisco, regole, soldi.
Scritta il 4 novembre 2026. **Non è una consulenza fiscale o legale**: le cifre sono indicative
e le regole cambiano ogni anno. Le decisioni importanti si confermano con il commercialista.

\---

## 1\. Le basi tecniche, in parole semplici

|Parola|Cos'è|Paragone|Chi lo paga / di chi è|
|-|-|-|-|
|**Dominio**|il nome: `cascinaguardia.it`|il nome sul campanello|del cliente, che lo rinnova ogni anno dal suo fornitore (Aruba, Register.it, Dataservice…)|
|**Registrar**|l'azienda dove è registrato il dominio|l'anagrafe del nome|il cliente ha un account lì|
|**DNS**|la "rubrica" del dominio: dice dove sta il sito e dove arriva la posta|l'indirizzo scritto in rubrica|si modifica nel pannello del registrar|
|**Hosting**|il computer sempre acceso che contiene i file del sito|la casa|per noi **Netlify**|
|**HTTPS**|il lucchetto: la connessione è cifrata|la serratura|gratis e automatico su Netlify|
|**Posta (MX)**|dove arrivano le email `@dominio`|la cassetta della posta|resta dal fornitore del cliente: **non si tocca mai**|
|**Backup**|copia di sicurezza del sito|le chiavi di scorta|ce l'abbiamo già: ogni sito è su GitHub con tutta la storia|
|**Monitoraggio**|un servizio che controlla ogni pochi minuti che il sito risponda|l'allarme|gratis con servizi tipo UptimeRobot|

### Cosa succede quando un sito va online

1. Si fotografano i DNS (`consegna.py dns ... --salva`).
2. Nel pannello del registrar si cambiano **solo due righe**: il record **A** del dominio e il **CNAME** del `www`.
3. Dopo qualche minuto (a volte qualche ora) il dominio porta al sito nuovo; Netlify attiva l'HTTPS da solo.
4. Si rifà la foto dei DNS: i record **MX** e **TXT** devono essere identici a prima.

### Errori classici da evitare

* Spostare i **nameserver** a Netlify: si rischia di perdere la posta del cliente.
* Lasciare un record **A** sul `www` e aggiungere il CNAME: molti pannelli danno errore. Prima si cancella l'A del www.
* Far **disdire il vecchio hosting** al cliente quando la posta è dallo stesso fornitore: perde le email.
* Dimenticare il **rinnovo del dominio**: sito e posta spariscono. Promemoria in calendario un mese prima.

### Domini: cose utili

* Il dominio va **intestato al cliente** (per i `.it` l'intestatario deve essere nell'Unione Europea).
* Per spostare un dominio da un registrar a un altro serve il **codice di trasferimento** (AuthInfo / EPP),
che si chiede al registrar attuale. Non serve per il nostro lavoro: a noi basta cambiare due record DNS.
* Il cliente deve avere **lui** le credenziali del pannello. Se non le ha più, vanno recuperate dal registrar
prima di iniziare la consegna.

\---

## 2\. Fisco: senza partita IVA (prestazione occasionale)

### Quando si può usare

Per lavori **saltuari**, senza organizzazione stabile. Non conta la cifra: conta il modo.
Segnali che portano verso la partita IVA: ricerca continua di clienti, listino fisso, clienti
ricorrenti, **canoni mensili**, pubblicità costante.

### Come si fa, passo passo

1. **Accordo scritto** con il cliente (l'email di accordo dell'agent Consegna + la sua risposta "Accetto").
2. **Ricevuta** per ogni pagamento (`consegna.py ricevuta`). Contiene:

   * i tuoi dati e il codice fiscale, i dati del cliente;
   * la dicitura "prestazione di lavoro autonomo occasionale, fuori campo IVA (art. 5 DPR 633/72)";
   * la **ritenuta d'acconto del 20%** se il cliente è un'azienda o un professionista (sostituto d'imposta);
   * la **marca da bollo da 2 €** se l'importo supera 77,47 € (si compra dal tabaccaio, si incolla sull'originale,
si scrive il numero sulla copia che mandi).
3. **Il cliente paga** il netto (80%) con bonifico e versa lui il 20% allo Stato con l'F24.
4. **Entro marzo dell'anno dopo** il cliente ti manda la **Certificazione Unica (CU)** con quanto ti ha pagato
e la ritenuta versata. Se non arriva, chiedila.
5. **Nel 730** questi compensi vanno tra i "redditi diversi" (di solito quadro D, rigo D5), con le ritenute
già versate. Si sommano al tuo stipendio e paghi la differenza tra la tua aliquota IRPEF e il 20% già trattenuto.

### Esempio su un sito da 590 €

|||
|-|-|
|Acconto 295 € → bonifico 236 €, ritenuta 59 €|Saldo 295 € → bonifico 236 €, ritenuta 59 €|
|Totale incassato sul conto: **472 €**|Ritenute già pagate per te: **118 €**|
|Nel 730, con un'aliquota del 33-35%, paghi ancora circa **80-90 €**|Netto finale: **circa 380-390 €**|

### Soglie da ricordare

* **5.000 € l'anno** di compensi occasionali: sopra scattano i contributi INPS (gestione separata) sulla parte
eccedente. Non è una soglia "senza partita IVA": è solo per i contributi.
* Lo script delle ricevute si blocca prima dei 5.000 € e avvisa dal **terzo cliente** dell'anno.

\---

## 3\. Fisco: con la partita IVA (regime forfettario)

### Quando aprirla

* Quando l'attività diventa **abituale**: più clienti con continuità, o canoni.
* Quando la vuoi per **vendere i canoni**.
* Quando conviene: indicativamente da **6-8 siti l'anno** in su, o con molti canoni.
* Decisione da prendere con il commercialista, **dal secondo cliente in poi**, con i numeri veri in mano.

### Come funziona il forfettario

* **Tasse:** 5% per i primi 5 anni (poi 15%), calcolate sul **67%** degli incassi (coefficiente per i servizi).
* **Contributi INPS:** se sei in **gestione separata**, circa il 26% sulla stessa base, **solo se incassi**.
Se invece ti iscrivono alla **gestione commercianti**, c'è un **minimo fisso di qualche migliaio di euro l'anno**
anche senza incassi: con pochi clienti non conviene. È la **prima domanda** da fare al commercialista.
* **Niente IVA** in fattura, ma **fattura elettronica obbligatoria** (dal 2024 anche per i forfettari),
con bollo da 2 € sopra 77,47 €.
* **Limiti:** incassi sotto 85.000 € l'anno; reddito da lavoro dipendente dell'anno prima sotto il limite di legge
(35.000 € per il 2026, da ricontrollare ogni anno perché viene rinnovato di anno in anno).
* **Costi fissi:** il commercialista (qualche centinaio di euro l'anno). Aprire e chiudere la partita IVA è gratis.

### Esempio con 4 siti e 4 canoni da 15 €/mese

Incassi 3.080 € → imponibile 2.064 € → imposta \~100 € + INPS \~540 € + commercialista \~400-600 € → **netto \~1.800-1.900 €**.

### Domande da fare al commercialista (portale scritte)

1. "Per lo sviluppo di siti web vado in **gestione separata** INPS o nella **gestione commercianti**?"
2. "Con il mio modo di lavorare (ricerca clienti, demo, listino) posso restare in **prestazione occasionale**? Fino a quando?"
3. "Che **codice ATECO** uso?"
4. "Rientro nel **forfettario** con il mio stipendio da dipendente?"
5. "Quanto costa il suo servizio all'anno e cosa include (fatture elettroniche, dichiarazione, F24)?"
6. "Se apro e poi l'attività non va, quanto costa **chiudere**?"

\---

## 4\. Il contratto di lavoro da dipendente

Prima del **primo incasso** rileggi il contratto e il regolamento aziendale. Cerca:

* **esclusiva** o divieto di altre attività retribuite;
* **obbligo di comunicare** all'azienda attività esterne;
* **non concorrenza** (durante il rapporto vale comunque l'obbligo di fedeltà dell'art. 2105 del codice civile:
non fare affari in concorrenza con il datore di lavoro);
* regole su **uso di PC, rete e orari aziendali**.

Accortezze pratiche:

* lavora al progetto **fuori orario** e, quando puoi, **dal PC di casa** (l'account GitHub e Gmail sono già personali, bene così);
* mai usare email, clienti, codice o strumenti aziendali;
* se il contratto ha dubbi, chiedi a un consulente del lavoro o al sindacato prima di incassare.

\---

## 5\. Regole legali da conoscere

### Contattare i prospect

* **Email commerciali non richieste**: per il Codice privacy (art. 130) servirebbe il consenso anche verso le aziende;
l'indirizzo pubblicato sul sito non basta. Il rischio è basso con email singole e personalizzate, ma esiste.
Le regole in `outreach/regole-contatto.md` lo tengono basso (massimo 5 al giorno, 1 sollecito, frase per non essere ricontattati).
* **Telefonate**: controllare il **Registro pubblico delle opposizioni** per i numeri non aziendali.
* **Di persona**: sempre lecito, ed è il canale migliore per le attività locali.
* Quando un cliente dice sì (a voce o per email) registra **data, canale e parole** (`--consenso`): da lì le email sono lecite.

### Sul sito del cliente

* **Partita IVA** dell'azienda visibile (di solito nel footer): è obbligatoria.
* **Privacy e cookie**: il titolare è il **cliente**, non tu. Noi prepariamo un testo base; lui lo legge e, se ha un consulente, lo fa controllare.
* **Niente cookie di profilazione o statistica** (es. Google Analytics) senza banner del consenso. Per questo:
Search Console sempre, statistiche solo senza cookie (voce del listino).
* **Foto e testi**: il cliente conferma di avere i diritti (nell'accordo). Attenzione alle foto di fotografi esterni.
* **Demo**: sempre con `noindex` e l'avviso "Anteprima di proposta", perché usa marchio e foto del cliente prima che abbia accettato.
* **Accessibilità** (European Accessibility Act, dal giugno 2025): riguarda soprattutto e-commerce e servizi digitali;
le microimprese che offrono servizi ne sono in genere escluse. Per i siti vetrina basta lavorare bene (contrasti,
testi alternativi alle immagini, sito usabile da tastiera), cosa che i nostri stili fanno già.

\---

## 6\. Hosting: regole e costi

* **Netlify gratuito**: permesso anche per siti di clienti, **purché non fai pagare l'hosting** (niente rivendita).
* Il gratuito ha **300 crediti al mese per tutto l'account**; il traffico costa circa 20 crediti per GB, quindi circa
15 GB al mese in tutto. Se finiscono, i siti vengono **messi in pausa**. Per pochi siti locali basta: controlla i
crediti nel pannello ogni tanto.
* **Con il canone** (rivendita): serve un piano a pagamento (Personal circa 9 $/mese, Pro circa 20 $/mese, per tutto l'account),
oppure **Cloudflare Pages** (gratis anche per uso commerciale, traffico illimitato, fino a 100 progetti).
* Netlify può cambiare le regole del gratuito: per questo ogni sito ha il suo **repo su GitHub** e il dominio è del cliente.
Spostare un sito = ripubblicarlo altrove + cambiare due righe DNS.
* **Nuovi progetti Netlify sono privati**: dopo ogni pubblicazione, Visitor access → production pubblica. Prova sempre in incognito.

\---

## 7\. Soldi: pagamenti, ritardi, canoni

### Regole per farsi pagare

* **50% prima di iniziare.** Senza acconto non si lavora (protegge il tuo tempo).
* **Saldo il giorno della pubblicazione**: il sito definitivo lo mostri in anteprima, il cliente lo approva,
paga il saldo, e **poi** colleghi il dominio.
* Tutto per **bonifico**, mai contanti senza ricevuta.
* Registra ogni pagamento con `consegna.py incassato`: `riepilogo` ti dice cosa manca.

### Se un cliente non paga

1. Dopo 7 giorni: promemoria gentile per email.
2. Dopo altri 7-10 giorni: telefonata.
3. Poi: email più formale con la data entro cui pagare.
4. Ultima strada: lettera di diffida (anche tramite avvocato o associazione di categoria) e, per importi piccoli,
valutare se ne vale la pena.
Con l'acconto del 50% la perdita massima è comunque metà.

### Canoni (quando avrai la partita IVA)

|Versione|Prezzo indicativo|Cosa include|Lavoro per te|
|-|-|-|-|
|Base|15 €/mese|hosting, HTTPS, backup, monitoraggio, promemoria rinnovo dominio|quasi zero|
|Con aggiornamenti|30-40 €/mese|come la base + 1-2 piccoli aggiornamenti al mese + resoconto Search Console|un po' ogni mese|

* Si accumulano: 20 clienti × 15 € = 3.600 € l'anno senza vendere siti nuovi.
* Meglio fatturare **annuale anticipato** (180 €): meno fatture, meno solleciti.
* Proponili **prima ai clienti che hai già**.

\---

## 8\. "Se succede X, fai Y"

|Situazione|Cosa fare|
|-|-|
|Un prospect risponde "mi interessa"|`registra --stato interessato --consenso "..."`, poi telefonata con `outreach/chiamata.md`|
|Ti chiama mentre sei al lavoro o in metro|"Grazie! Posso richiamarvi alle 18?" e richiama con la traccia davanti|
|Chiede uno sconto|"Ci penso e vi faccio sapere" (massimo 10%, lo decidi tu dopo)|
|Accetta|Agent Consegna: `avvia`, accordo, acconto. Prima del primo incasso: contratto di lavoro|
|Chiede l'e-commerce|Non al primo giro: catalogo con WhatsApp o preventivo; e-commerce vero dopo la partita IVA|
|Chiede Google Analytics|Search Console inclusa; statistiche senza cookie a 40 €|
|Vuole aggiornare da solo menu o eventi|Non promettere al telefono: proposta scritta (pannello semplice, aggiornamenti a preventivo o canone)|
|Non paga il saldo|Il dominio non si collega finché non paga; poi promemoria → telefonata → email formale|
|Netlify mette in pausa i siti|Crediti finiti: passa a Netlify Personal o sposta su Cloudflare Pages|
|GitHub blocca il push per un "secret"|README, sezione Git: togli la cartella `sorgente` dal commit, non cliccare "allow"|
|Secondo cliente che paga|Prenota il commercialista con le domande della sezione 3|
|Terzo cliente nell'anno o vuoi i canoni|Decidi con il commercialista se aprire la partita IVA|

\---

## Fonti utili

* Prestazione occasionale e partita IVA: guide Fiscozen (fiscozen.it/guide), Fiscomania (fiscomania.com).
* Forfettario e lavoro dipendente 2026: Flextax, TeamSystem, Informazione Fiscale.
* Email commerciali e consenso: provvedimenti del Garante privacy (garanteprivacy.it).
* Netlify: netlify.com/pricing e il forum answers.netlify.com (uso commerciale del piano gratuito).
* Cloudflare Pages: developers.cloudflare.com/pages.

