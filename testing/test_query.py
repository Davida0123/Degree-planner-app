import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use the public anon key to simulate client-side access
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("Missing Supabase URL or ANON Key in .env file!")

# Initialize client with ANON key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def test_queries():
    print("--- TEST 1: Fetching all CMPT courses ---")
    response = (
        supabase.table("courses")
        .select("course_code, title, credits, schedule, prerequisites")
        .eq("department", "CMPT")
        .execute()
    )
    
    cmpt_courses = response.data
    print(f"Found {len(cmpt_courses)} CMPT courses.\n")
    
    for c in cmpt_courses[:5]:  # Display first 5
        print(f"[{c['course_code']}] {c['title']} | Credits: {c['credits']} | Schedule: {c['schedule']}")
        print(f"   Prereqs: {c['prerequisites']}\n")

    print("\n--- TEST 2: Searching titles with keyword 'Data' ---")
    search_response = (
        supabase.table("courses")
        .select("course_code, title")
        .ilike("title", "%Data%")  # Case-insensitive pattern match
        .execute()
    )
    
    results = search_response.data
    print(f"Found {len(results)} courses matching 'Data':")
    for row in results:
        print(f"  - {row['course_code']}: {row['title']}")

if __name__ == "__main__":
    test_queries()