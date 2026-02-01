import json
import os

DATA_FILE = "municipios_data.json"

class DataProvider:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return {"estados": []}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_data(self):
        return self.data

    def get_municipio_metadata(self, estado_nombre, municipio_nombre):
        """Busca metadata específica para un municipio"""
        for estado in self.data.get("estados", []):
            if estado["nombre"] == estado_nombre:
                for muni in estado["municipios"]:
                    if muni["nombre"] == municipio_nombre:
                        return muni.get("metadata", {})
        return None
