import Authentication
from firebase_admin import firestore
from prettytable import PrettyTable
import UserData
import random
import Room
db = firestore.client()
response = Authentication.init()

if response != False:
    print("Signed in successfully to Splitwiser.")
    userData = UserData.load_user_data(response.email)
    t_head = PrettyTable(['Email', 'UPI'])
    t_head.add_row([response.email,userData['UPI']])
    print(t_head)
    choice = None
    doc_ref_per = db.collection("Users").document(response.email)
    while choice != 'q':
        t = PrettyTable(['Index', 'Options'])
        t.add_row(['1', 'Create a Room'])
        t.add_row(['2', 'Join a Room'])
        t.add_row(['3', 'Show Rooms'])
        print(t)
        choice = input("Enter Choice: ")

        if choice == '1':
            code = random.randint(1000,9999)
            doc_ref = db.collection("Rooms").document(str(code))
            roomName = input("Room Name: ")
            doc_ref.set({"room_name":roomName,"joined_users":[response.email]})
            doc_ref_per.update({"joined_rooms":firestore.ArrayUnion([code])})
            print("Room created successfully.")

        elif choice == '2':
            code_input = (input("Enter room code: "))
            room_codes = [doc.id for doc in db.collection("Rooms").stream()]
            for i in room_codes:
                if code_input == i:
                    doc_ref = db.collection("Rooms").document(code_input)
                    doc_ref_per.update({"joined_rooms": firestore.ArrayUnion([code_input])})
                    doc_ref.update({"joined_users":firestore.ArrayUnion([response.email])})
                    print("Successfully joined room")
                    break
            else:
                print("Room not found.")

        elif choice == '3':
            doc_ref = db.collection("Users").document(response.email)
            room_dict = {}
            code_list = doc_ref.get().to_dict()['joined_rooms']
            t_room = PrettyTable(['Index', 'Rooms'])
            for index,code in enumerate(code_list,1):
                doc_ref = db.collection("Rooms").document(str(code))
                room_dict[index] = doc_ref.id
                t_room.add_row([index,doc_ref.get().to_dict()['room_name']])
            print(t_room)
            room_input = int(input("Which Room ??: "))
            Room.room_init(room_dict[room_input],response)
        else:
            print("Wrong input.")
else:
    exit()