from firebase_admin import firestore
db = firestore.client()

def load_user_data(email):
    try:
        doc_ref = db.collection("Users").document(email)
        doc = doc_ref.get()
        return doc.to_dict()
    except Exception as error:
        print("Error reading document: {}".format(error))
        return None

