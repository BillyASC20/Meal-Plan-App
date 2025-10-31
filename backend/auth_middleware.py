from functools import wraps
from flask import request, jsonify
import os
import jwt
import requests
from typing import Optional, Dict, Any

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '')

_jwt_secret: Optional[str] = None


def get_jwt_secret() -> str:
    global _jwt_secret
    
    if _jwt_secret:
        return _jwt_secret
    
    if SUPABASE_JWT_SECRET:
        _jwt_secret = SUPABASE_JWT_SECRET
        return _jwt_secret
    
    if SUPABASE_SERVICE_ROLE_KEY:
        _jwt_secret = SUPABASE_SERVICE_ROLE_KEY
        return _jwt_secret
    
    raise ValueError("SUPABASE_JWT_SECRET not configured")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print(f"Missing Supabase credentials: URL={bool(supabase_url)}, KEY={bool(supabase_key)}")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        
        user_response = supabase.auth.get_user(token)
        
        if user_response and user_response.user:
            return {
                'sub': user_response.user.id,
                'email': user_response.user.email,
                'role': 'authenticated'
            }
        
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        from flask import g
        g.user = {
            'id': payload.get('sub'),
            'email': payload.get('email'),
            'role': payload.get('role')
        }
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            payload = verify_token(token)
            
            if payload:
                from flask import g
                g.user = {
                    'id': payload.get('sub'),
                    'email': payload.get('email'),
                    'role': payload.get('role')
                }
        
        return f(*args, **kwargs)
    
    return decorated_function
