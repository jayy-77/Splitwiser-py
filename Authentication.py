import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

global upi
db = firestore.client()

import UserData

def init():
    print("Welcome to Splitwiser\nAuthentication Page: \n")
    email = "a@gmail.com"
    password = "qwerty"
    signinResponse = sign_in(email,password)

    if signinResponse == False:
        print("New user ? Enter UPI to signup here.")
        upi = input("UPI: ")
        return store_credentials(sign_up(email, password),upi,password)
    elif signinResponse:
        return sign_in(email, password)
    else:
        return False

def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user
    except Exception as error:
        print("Sign up failed: {}".format(error))
        return False

def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        if UserData.load_user_data(user.email)['Password'] == password:
            return user
        else:
            print("Wrong credentials.")
            return
    except Exception as error:
        print("Sign in failed: {}".format(error))
        return False

def store_credentials(user,upi,password):
    try:
        doc_ref = db.collection("Users").document(user.email)
        doc_ref.set({"Email:":user.email,"UPI":upi,"Password":password})
    except Exception as error:
        print("Error stroring user credentials {}".format(error))
        return False
    else:
        print("Credentials stored successfully.")
        return user