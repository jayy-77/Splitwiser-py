import Authentication
from firebase_admin import firestore
import UserData
import random
db = firestore.client()
response = Authentication.init()

if response != False:
    print("Signed in successfully to Splitwiser.")
    userData = UserData.load_user_data(response.email)
    headFormat ="Email: {} || UPI: {}".format(response.email,userData['UPI'])
    print("*"*(len(headFormat)+4))
    print("*",headFormat,"*")
    print("*"*(len(headFormat)+4))
    print("1.Create a Room.\n2.Join a Room\n3.Show joined Rooms.\n")
    choice = 'w'
    doc_ref_per = db.collection("Users").document(response.email)
    while choice != 'q':
        choice = input("Enter Choice: ")

        if choice == '1':
            code = random.randint(1000,9999)
            doc_ref = db.collection("Rooms").document(str(code))
            roomName = input("Room Name: ")
            doc_ref.set({"room_name":roomName,"joined_users":[response.email]})
            doc_ref_per.update({"joined_rooms":firestore.ArrayUnion([code])})

        elif choice == '2':
            code_input = (input("Enter room code: "))
            room_codes = [doc.id for doc in db.collection("Rooms").stream()]
            for i in room_codes:
                if code_input == i:
                    doc_ref = db.collection("Rooms").document(code_input)
                    doc_ref_per.update({"joined_rooms": firestore.ArrayUnion([code_input])})
                    doc_ref.update({"joined_users":firestore.ArrayUnion([response.email])})
                else:
                    print("No room exits.")

        elif choice == '3':
            doc_ref = db.collection("Users").document(response.email)
            data = doc_ref.get()
            room_dict = {}
            code_list = data.to_dict()['joined_rooms']
            for index,code in enumerate(code_list,1):
                doc_ref = db.collection("Rooms").document(str(code))
                room_dict[index] = doc_ref.id
                print(index,doc_ref.get().to_dict()['room_name'])
        else:
            print("Wrong input.")
else:
    exit()