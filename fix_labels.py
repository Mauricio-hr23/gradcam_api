import os, json

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

def normalize_labels(raw):
    """Convierte cualquier formato irregular de labels a una lista plana de strings."""
    if isinstance(raw, dict):
        # {"0": "A", "1": "B"}
        return [v for _, v in sorted(raw.items(), key=lambda x: int(x[0]))]
    elif isinstance(raw, list):
        labels = []
        for item in raw:
            if isinstance(item, (list, tuple)):
                # Ej: [0, "A"] o [("0","A")]
                if len(item) == 2 and isinstance(item[1], str):
                    labels.append(item[1])
                else:
                    for sub in item:
                        if isinstance(sub, str):
                            labels.append(sub)
            elif isinstance(item, str):
                labels.append(item)
        return labels
    else:
        raise ValueError(f"Formato desconocido: {type(raw)}")

def fix_all_labels():
    fixed = 0
    for file in os.listdir(MODELS_DIR):
        if file.endswith("_labels.json"):
            path = os.path.join(MODELS_DIR, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                labels = normalize_labels(data)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(labels, f, indent=4, ensure_ascii=False)
                print(f"✅ Corregido: {file} → {len(labels)} etiquetas")
                fixed += 1
            except Exception as e:
                print(f"⚠️ Error en {file}: {e}")
    print(f"\n🔄 {fixed} archivos corregidos con éxito.")

if __name__ == "__main__":
    fix_all_labels()
