import os
from supabase import create_client, Client
import config

url: str = config.SUPABASE_URL
key: str = config.SUPABASE_KEY
supabase: Client = create_client(url, key)

"""
The fetch functions return a list of dictionaries which contain row values
"""
def fetch_schools() -> list:
    res = supabase.table('Schools').select('*').execute()
    return list(res.data)

def fetch_majors(school: int) -> list:
    res = supabase.table('Curriculum').select('*').eq('school', school).eq('type', "major").execute()
    return list(res.data)

def fetch_minors(school: int) -> list:
    res = supabase.table('Curriculum').select('*').eq('school', school).eq('type', "minor").execute()
    return list(res.data)

def fetch_unique_courses(school: int) -> list:
    res = supabase.table('Courses').select('*').eq('school', school).execute()
    return list(res.data)

# Retrieve course from course id (found in curriculum for example)
def get_course(school: int, id: int) -> dict:
    data = fetch_unique_courses(school)
    for course in data:
        if course['id'] == id:
            return course
