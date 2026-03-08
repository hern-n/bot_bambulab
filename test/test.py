import json

def load_json(file_path: str) -> dict:
    """Carga un archivo JSON y lo devuelve como un diccionario de Python."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

data = load_json("config.json")

print(data["coordenates"]["16"])