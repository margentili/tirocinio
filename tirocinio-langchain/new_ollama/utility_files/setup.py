import json, yaml, re, random, itertools
from pathlib import Path
from utility_files.logger import RunLog
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv


load_dotenv()

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
    for p in sorted(Path(cartella).rglob("*.mail")):
        testo = p.read_text(encoding="utf-8")
        testa, _, corpo = testo.partition("---")
        campi = {}
        for r in testa.strip().splitlines():
            if ": " in r:
                k, v = r.split(": ", 1)
                campi[k.strip().upper()] = v.strip()
        d = {"da": campi.get("DA", ""),
             "oggetto": campi.get("OGGETTO", ""),
             "tipo": campi.get("TIPO", "altro").lower(),
             "corpo": corpo.strip(),
             "file": p.name}
        fuori.setdefault(d["tipo"], []).append(d)
    return fuori

def crea_llm(ruolo, cfg, json_mode=False):
    m = cfg["modelli"][ruolo]
    if m.get("provider") == "azure":
        from langchain_openai import AzureChatOpenAI
        kw = dict(
            azure_endpoint=os.environ["AZURE_AI_ENDPOINT"],
            api_key=os.environ["AZURE_AI_KEY"],
            azure_deployment=os.environ["AZURE_AI_DEPLOYMENT"],
            api_version=os.environ["AZURE_AI_API_VERSION"],
        )
        if m.get("temp") is not None:
            kw["temperature"] = m["temp"]
        if json_mode:
            kw["model_kwargs"] = {"response_format": {"type": "json_object"}}
        return AzureChatOpenAI(**kw)

    kw = dict(base_url=m["host"], model=m["name"], temperature=m["temp"],
              num_ctx=2048, num_predict=250, client_kwargs={"timeout": 120})
    if json_mode:
        kw["format"] = "json"
    return ChatOllama(**kw)