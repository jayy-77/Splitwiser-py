from firebase_admin import firestore
import random
from prettytable import PrettyTable

import UPI

db = firestore.client()
def room_init(room_id,response):
        doc_ref_room = db.collection("Rooms").document(room_id)
        doc_room_data = doc_ref_room.get().to_dict()
        choice = None
        while choice != 'q':
            room_head = PrettyTable(['Room Name',doc_room_data['room_name']])
            room_head.add_row(['Index','Options'])
            room_head.add_row(['-----','-------'])
            room_head.add_row(['1','Split Request'])
            room_head.add_row(['2','Split Info'])
            room_head.add_row(['3','Payment Approvals'])
            room_head.add_row(['4','Settlement'])
            print(room_head)
            choice = int(input("choice: "))
            if choice == 1:
                split_request(room_id,response,doc_ref_room)
            elif choice == 2:
                show_split_data(room_id,response)
            elif choice == 3:
                payment_aprovals(room_id,doc_ref_room,response)
            elif choice == 4:
                payment_settlement(room_id,doc_ref_room,response)
def split_request(room_id,response,doc_ref_room):
    user_dict = {}
    split_dict = {}
    paid = []
    unpaid= []
    payment_approvals = []
    split_name = input("Split Name: ")
    total_amount = int(input("Split Amount: "))
    print("Select users")
    user_t = PrettyTable(['=>','Select users'])
    for index,user in enumerate(user_info(room_id),1):
        user_dict[index] = user
        user_t.add_row([index,user])
    print(user_t)
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
        "payment_approvals": payment_approvals
    }
    doc_ref_room.collection("Splits").document(str(random.randint(1000,9999))).set(split_dict)
    print("Split created successfully.")
def show_split_data(room_id,response):
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

    user_room_code = input("Enter room code for payment: ")
    for key,value in room_data.items():
        if user_room_code == key:
            if response.email in value['paid']:
                print("You already paid.")
            elif response.email in value['unpaid']:
                UPI.make_payment(value['split_sender'],value['split_name'],value['split_amount'])
                choice = input("Success | Failed (y/n)")
                if choice.lower() == 'y':
                    doc_split_ref.document(user_room_code).update(
                        {
                            "payment_approvals":firestore.ArrayUnion([{
                            "Amount":value['split_amount'],
                            "sender":response.email,
                            "type":"single"
                        }])}
                    )

                elif choice.lower() == 'n':
                    pass
            else:
                print("No need to pay.")
def payment_aprovals(room_id,doc_ref_room,response):
    doc_ref_room_split = doc_ref_room.collection("Splits")
    local_data = {}
    local_data_settlement = {}
    split_codes = [doc.id for doc in doc_ref_room_split.stream()]
    settlement_codes = [doc.id for doc in doc_ref_room.collection("Settlement").stream()]
    for i in split_codes:
        local_data[i] = doc_ref_room_split.document(i).get().to_dict()
    for i in settlement_codes:
        local_data_settlement[i] = doc_ref_room.collection("Settlement").document(i).get().to_dict()
    pa_table = PrettyTable(['index','Room Code','User Name','Amount','Type'])
    for room_code, room_data in local_data.items():
        for index,name in enumerate(room_data['payment_approvals']):
            pa_table.add_row([index,room_code, name['sender'], room_data['split_amount'], name['type']])
    for room_code, room_data in local_data_settlement.items():
        for index,name in enumerate(room_data['payment_approvals']):
            pa_table.add_row([index,room_code, name['sender'], name['Amount'], name['type']])
    print(pa_table)
    choice = eval(input("Enter (index,code) for payment approval: "))
    paid_user = local_data[str(choice[1])]['payment_approvals'][int(choice[0])]['sender']
    del local_data[str(choice[1])]['payment_approvals'][int(choice[0])]
    local_data[str(choice[1])]['paid'].append(paid_user)
    local_data[str(choice[1])]['unpaid'].remove(paid_user)
    doc_ref_room_split.document(str(choice[1])).update(local_data[str(choice[1])])
def payment_settlement(room_id,doc_ref_room,response):
    self_usr = 0
    opp_usr = 0
    doc_ref_room_split = doc_ref_room.collection("Splits")
    ps_table = PrettyTable(['Index','User'])
    user_list = user_info(room_id)
    for index,user in enumerate(user_list,1):
        ps_table.add_row([index,user])
    print(ps_table)
    user_choice = int(input("Which user? "))
    split_codes = [doc.id for doc in doc_ref_room_split.stream()]
    for i in split_codes:
        split_data = doc_ref_room_split.document(i).get().to_dict()
        if split_data['split_sender'] == response.email and user_list[user_choice-1] in split_data['unpaid']:
            self_usr += split_data['split_amount']
        elif split_data['split_sender'] == user_list[user_choice-1] and response.email in split_data['unpaid']:
            opp_usr += split_data['split_amount']
    if self_usr-opp_usr < 0:
        print("You have to pay",user_list[user_choice-1],abs(self_usr-opp_usr))
        UPI.make_payment(user_list[user_choice-1], split_data['split_name'], opp_usr-self_usr)
        choice = input("Success | Failed (y/n)")
        if choice.lower() == 'y':
            doc_ref_room.collection("Settlement").document(str(random.randint(1000,9999))).set(
                    {
                            "payment_approvals": firestore.ArrayUnion([{
                            "Amount": opp_usr-self_usr,
                            "sender": response.email,
                            "type":"settlement"
                        }])}
                )
        else:
            pass
    else:
        print(user_list[user_choice-1],"owe you",self_usr-opp_usr)






def user_info(room_id):
    doc_ref_user = db.collection("Rooms").document(room_id)
    return doc_ref_user.get().to_dict()['joined_users']
