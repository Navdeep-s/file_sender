# # importing tkinter module
from tkinter import *
from tkinter.ttk import *
import time
from tkinter import filedialog



import socket
import os
import threading

import sys
class ClientKill(Exception):
    pass





#change the file saving path to your own
saving_file_path = "E:\\mobile_downloads"



# os.chdir(saving_file_path)
# if len(sys.argv)<2:
#     print("type ip of your machine")
#     sys.exit()
# else:
#     ip = sys.argv[1]
#
#     print (ip)

ip = "192.168.43.204"
count = -1


progress_bars = []
permanent_client = None

path_to_file =[]

# creating tkinter window
root = Tk()

# Progress bar widget



label_file_explorer = Label(root,
                            text="mera awda software :) :)")



# Function responsible for the updation
# of the progress bar value

def browseFiles():
    filename = filedialog.askopenfilenames(initialdir="/",
                                          title="Select a File",
                                          )

    # Change label contents
    return filename


def i_dont():
    global path_to_file,permanent_client
    path_to_file=list(browseFiles())
    y = len(path_to_file)
    no_of_files = ((y).to_bytes(4, "big"))
    print(path_to_file)
    print(y)
    print(no_of_files)
    permanent_client.send(no_of_files)




def make_bar1(file_name):
        progress = Progressbar(root, orient=HORIZONTAL,
                               length=100, mode='determinate')


        label = Label(root,text=file_name)

        label.pack(pady=2)

        progress.pack(pady=10)
        return (progress,label)


    # for k in range(100):
    #     progress['value'] =k
    #     root.update_idletasks()
    #     time.sleep(.01)

label_file_explorer.pack(pady = 10)

# This button will initialize
# the progress bar
Button(root, text = 'Send', command = i_dont).pack(pady = 10)







k=socket.gethostbyname(socket.gethostname())





def file_sender(client_local,file_path,progress):
    file_name = file_path.split("/")[-1]
    statinfo = os.stat(file_path)
    no_of_bites = statinfo.st_size
    #print(no_of_bites)
    size = ((no_of_bites).to_bytes(4, "big"))
    file_byte_name = (bytes(file_name,"utf-8"))
    print("sending size of file",no_of_bites)
    client_local.send(size)
    client_local.send(len(file_byte_name).to_bytes(4,"big"))
    client_local.send(file_byte_name)


    y = open(file_path,"rb")
    sended = 0
    while True:
        read_bytes = y.read(1024)
        if not read_bytes:
            break
        client_local.sendall(read_bytes)
        sended = sended + len(read_bytes)
        p_value = (sended*100/no_of_bites)
        progress['value'] = p_value
        root.update_idletasks()


    just_end = recieve_certain(client_local,4)
    print(file_name,"done")
    size = ((no_of_bites).to_bytes(4, "big"))
    print("finally_closed")
    #print("done")

    # client_local.close()



def send_file(client):
    global path_to_file
    file_path=path_to_file[0]
    print(file_path)
    path_to_file.remove(file_path)

    # print(count)
    #print(path_to_file)
    #print("holla")
    # for path in path_to_file:
    #     print(path_to_file)
    file_name = file_path.split("/")[-1]
    progress_this= make_bar1(file_name)[0]


    file_sender(client,file_path,progress_this)
    # print(path_to_file[count])

        # path_to_file.remove(path)


def recieve_certain(client,n):
    a=client.recv(n)
    remaining = n-len(a)
    while remaining>0:
        a = a+client.recv(remaining)
        remaining = n - len(a)
    return a

def reciver(client):
    os.chdir(saving_file_path)

    #print("starting ")
    buffer_size = 1024
    a=recieve_certain(client,8)#reciving file length as 8 byte long big endian
    size_of_file = int.from_bytes(a, byteorder='big', signed=False)

    a = recieve_certain(client,4)#recieving name length as 4 byte interger big endian
    size_of_name = int.from_bytes(a, byteorder='big', signed=False)


    a = recieve_certain(client,size_of_name)
    name_of_file = a.decode()


    while (os.path.exists(name_of_file)):
        name_of_file =str(1)+name_of_file


    remaining_file = size_of_file
    print("starting "+ name_of_file+" "+" "+str(size_of_file) +"bytes")
    print(name_of_file)
    y = open(name_of_file,"wb")
    dize=0
    while remaining_file>0:
        if(remaining_file<buffer_size):
            size_to_receive = remaining_file

        else:
            size_to_receive = buffer_size

        k=client.recv(size_to_receive)
        # #print(len(k))
        remaining_file = remaining_file -len(k)
        y.write(k)
        dize = dize +size_to_receive
        # #print(dize)
        # #print(k)
        # #print(remaining_file)

    y.close()
    print("done {}".format(name_of_file+os.getcwd()))
    # client.close()




def handle_permanent_client(client):
    global path_to_file
    while (True):
        y=input("enter file path")

        if(os.path.exists(y)):
            #print("sending")
            path_to_file.append(y)
            k = ((1).to_bytes(4, "big"))
            #print(k)
            client.send(k)
        else:
            print(y,"does not exit")


def connection_manager(client):
    global permanent_client,count
    k = recieve_certain(client, 4)
    #print("int client manager")
    acknowledge_ment = int.from_bytes(k, byteorder='big', signed=False)
    if(acknowledge_ment == 33):
        permanent_client = client
        count = -1
        # threading.Thread(target=handle_permanent_client, args=(permanent_client,)).start()
    elif(acknowledge_ment == 22):
        count = count + 1

        threading.Thread(target=send_file, args=(client,)).start()
        print("connection"+str(count))
    else:
        threading.Thread(target=reciver, args=(client,)).start()

def do_stuff():
    port = 8080
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((ip, port))
        listener.listen(5)
        # time.sleep(0.07)

        try:
            while True:
                client, addr = listener.accept()
                connection_manager(client)

        except ClientKill:
            print("Server killed by remote client")



threading.Thread(target=do_stuff, args=()).start()

def doSomething():
    # check if saving
    # if not:
    root.destroy()
    print("Thanks for useing")
    os._exit(1)
root.protocol('WM_DELETE_WINDOW', doSomething)  # root is your root window



mainloop()



