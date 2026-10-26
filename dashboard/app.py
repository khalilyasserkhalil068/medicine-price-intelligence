import sqlite3
import csv
import json
import os
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "medicine.db"
ANALYSIS_DIR = BASE_DIR / "reports" / "analysis"

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/portal")
@app.route("/portal/")
def portal():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/reports/<path:filename>")
@app.route("/portal/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory(BASE_DIR / "reports", filename)

@app.route("/assets/<path:filename>")
@app.route("/portal/assets/<path:filename>")
def serve_asset(filename):
    return send_from_directory(BASE_DIR / "assets", filename)

# Re-read templates and static assets from disk on every request. Without this
# Flask caches the rendered page in memory, so editing dashboard/templates/
# index.html has no visible effect until the server is restarted - which is
# confusing when you are iterating on the design.
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: load cached CSV analysis data
def load_manufacturer_index():
    mfr_path = ANALYSIS_DIR / "manufacturer_price_index.csv"
    results = []
    if mfr_path.exists():
        with open(mfr_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    "manufacturer_name": row["manufacturer_name"],
                    "n": int(row["n"]),
                    "median_index": float(row["median_index"]),
                    "pct_cheapest": float(row["pct_cheapest"]),
                    "category": "Budget" if float(row["median_index"]) < 0.95 else ("Premium" if float(row["median_index"]) > 1.05 else "Fair")
                })
    return results

def load_top_groups():
    grp_path = ANALYSIS_DIR / "alternatives_per_group.csv"
    results = []
    if grp_path.exists():
        with open(grp_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append({
                    "generic_name": row["generic_name"],
                    "dosage_form_name": row["dosage_form_name"],
                    "strength_normalized": row["strength_normalized"],
                    "brands": int(row["brands"]),
                    "min_price": float(row["min_price"]),
                    "median_price": float(row["median_price"]),
                    "max_price": float(row["max_price"]),
                    "spread_x": float(row["spread_x"]),
                    "max_saving_pct": float(row["max_saving_pct"])
                })
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/kpi")
def get_kpi():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM medicines")
    total_meds = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM generics")
    total_generics = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM manufacturers")
    total_mfrs = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(price) FROM medicines")
    priced_meds = cur.fetchone()[0]
    
    conn.close()
    
    top_groups = load_top_groups()
    total_groups = len(top_groups)
    
    return jsonify({
        "total_medicines": total_meds,
        "total_generics": total_generics,
        "total_manufacturers": total_mfrs,
        "priced_medicines": priced_meds,
        "price_coverage_pct": round(priced_meds / total_meds * 100, 2),
        "total_comparable_groups": total_groups,
        "non_cheapest_share_pct": 79.8,
        "median_savings_pct": 28.6,
        "average_savings_pct": 30.5
    })

@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Priority search: exact brand start first, then contains
    cur.execute("""
        SELECT 
            m.brand_id,
            m.brand_name,
            m.generic_name,
            m.dosage_form_name,
            m.strength_normalized,
            m.manufacturer_name,
            m.price
        FROM vw_medicine_details m
        WHERE m.brand_name LIKE ? OR m.generic_name LIKE ?
        ORDER BY 
            CASE 
                WHEN m.brand_name LIKE ? THEN 1
                WHEN m.brand_name LIKE ? THEN 2
                ELSE 3 
            END,
            m.price ASC
        LIMIT 15
    """, (f"%{query}%", f"%{query}%", f"{query}%", f"% {query}%"))
    
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "brand_id": r["brand_id"],
            "brand_name": r["brand_name"],
            "generic_name": r["generic_name"] or "Not specified",
            "dosage_form_name": r["dosage_form_name"] or "Not specified",
            "strength_normalized": r["strength_normalized"] or "",
            "manufacturer_name": r["manufacturer_name"] or "",
            "price": round(r["price"], 2) if r["price"] is not None else None
        })
    return jsonify(results)

@app.route("/api/medicine/<int:brand_id>")
def get_medicine(brand_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            m.brand_id,
            m.brand_name,
            m.generic_name,
            m.dosage_form_name,
            m.strength_normalized,
            m.manufacturer_name,
            m.drug_class_name,
            m.indication_name,
            m.price,
            m.pack_price,
            m.pack_size,
            m.currency,
            m.package_description,
            m.type
        FROM vw_medicine_details m
        WHERE m.brand_id = ?
    """, (brand_id,))
    
    med = cur.fetchone()
    if not med:
        conn.close()
        return jsonify({"error": "Medicine not found."}), 404
    
    g_name = med["generic_name"]
    df_name = med["dosage_form_name"]
    str_norm = med["strength_normalized"]
    price = med["price"]
    
    # Group stats
    group_stats = None
    if g_name and df_name and str_norm:
        cur.execute("""
            SELECT 
                COUNT(*) as count_total,
                COUNT(price) as count_priced,
                MIN(price) as min_price,
                MAX(price) as max_price
            FROM vw_medicine_details
            WHERE generic_name = ? AND dosage_form_name = ? AND strength_normalized = ?
        """, (g_name, df_name, str_norm))
        stats = cur.fetchone()
        
        # Calculate median in python
        cur.execute("""
            SELECT price FROM vw_medicine_details
            WHERE generic_name = ? AND dosage_form_name = ? AND strength_normalized = ? AND price IS NOT NULL
            ORDER BY price ASC
        """, (g_name, df_name, str_norm))
        prices = [row[0] for row in cur.fetchall()]
        
        median_price = None
        if prices:
            n = len(prices)
            mid = n // 2
            median_price = (prices[mid] if n % 2 != 0 else (prices[mid-1] + prices[mid]) / 2.0)
            
        group_stats = {
            "total_brands": stats["count_total"],
            "priced_brands": stats["count_priced"],
            "min_price": round(stats["min_price"], 2) if stats["min_price"] is not None else None,
            "max_price": round(stats["max_price"], 2) if stats["max_price"] is not None else None,
            "median_price": round(median_price, 2) if median_price is not None else None,
            "spread_x": round(stats["max_price"] / stats["min_price"], 2) if stats["min_price"] and stats["max_price"] else 1.0
        }
    
    conn.close()
    
    return jsonify({
        "brand_id": med["brand_id"],
        "brand_name": med["brand_name"],
        "type": med["type"],
        "generic_name": g_name or "Not specified",
        "dosage_form_name": df_name or "Not specified",
        "strength_normalized": str_norm or "Not specified",
        "manufacturer_name": med["manufacturer_name"] or "Not specified",
        "drug_class_name": med["drug_class_name"] or "Not specified",
        "indication_name": med["indication_name"] or "Not specified",
        "price": round(price, 2) if price is not None else None,
        "pack_price": round(med["pack_price"], 2) if med["pack_price"] is not None else None,
        "pack_size": med["pack_size"],
        "package_description": med["package_description"] or "",
        "currency": med["currency"] or "BDT",
        "group_stats": group_stats
    })

@app.route("/api/alternatives/<int:brand_id>")
def get_alternatives(brand_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Fetch current medicine details
    cur.execute("""
        SELECT generic_name, dosage_form_name, strength_normalized, price
        FROM vw_medicine_details
        WHERE brand_id = ?
    """, (brand_id,))
    target = cur.fetchone()
    
    if not target or not target["generic_name"] or not target["dosage_form_name"] or not target["strength_normalized"]:
        conn.close()
        return jsonify({
            "message": "No equivalent brand can be listed because the generic, dosage form or strength is missing for this product.",
            "alternatives": []
        })
    
    g_name = target["generic_name"]
    df_name = target["dosage_form_name"]
    str_norm = target["strength_normalized"]
    current_price = target["price"]
    
    # 2. Fetch all equivalent brands matching (generic + form + strength)
    cur.execute("""
        SELECT 
            m.brand_id,
            m.brand_name,
            m.manufacturer_name,
            m.price,
            m.pack_price,
            m.pack_size,
            m.package_description
        FROM vw_medicine_details m
        WHERE m.generic_name = ? 
          AND m.dosage_form_name = ? 
          AND m.strength_normalized = ?
        ORDER BY 
            CASE WHEN m.price IS NULL THEN 1 ELSE 0 END,
            m.price ASC,
            m.brand_name ASC
    """, (g_name, df_name, str_norm))
    
    rows = cur.fetchall()
    conn.close()
    
    min_price = None
    priced_brands = [r["price"] for r in rows if r["price"] is not None]
    if priced_brands:
        min_price = min(priced_brands)
    
    alternatives = []
    for r in rows:
        b_id = r["brand_id"]
        b_price = r["price"]
        
        diff = None
        saving_amount = None
        saving_pct = None
        
        if current_price is not None and b_price is not None:
            diff = round(current_price - b_price, 2)
            saving_amount = round(max(0.0, current_price - b_price), 2)
            if current_price > 0:
                saving_pct = round((saving_amount / current_price) * 100.0, 1)
        
        is_current = (b_id == brand_id)
        is_cheapest = (b_price is not None and b_price == min_price)
        
        alternatives.append({
            "brand_id": b_id,
            "brand_name": r["brand_name"],
            "manufacturer_name": r["manufacturer_name"],
            "price": round(b_price, 2) if b_price is not None else None,
            "pack_price": round(r["pack_price"], 2) if r["pack_price"] is not None else None,
            "pack_size": r["pack_size"],
            "package_description": r["package_description"] or "",
            "price_diff": diff,
            "saving_amount": saving_amount,
            "saving_pct": saving_pct,
            "is_current": is_current,
            "is_cheapest": is_cheapest
        })
    
    return jsonify({
        "generic_name": g_name,
        "dosage_form_name": df_name,
        "strength_normalized": str_norm,
        "total_alternatives": len(alternatives) - 1 if len(alternatives) > 0 else 0,
        "cheapest_price": min_price,
        "alternatives": alternatives
    })

@app.route("/api/calculator", methods=["POST"])
def calculate_savings():
    data = request.get_json() or {}
    brand_id = data.get("brand_id")
    units = float(data.get("units", 30))
    
    if not brand_id or units <= 0:
        return jsonify({"error": "Invalid request: a medicine and a positive number of units are required."}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT brand_id, brand_name, generic_name, dosage_form_name, strength_normalized, price, manufacturer_name
        FROM vw_medicine_details
        WHERE brand_id = ?
    """, (brand_id,))
    target = cur.fetchone()
    
    if not target or target["price"] is None:
        conn.close()
        return jsonify({"error": "This medicine has no recorded unit price, so it cannot be compared."}), 400
        
    g_name = target["generic_name"]
    df_name = target["dosage_form_name"]
    str_norm = target["strength_normalized"]
    current_price = target["price"]
    
    # Find cheapest
    cur.execute("""
        SELECT brand_id, brand_name, manufacturer_name, price
        FROM vw_medicine_details
        WHERE generic_name = ? AND dosage_form_name = ? AND strength_normalized = ? AND price IS NOT NULL
        ORDER BY price ASC
        LIMIT 1
    """, (g_name, df_name, str_norm))
    cheapest = cur.fetchone()
    conn.close()
    
    if not cheapest:
        return jsonify({"error": "No comparable alternative has a recorded price."}), 400
        
    cheapest_price = cheapest["price"]
    current_total = round(units * current_price, 2)
    cheapest_total = round(units * cheapest_price, 2)
    net_savings = round(max(0.0, current_total - cheapest_total), 2)
    saving_pct = round((net_savings / current_total * 100.0), 2) if current_total > 0 else 0.0
    
    return jsonify({
        "units": units,
        "current_medicine": {
            "brand_id": target["brand_id"],
            "brand_name": target["brand_name"],
            "manufacturer_name": target["manufacturer_name"],
            "unit_price": round(current_price, 2),
            "total_cost": current_total
        },
        "cheapest_alternative": {
            "brand_id": cheapest["brand_id"],
            "brand_name": cheapest["brand_name"],
            "manufacturer_name": cheapest["manufacturer_name"],
            "unit_price": round(cheapest_price, 2),
            "total_cost": cheapest_total
        },
        "net_savings_bdt": net_savings,
        "saving_percentage": saving_pct,
        "is_already_cheapest": (target["brand_id"] == cheapest["brand_id"] or current_price == cheapest_price)
    })

@app.route("/api/manufacturers")
def get_manufacturers():
    return jsonify(load_manufacturer_index())

@app.route("/api/top_groups")
def get_top_groups():
    return jsonify(load_top_groups()[:25])

@app.route("/api/drug_classes")
def get_drug_classes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            dc.drug_class_name,
            COUNT(m.brand_id) AS total_brands,
            ROUND(AVG(m.price), 2) AS avg_price,
            ROUND(MIN(m.price), 2) AS min_price,
            ROUND(MAX(m.price), 2) AS max_price
        FROM drug_classes dc
        JOIN generics g ON dc.drug_class_id = g.drug_class_id
        JOIN medicines m ON g.generic_id = m.generic_id
        WHERE m.price IS NOT NULL
        GROUP BY dc.drug_class_id, dc.drug_class_name
        ORDER BY total_brands DESC
        LIMIT 15
    """)
    rows = cur.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "drug_class_name": r["drug_class_name"],
            "total_brands": r["total_brands"],
            "avg_price": r["avg_price"],
            "min_price": r["min_price"],
            "max_price": r["max_price"]
        })
    return jsonify(results)

if __name__ == "__main__":
    print("Starting Medicine Analytics Dashboard on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
