# Consegna {{cliente}} — avviata il {{data}}

Spunta man mano (`[x]`). L'agent Consegna la tiene aggiornata.

## 1. Accordo
- [ ] `cliente.txt` controllato con il cliente (ragione sociale, P.IVA, indirizzo, sostituto d'imposta) → `verificato=si`
- [ ] Bozza accordo approvata dall'utente e inviata
- [ ] Il cliente ha risposto "Accetto" (salvare la risposta in `consegna/`)
- [ ] `outreach.py registra "<nome>" --stato vinto`

## 2. Acconto
- [ ] Ricevuta di acconto creata, firmata (e bollo se > 77,47 €) e inviata
- [ ] Bonifico arrivato → `consegna.py incassato <numero>`

## 3. Materiali
- [ ] Testi definitivi
- [ ] Logo in buona qualità
- [ ] Foto: il cliente ha confermato di avere i diritti (soprattutto foto di fotografi esterni)
- [ ] Accesso al pannello del dominio (o contatto di chi lo gestisce)
- [ ] Usano email @dominio? (se sì: MX da non toccare)

## 4. Sito definitivo
- [ ] Modifiche richieste applicate alla demo (massimo 2 giri)
- [ ] `consegna.py produzione` senza errori
- [ ] Controllato in anteprima su telefono e computer
- [ ] Privacy letta dal cliente
- [ ] `consegna.py repo` + repo GitHub privato + progetto Netlify pubblico

## 5. Dominio
- [ ] `consegna.py dns <dominio> --salva ...` PRIMA di toccare qualcosa
- [ ] Dominio aggiunto su Netlify, cambiati solo A e CNAME
- [ ] HTTPS attivo (lucchetto) su dominio con e senza www
- [ ] `consegna.py dns ... --salva ...` DOPO: MX invariati, email del cliente funzionante
- [ ] Vecchio hosting: il cliente sa che può disdirlo (dopo qualche giorno di controllo)

## 6. Chiusura
- [ ] Il cliente ha approvato il sito online
- [ ] Ricevuta di saldo inviata e incassata
- [ ] Google Search Console: sito aggiunto e sitemap inviata
- [ ] Documento di consegna inviato
- [ ] Demo Netlify vecchia eliminata o resa privata
