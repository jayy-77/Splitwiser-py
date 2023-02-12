import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
def initialization():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
