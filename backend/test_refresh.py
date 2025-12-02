import os
from dotenv import load_dotenv

load_dotenv()

# Test if we can get user info from the access token
access_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlN6KzZBVENzV1NGbGxLRkUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3JhY3FrcHZoYWhlaWpsaXlpcmN3LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIzMDNhNTJjZC00ZTczLTRlMmQtYjc5My0xMDcxZGE4ZDE0YTgiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY0NjU1MjU2LCJpYXQiOjE3NjQ2NTE2NTYsImVtYWlsIjoiemFrYXJpYWNueUBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiemFrYXJpYWNueUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiIzMDNhNTJjZC00ZTczLTRlMmQtYjc5My0xMDcxZGE4ZDE0YTgifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc2NDY1MTQwOH1dLCJzZXNzaW9uX2lkIjoiZGQ4MDRiZTQtZWUxNi00NDg3LWFhNTMtNTM2MDUwODIzNzRiIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.vQK5EPQXn1MqivyMmwrF30mV2gHQW5SpHwKqlvokpY4"

from supabase import create_client

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"Supabase URL: {supabase_url}")
print(f"Service key exists: {bool(supabase_key)}")

supabase = create_client(supabase_url, supabase_key)

# Try to get user from access token
try:
    # Set the session with the access token
    user_response = supabase.auth.get_user(access_token)
    print(f"\n✓ Successfully retrieved user from access token")
    print(f"User ID: {user_response.user.id}")
    print(f"Email: {user_response.user.email}")
    
    # Check expiration from JWT
    import json
    import base64
    from datetime import datetime
    
    parts = access_token.split('.')
    payload = parts[1]
    padding = len(payload) % 4
    if padding:
        payload += '=' * (4 - padding)
    
    decoded = json.loads(base64.urlsafe_b64decode(payload))
    exp_time = datetime.fromtimestamp(decoded['exp'])
    now = datetime.now()
    
    print(f"\nToken expires at: {exp_time}")
    print(f"Current time: {now}")
    print(f"Time remaining: {exp_time - now}")
    print(f"Is expired: {now > exp_time}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*50)
print("Note: To test refresh endpoint, we need the refresh_token from localStorage")
print("The refresh token is stored alongside the access token when you log in")
