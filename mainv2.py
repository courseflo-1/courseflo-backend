import os
from supabase import create_client, Client
import config

url: str = config.SUPABASE_URL
key: str = config.SUPABASE_KEY
supabase: Client = create_client(url, key)

res = supabase.table('Courses').select('*').execute()

print(res)