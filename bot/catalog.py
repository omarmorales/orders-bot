import os
from thefuzz import process
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

def get_products():
    if not supabase:
        print("⚠️ Supabase not configured. Returning empty catalog.")
        return []
    try:
        response = supabase.table("products").select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Error fetching catalog from Supabase: {e}")
        return []

def get_catalog_text():
    products = get_products()
    lines = []
    for p in products:
        if p.get("sells_by_box"):
            lines.append(
                f"- {p['name']} (Category: {p.get('category', '')}) — "
                f"Unit: ${p['unit_price']:.2f} | "
                f"Box ({p.get('units_per_box')} units): ${p['box_price']:.2f}"
            )
        else:
            lines.append(
                f"- {p['name']} (Category: {p.get('category', '')}) — "
                f"Unit only: ${p['unit_price']:.2f}"
            )
    return "\n".join(lines)

def get_relevant_catalog_text(query: str, top_k: int = 15):
    products = get_products()
    if not products:
        return ""
    
    product_names = [p["name"] for p in products]
    best_matches = process.extract(query, product_names, limit=top_k)
    matched_names = {match[0] for match in best_matches}
    relevant_products = [p for p in products if p["name"] in matched_names]
    
    lines = []
    for p in relevant_products:
        if p.get("sells_by_box"):
            lines.append(
                f"- {p['name']} (Category: {p.get('category', '')}) — "
                f"Unit: ${p['unit_price']:.2f} | "
                f"Box ({p.get('units_per_box')} units): ${p['box_price']:.2f}"
            )
        else:
            lines.append(
                f"- {p['name']} (Category: {p.get('category', '')}) — "
                f"Unit only: ${p['unit_price']:.2f}"
            )
    return "\n".join(lines)