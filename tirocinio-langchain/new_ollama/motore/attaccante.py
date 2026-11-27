import re
from motore.setup import ATTACCHI, accenti, crea_llm

IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")

def validazione(corpo, oggetto, scenario):
    corpo = (corpo or "").strip()
    if not oggetto:
        return False, "oggetto vuoto"
    if len(corpo) < 200:
        return False, "troppo corto"
    if "```" in corpo:
        return False, "markdown"
    if scenario.get("link") and scenario["link"] not in corpo:
        return False, "link assente"
    if scenario.get("iban") and scenario["iban"] not in corpo:
        return False, "iban assente"
    righe = [r.strip() for r in corpo.splitlines() if r.strip()]
    if "XXX" in corpo:
        return False, "segnaposto"
    if not righe:
        return False, "vuoto"
    firma = scenario.get("mittente_nome","")
    if firma and f"{firma}," not in "\n".join(righe[-8:]):
        return False, "firma senza virgola"
    return True, "ok"
def genera_attacco(cfg, scenario,persona, log, tentativi=3):
    link = scenario["link"]
    cartella = ATTACCHI / scenario["id"]
    cartella.mkdir(parents=True, exist_ok=True)
    esiti = []

    tentativi_totali = cfg["mail_per_braccio"] * 4
    n = 0
    while sum(esiti) < cfg["mail_per_braccio"] and n < tentativi_totali:
        n += 1
        mittente = f'{scenario["mittente_nome"]}, {scenario["mittente_ruolo"]}'
        prompt = f"""Sei un attaccante esperto di spear phishing.
Azienda: Nordvia Componenti S.r.l., distribuzione di componentistica industriale, 48 dipendenti, nord Italia.
Bersaglio: reparto {scenario["bersaglio"]}
Tipo di attacco: {scenario["pretext"]}
Strumento da citare: {scenario["strumento"]}
Mittente finto: {mittente}
Leva da usare: {scenario["trigger"]}

Regole: prima riga "OGGETTO: ...", massimo 120 parole, apri con "Gentile {persona["nome"]}",
nel corpo introduci il link {link} con una frase che chieda di confermare dal portale; chiudi con la firma su una riga sola {mittente}
il telefono {scenario["tel"]}, specifica che la password non si chiede per email.
Chi firma è il mittente finto: non presentarti come Nordvia. Solo la mail.
Inserisci l'IBAN nuovo {scenario.get("iban", "")} nel corpo, su una riga a sé, dopo il link."""

        valida, motivo, corpo, oggetto, da = False, "", "", "", scenario.get("da", "")
        for t in range(tentativi):
            llm = crea_llm("attacker", cfg, seed=cfg.get("seed_run", 0) + n * 10 + t)
            risposta = llm.invoke(prompt).content.strip()
            if "OGGETTO:" in risposta:
                _, _, resto = risposta.partition("OGGETTO:")
                oggetto, _, corpo = resto.partition("\n")
                oggetto, corpo = oggetto.strip(), accenti(corpo.strip())
            else:
                corpo = accenti(risposta)
            valida, motivo = validazione(corpo, oggetto, scenario)
            log.scrivi(1,"attaccante", slot=n, tentativo=t, valida=valida,
                       motivo=motivo, oggetto=oggetto, corpo=corpo)
            if valida:
                break    
        elemento, template = "link", None

        if valida:
            nome_file = f"{cfg[modalita]}_{sum(esiti):02d}.mail"
            (cartella / nome_file).write_text(
                f"DA: {da}\nOGGETTO: {oggetto}\nSCENARIO: {scenario['id']}\n"
                f"MODALITA: {cfg['modalita']}\nELEMENTO: {elemento}\n"
                f"TEMPLATE: {template or '-'}\n---\n{corpo}\n", encoding="utf-8")
            log.scrivi(1,"attaccante", esca=nome_file)
        esiti.append(valida)

    print(sum(esiti), "valide su", len(esiti))