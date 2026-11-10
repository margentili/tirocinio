import json, yaml, re, random, itertools
from pathlib import Path
from utility_files.logger import RunLog



CONFIG   = Path("utility_files/config.yaml")
SCENARI  = Path("configuration/scenari.json")
PERSONE  = Path("configuration/persone.json")
LEGITTIME = Path("configuration/legittime.json")

ACCENTI = {"venerdi'":"venerdì","disponibilita'":"disponibilità","necessita'":"necessità",
           "lunedi'":"lunedì","perche'":"perché","piu'":"più","puo'":"può"}

def parse_json(testo):
    t = re.sub(r"^```(?:json)?|```$", "", testo.strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {}

def accenti(t):
    for k, v in ACCENTI.items():
        t = t.replace(k, v)
    return re.sub(r"\be'\b", "è", t)

def carica():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    scenari = {s["id"]: s for s in json.loads(SCENARI.read_text(encoding="utf-8"))}
    persone = {p["id"]: p for p in json.loads(PERSONE.read_text(encoding="utf-8"))}
    scenario = scenari[cfg["scenario"]]
    persona = persone[cfg["persona"]]

    templ = [l for l in json.loads(LEGITTIME.read_text(encoding="utf-8"))
             if scenario["id"] in l.get("scenari", [])]
    assert templ, f"nessun template associato allo scenario '{scenario['id']}'"
    ciclo = itertools.cycle(templ)
    return cfg, scenario, persona, ciclo

def nuovo_log(cfg, cartella):
    log = RunLog(cfg, cartella)
    log.scrivi(0, "sistema", evento="avvio", modalita=cfg["modalita"])
    return log

def carica_rumore(cartella="configuration/rumore"):
    fuori = {}
    for p in sorted(Path(cartella).glob("*/*.mail")):
        testo = p.read_text(encoding="utf-8")
        testa, _, corpo = testo.partition("---")
        campi = dict(r.split(": ", 1) for r in testa.strip().splitlines() if ": " in r)
        campi["corpo"] = corpo.strip()
        fuori.setdefault(campi.get("TIPO", "altro").lower(), []).append(campi)
    return fuori