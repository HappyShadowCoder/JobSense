import os
from functools import wraps
from flask import request, jsonify

def clerk_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        print("=== Auth header:", auth_header[:50] if auth_header else "NONE")
        
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ")[1]
        print("=== Token received, length:", len(token))

        try:
            import jwt as pyjwt
            unverified = pyjwt.decode(token, options={"verify_signature": False})
            print("=== Decoded token:", unverified)
            clerk_user_id = unverified.get("sub")
            print("=== Clerk user ID:", clerk_user_id)

            if not clerk_user_id:
                return jsonify({"error": "Invalid token"}), 401

            from utils.db import query_one, execute
            user = query_one(
                "SELECT id FROM users WHERE clerk_id = %s",
                (clerk_user_id,)
            )
            print("=== DB user found:", user)

            if not user:
                user = execute(
                    """
                    INSERT INTO users (clerk_id)
                    VALUES (%s)
                    ON CONFLICT (clerk_id) DO UPDATE SET clerk_id = EXCLUDED.clerk_id
                    RETURNING id
                    """,
                    (clerk_user_id,),
                    returning=True
                )
                print("=== New user created:", user)

            request.user_id = str(user["id"])
            print("=== request.user_id set to:", request.user_id)
            return f(*args, **kwargs)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("=== ERROR:", str(e))
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401

    return decorated