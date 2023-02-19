import webbrowser
import urllib.parse
import qrcode
import random
from firebase_admin import firestore
db = firestore.client()
def make_payment(email,note,amount):
    user_doc_ref = db.collection("Users").document(email)
    payment_dict = {
        "pa": user_doc_ref.get().to_dict()['UPI'],
        "pn": email,
        "tr": random.randint(10000,99999),
        "tn": note,
        "am": amount,
        "cu": "INR"
    }
    upi_deep_link = "upi://pay" + '?' + urllib.parse.urlencode(payment_dict)
    img = qrcode.make(upi_deep_link)
    img.save('upi.png')
    webbrowser.open('upi.png')
