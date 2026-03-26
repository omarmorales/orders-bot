import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Cannot seed database: SUPABASE_URL and SUPABASE_KEY are missing from .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "products.csv")

def run_seed():
    print(f"📦 Reading products from {CSV_PATH}...")
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            new_products = []
            for row in reader:
                # Convert empty strings to None (null)
                box_price = float(row["precio_caja"]) if row.get("precio_caja", "").strip() else None
                units_per_box = int(row["piezas_caja"]) if row.get("piezas_caja", "").strip() else None
                sells_by_box = row.get("venta_caja", "false").strip().lower() == "true"
                
                new_products.append({
                    "name": row["nombre"].strip(),
                    "unit_price": float(row["precio_pieza"]),
                    "box_price": box_price,
                    "units_per_box": units_per_box,
                    "category": row["categoria"].strip(),
                    "sells_by_box": sells_by_box
                })
            
            # Print preview
            print(f"✅ Preview: Read {len(new_products)} products. Inserting into Supabase...")
            
            # Insert into supabase
            # We assume a table named 'products'
            for prod in new_products:
                response = supabase.table("products").insert(prod).execute()
                print(f"Inserted: {prod['name']}")
                
            print("🚀 Seeding completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during seeding: {e}")

if __name__ == "__main__":
    run_seed()
