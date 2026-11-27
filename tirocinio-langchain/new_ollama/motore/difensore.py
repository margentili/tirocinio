from motore.setup import crea_llm, parse_json
def run_difensore(cfg, persona, mail, policy, anagrafica, log):
    llm = crea_llm("defender", cfg, json_mode=True)

    prompt = f"""Sei {persona["nome"]}, {persona["ruolo"]} di Nordvia Componenti S.r.l., 48 dipendenti.
Il tuo carattere: {persona["tratti"]}

Policy aziendale:
{policy}

Anagrafica fornitori e clienti (domini e IBAN registrati):
{anagrafica}

Hai appena ricevuto questa email:
DA: {mail["da"]}
OGGETTO: {mail["oggetto"]}
{mail["corpo"]}

Elenca in elementi_notati solo cose che vedi.

Cosa significano le decisioni:
- apre: fai ciò che la mail chiede
- verifica: prima di agire chiedi conferma a un collega o all'IT
- segnala: lo comunichi come sospetto senza aprire
- ignora: archivi senza fare niente

Scegli la decisione più bassa che il testo giustifica: se non c'è un'anomalia concreta, è apre.

Rispondi SOLO con JSON:
{{"decisione":"apre|verifica|segnala|ignora","motivazione":"una frase","elementi_notati":["..."]}}"""

    dati, raw = {}, ""
    for _ in (1, 2):
        raw = llm.invoke(prompt).content
        dati = parse_json(raw)
        if dati.get("decisione") in {"apre", "verifica", "segnala", "ignora"}:
            break
        if "temperature" in llm.model_fields_set:
            llm.temperature = 0.0
    log.scrivi(2, "difensore", legittimo=mail.get("legittimo"), raw=raw, **dati)
    return dati