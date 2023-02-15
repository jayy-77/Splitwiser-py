from firebase_admin import firestore
import random
from prettytable import PrettyTable
db = firestore.client()
def room_init(room_id,response):
        doc_ref_room = db.collection("Rooms").document(room_id)
        doc_room_data = doc_ref_room.get().to_dict()
        print("Room Name:",doc_room_data['room_name'])
        print("1.Split Request\n2.Split Info\n")
        choice = None
        while choice != 'q':
            choice = int(input("choice: "))
            if choice == 1:
                split_request(room_id,response,doc_ref_room)
            elif choice == 2:
                show_split_data(room_id)
def split_request(room_id,response,doc_ref_room):
    user_dict = {}
    split_dict = {}
    paid = []
    unpaid= []
    split_name = input("Split Name: ")
    total_amount = int(input("Split Amount: "))
    print("Select users")
    for index,user in enumerate(user_info(room_id),1):
        user_dict[index] = user
        print(index,user)
    select_user_input = eval(input())
    select_user_list = [user_dict[i] for i in select_user_input]
    total_user = len(select_user_list)
    if response.email in select_user_list:
        paid.append(response.email)
        select_user_list.remove(response.email)
        unpaid.extend(select_user_list)
    else:
        unpaid.extend(select_user_list)

    split_dict = {
        "split_sender":response.email,
        "split_name":split_name,
        "total_amount":total_amount,
        "split_amount":total_amount/total_user,
        "unpaid":unpaid,
        "paid": paid,
    }
    doc_ref_room.collection("Splits").document(str(random.randint(1000,9999))).set(split_dict)
    print("Split created successfully.")
def show_split_data(room_id):
    room_data = {}
    doc_split_ref = db.collection("Rooms").document(room_id).collection("Splits")
    split_codes = [doc.id for doc in doc_split_ref.stream()]
    for i in split_codes:
        room_data_dict = doc_split_ref.document(i).get().to_dict()
        room_data[i] = room_data_dict
    for key,value in room_data.items():
        split_head = PrettyTable(['Code: '+key,'Split Name: '+value['split_name']])
        split_head.add_row(['Split Sender: ',value['split_sender']])
        split_head.add_row(['Amount: ',value['split_amount']])
        split_head.add_row(['Total Amount: ',value['total_amount']])
        split_head.add_row(['Paid: ',value['paid']])
        split_head.add_row(['UnPaid: ',value['unpaid']])
        print(split_head)
def user_info(room_id):
    doc_ref_user = db.collection("Rooms").document(room_id)
    return doc_ref_user.get().to_dict()['joined_users']
