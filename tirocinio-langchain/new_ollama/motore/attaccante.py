from pathlib import Path
import re
from motore.setup import ATTACCHI, accenti, crea_llm

ATTACCHI = Path("attacchi")

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
def genera_attacco(cfg, scenario,persona,  ciclo, log, tentativi=3):
    link = scenario["link"]
    cartella = ATTACCHI / scenario["id"]
    cartella.mkdir(parents=True, exist_ok=True)
    esiti = []

    tentativi_totali = cfg["mail_per_braccio"] * 4
    n = 0
    while sum(esiti) < cfg["mail_per_braccio"] and n < tentativi_totali:
        n += 1
        if cfg["modalita"] == "mutata":
            base = next(ciclo)
            corpo = base["corpo"].replace(base["da"], base["da_sosia"])
            a = base["ancora"]
            corpo = corpo.replace(a, a + ": " + link, 1) if a in corpo else corpo + "\n\n" + link
            da, oggetto, elemento, template, valida = base["da_sosia"], base["oggetto"], "link", base["id"], True
            motivo = "mutata"
        else:
            mittente = f'{scenario["mittente_nome"]}, {scenario["mittente_ruolo"]}'
            prompt = f"""Sei un attaccante esperto di spear phishing.
Azienda: Nordvia Componenti S.r.l., distribuzione di componentistica industriale, 48 dipendenti, nord Italia.
Bersaglio: reparto {scenario["bersaglio"]}
Tipo di attacco: {scenario["pretext"]}
Strumento da citare: {scenario["strumento"]}
Mittente finto: {mittente}
Leva da usare: {scenario["trigger"]}

Regole: prima riga "OGGETTO: ...", massimo 120 parole, apri con "Gentile {persona["nome"]}",
firma su una riga sola: {mittente}, poi il link {link} su riga sua senza parentesi,
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
                if valida:
                    break    
            elemento, template = "link", None

        if valida:
            (cartella / f"{cfg['modalita']}_{sum(esiti):02d}.mail").write_text(
                f"DA: {da}\nOGGETTO: {oggetto}\nSCENARIO: {scenario['id']}\n"
                f"MODALITA: {cfg['modalita']}\nELEMENTO: {elemento}\n"
                f"TEMPLATE: {template or '-'}\n---\n{corpo}\n", encoding="utf-8")
        log.scrivi(1, "attaccante", valida=valida, motivo=motivo, oggetto=oggetto, corpo=corpo)
        esiti.append(valida)

    print(sum(esiti), "valide su", len(esiti))