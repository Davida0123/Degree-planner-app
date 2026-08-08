import json
import os
from dotenv import load_dotenv #run `pip install python-dotenv prior`
from supabase import create_client, Client #run `python -m pip isntall supabase`

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials securely from the environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Safety check to ensure variables loaded correctly
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env file!")

JSON_FILE = "MacEwan_courses.json"

def upload_to_supabase():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) #supabase is var holding your connection instance
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    records = [] #list of dictionaries(varying course data)
    #read and preserve structure from uni json
    for ccode, data in catalog.items():
        records.append({
            "course_code": ccode,
            "department": data.get("Department", ""),
            "title": data.get("Title", "N/A"),
            "credits": data.get("Credits", "N/A"),
            "schedule": data.get("Schedule", "N/A"),
            "description": data.get("Description", ""),
            "prerequisites": data.get("Prerequisites", "N/A"),
            "restrictions": data.get("Restrictions", []),
            "notes": data.get("Notes", [])
        })

    BATCH_SIZE = 500 #num of courses per batch 
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        supabase.table("courses").upsert(batch).execute() #target the created table at supabase and insert rows(batch) with respective data. Mirrors standard querying.
        print(f"Uploaded batch {i // BATCH_SIZE + 1} / {(len(records) + BATCH_SIZE - 1) // BATCH_SIZE}") #int divison to find zero-indexed batch lop count(+1 for readability)

    print("Success! Catalog imported into Supabase PostgreSQL.")

if __name__ == "__main__":
    upload_to_supabase()