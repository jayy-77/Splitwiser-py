import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

auth = firebase_admin.auth

def sign_in_with_google(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        user = auth.get_user(uid)
        return user
    except Exception as error:
        print(f"Sign in with Google failed: {error}")
        return None

# Example usage:

id_token = "ID_TOKEN_FROM_GOOGLE_SIGN_IN"

user = sign_in_with_google(id_token)

if user:
    print(f"Sign in with Google succeeded. User: {user}")
else:
    print("Sign in with Google failed.")
