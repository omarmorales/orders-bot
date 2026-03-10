import os
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

products = []
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "products.csv")


def load_products():
    global products
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            new_products = []
            for row in reader:
                new_products.append({
                    "name":          row["nombre"].strip(),
                    "unit_price":    float(row["precio_pieza"]),
                    "box_price":     float(row["precio_caja"])  if row.get("precio_caja", "").strip()  else None,
                    "units_per_box": int(row["piezas_caja"])    if row.get("piezas_caja", "").strip()   else None,
                    "category":      row["categoria"].strip(),
                    "sells_by_box":  row.get("venta_caja", "false").strip().lower() == "true",
                })
            products = new_products
            print(f"✅ Catalog loaded: {len(products)} products")
    except FileNotFoundError:
        print(f"❌ File not found: {CSV_PATH}")
    except Exception as e:
        print(f"❌ Error loading products.csv: {e}")

class CSVHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("products.csv"):
            print("🔄 Detected change in products.csv, reloading catalog...")
            load_products()

def start_catalog_watcher():
    observer = Observer()
    observer.schedule(CSVHandler(), path=os.path.dirname(CSV_PATH) or ".", recursive=False)
    observer.start()
    return observer

def get_catalog_text():
    lines = []
    for p in products:
        if p["sells_by_box"]:
            lines.append(
                f"- {p['name']} (Category: {p['category']}) — "
                f"Unit: ${p['unit_price']:.2f} | "
                f"Box ({p['units_per_box']} units): ${p['box_price']:.2f}"
            )
        else:
            lines.append(
                f"- {p['name']} (Category: {p['category']}) — "
                f"Unit only: ${p['unit_price']:.2f}"
            )
    return "\n".join(lines)

# Load on import
load_products()