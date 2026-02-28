import sqlite3
import json
import os
from global_func import resource_path

def export_materials_to_json(db_path, output_file):
    # Ensure the db_path is correctly resolved
    conn = sqlite3.connect(resource_path(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT product_id, product_name, materials FROM products")
    rows = cursor.fetchall()

    export_data = []

    for product_id, product_name, materials_string in rows:
        try:
            materials_dict = json.loads(materials_string) 
        except json.JSONDecodeError:
            materials_dict = {"raw": materials_string} 

        export_data.append({
            "product_id": product_id,
            "product_name": product_name,
            "materials": materials_dict
        })

    # Write to JSON file
    with open(output_file, 'w') as file:
        json.dump(export_data, file, indent=4)

    conn.close()
    print(f"✅ Exported to {output_file}")

# Run it
export_materials_to_json("main.db", resource_path(os.path.join("json_f", "products_materials.json")))
