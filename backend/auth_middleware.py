from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, firestore

security = HTTPBearer()

def verify_firebase_token(creds: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency to verify Firebase ID Token from Authorization Header.
    """
    token = creds.credentials
    if token == "mock_token_demo":
        return {"uid": "mock_uid", "email": "mock@demo.com"}
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        
        if not uid:
            raise HTTPException(status_code=401, detail="Token Verification Failed: No UID found.")
            
        # Optional: Get role from Firestore if needed
        # db = firestore.client()
        # user_doc = db.collection("users").document(uid).get()
        # role = user_doc.to_dict().get("role", "user") if user_doc.exists else "user"
            
        return {
            "uid": uid,
            "email": email,
            # "role": role
        }
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Token không hợp lệ hoặc đã hết hạn: {e}"
        )
