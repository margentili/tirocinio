import json, uuid, datetime, pathlib

class RunLog:
    def __init__(self, cfg):
        self.run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.cfg = cfg
        self.path = pathlib.Path(f"runs/{self.run_id}.jsonl")
        self.path.parent.mkdir(exist_ok=True)

    def scrivi(self, giro, attore, **campi):
        riga = {"run_id": self.run_id, "ts": datetime.datetime.now().isoformat(),
                "giro": giro, "attore": attore, "seed": self.cfg["seed"],
                "scenario": self.cfg["scenario"], "persona": self.cfg["persona"],
                **campi}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(riga, ensure_ascii=False) + "\n")