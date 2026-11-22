import json, random
from datetime import datetime

from motore.setup import (carica, nuovo_log, carica_rumore, carica_attacchi,
                          RUNS, CONFIG, POLICY, ANAGRAFICA, ATTACCHI)
from motore.attaccante import genera_attacco
from motore.difensore import run_difensore
from motore.giudice import run_giudice

ESITO = {"apre": 2, "verifica": 1, "segnala": 0, "ignora": 0}


def prepara(scenario_id=None, persona_id=None):
    cfg, scenario, persona, ciclo = carica(scenario_id, persona_id)
    batch = RUNS / datetime.now().strftime("batch_%Y%m%d_%H%M%S")
    batch.mkdir(parents=True, exist_ok=True)
    (batch / "config.yaml").write_text(CONFIG.read_text(encoding="utf-8"), encoding="utf-8")
    print("ATTACCANTE:", cfg["modelli"]["attacker"]["name"])
    print("DIFENSORE :", cfg["modelli"]["defender"]["name"])
    print("GIUDICE   :", cfg["modelli"]["judge"]["name"])
    print(batch)
    return {"cfg": cfg, "scenario": scenario, "persona": persona, "ciclo": ciclo,
            "policy": POLICY.read_text(encoding="utf-8"),
            "anagrafica": ANAGRAFICA.read_text(encoding="utf-8"),
            "batch": batch}


def esegui(ctx):
    cfg, scenario, persona, batch = ctx["cfg"], ctx["scenario"], ctx["persona"], ctx["batch"]
    policy, anagrafica, ciclo = ctx["policy"], ctx["anagrafica"], ctx["ciclo"]
    rumore = carica_rumore(persona["nome"], scenario["bersaglio"])

    cartella = ATTACCHI / scenario["id"]
    if cartella.exists():
        for f in cartella.glob("*.mail"):
            f.unlink()
    log_gen = nuovo_log(cfg, batch)
    cfg["seed_run"] = cfg["seed"]
    genera_attacco(cfg, scenario,persona, ciclo, log_gen)

    attacchi = carica_attacchi(scenario["id"], persona["nome"])
    assert attacchi, f"nessun attacco congelato per '{scenario['id']}'"

    for i, mail in enumerate(attacchi):
        cfg["seed_run"] = cfg["seed"] * 1000 + i
        random.seed(cfg["seed_run"])
        log_i = nuovo_log(cfg, batch)

        casella = []
        for t in ("ferie", "ordine", "ddt", "iban"):
            pool = rumore.get(t, [])
            if pool:
                casella += [{**r, "legittimo": True}
                            for r in random.sample(pool, min(cfg["rumore_per_tipo"], len(pool)))]
        casella.append({**mail, "legittimo": False})
        random.shuffle(casella)

        pos_attacco = next(p for p, x in enumerate(casella) if not x["legittimo"])
        righe, dec_attacco, esito_attacco = [], None, None

        for pos, m in enumerate(casella):
            dec = run_difensore(cfg, persona, m, policy, anagrafica, log_i)
            if m["legittimo"]:
                righe.append({"run_id": log_i.run_id, "i": i, "posizione": pos,
                              "persona": cfg["persona"], "scenario": cfg["scenario"],
                              "legittimo": True, "decisione": dec.get("decisione"),
                              "falso_allarme": int(dec.get("decisione") == "segnala")})
            else:
                dec_attacco = dec
                esito_attacco = ESITO.get(dec.get("decisione"), -1)
                riga_attacco = {"run_id": log_i.run_id, "i": i, "posizione": pos,
                                "persona": cfg["persona"], "scenario": cfg["scenario"],
                                "legittimo": False, "template": mail.get("template"),
                                "decisione": dec.get("decisione"), "esito": esito_attacco}

        try:
            giud = run_giudice(cfg, mail, dec_attacco, log_i)
        except Exception as e:
            giud = {}
            log_i.scrivi(3, "giudice", errore=str(e))
        riga_attacco.update({f"p_{k}": v for k, v in giud.get("punteggi", {}).items()})
        righe.append(riga_attacco)

        with open(batch / "riepilogo.jsonl", "a", encoding="utf-8") as f:
            for r in righe:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(i, "attacco in posizione", pos_attacco, "esito:", esito_attacco)