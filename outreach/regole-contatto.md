# Regole di contatto

## Metodo scelto: prima email, poi telefonate lampo
L'utente ha scelto di provare **prima l'email**, sapendo che per il Garante privacy l'email
commerciale non richiesta è illecita anche verso le aziende (art. 130 Codice privacy; l'indirizzo
pubblicato sul sito non vale come consenso; il link "disiscriviti" non basta). Il rischio è suo;
il compito dell'agent è tenerlo il più basso possibile e passare alle **telefonate lampo** se
l'email non funziona.

### Email a freddo: regole obbligatorie
1. **Una a una, mai in serie.** Ogni email è scritta per quell'azienda e cita qualcosa di vero e
   specifico del loro sito. Niente testo identico copiato per più aziende.
2. **Massimo 5 email nuove al giorno** (anche per non finire nello spam di Gmail).
3. **Mittente chiaro:** nome e cognome dell'utente, cosa fa, dove ha trovato l'indirizzo
   ("dal vostro sito").
4. **Uscita facile:** sempre la frase "Se non le interessa me lo scriva pure e non la ricontatterò."
5. **Indirizzo giusto:** quello generico dell'azienda (info@, commerciale@...), mai indirizzi personali
   di dipendenti, mai PEC.
6. **Al massimo 1 sollecito**, dopo almeno 6 giorni lavorativi. Poi stato "freddo": niente più email.
7. **Chi chiede di non essere ricontattato** → stato `non_contattare`, per sempre.
8. **Corta:** al massimo 120 parole. Il link alla demo è il centro dell'email.
9. **Oggetto sobrio**, niente maiuscole o punti esclamativi, niente "offerta", "gratis", "urgente".

### Quando passare alle telefonate lampo
Dopo **10 email a freddo** l'agent fa il conto: se le risposte (anche negative) sono meno di 2,
propone all'utente di passare alle telefonate lampo per i prospect successivi.

## Telefonata lampo (30 secondi)
Solo per chiedere il permesso di scrivere. Per le aziende con un numero fisso aziendale.
Prima di chiamare un numero che potrebbe essere personale (cellulare del titolare) verificare il
Registro pubblico delle opposizioni o preferire la visita di persona.

## Visita di persona
Per negozi, ristoranti, atelier: la demo sul telefono, 2 minuti, poi "le mando il link per email?".

## Consenso
Quando il cliente dice sì (a voce, per telefono o rispondendo a un'email) si registra **data,
canale e parole usate** con `outreach.py registra ... --consenso "..."`. Da quel momento le email
sono richieste e quindi lecite.
