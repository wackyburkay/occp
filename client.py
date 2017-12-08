import socket
import os
import threading
import time

class UDPHelloThread(threading.Thread):

    def __init__(self, tip, tport):
        threading.Thread.__init__(self)
        self.tip = tip
        self.tport = tport

    def run(self):
        global flag
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not flag:
            try:
                socket1.sendto("HELLO".encode(), (self.tip, self.tport))
                time.sleep(1)
            except KeyboardInterrupt or socket.error:
                exit()
        exit()

class ServerBehaviorThread(threading.Thread):

    def __init__(self, conn, serverconn, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self. port = port
        self.conn = conn
        self.serverconn = serverconn

    def run(self):

        global peer_dc2
        global initiator
        global mainloop_dge
        global gotonlines
        global usr

        if not initiator:
            logf = open("OCCP-Log-for-" + usr + ".txt", "w")
            logf.write("CHATLOG OF " + usr + " - " + self.ip + "\n")
            logf.close()

        while True:
            try:
                data = self.conn.recv(2048).decode()
                if (not data) or (data == "/disconnect"):
                    raise Exception
                else:
                    logf = open("OCCP-Log-for-" + usr + ".txt", "a")
                    logf.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " - Peer says: " + data + "\n")
                    logf.close()
                    print("Peer says: ", data)
            except:
                if (not initiator) and (not peer_dc2):
                    self.serverconn.send("PCHATEND".encode())

                if not peer_dc2:
                    os.system(cleaning)
                    print("Peer disconnected or rejected connection. Press enter to continue.")
                    global peer_dc
                    peer_dc = True
                peer_dc2 = False
                mainloop_dge = False
                gotonlines = False
                exit()

class ClientBehaviorThread(threading.Thread):

    def __init__(self, conn, serverconn, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.serverconn = serverconn

    def run(self):
        global peer_dc
        global peer_dc2
        global initiator
        global mainloop_dge
        global gotonlines
        global usr

        while True:
            try:
                if(peer_dc):
                    break

                data = input()
                logf = open("OCCP-Log-for-" + usr + ".txt", "a")
                logf.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " - You: " + data + "\n")
                logf.close()
                self.conn.send(data.encode())

                if data == "/disconnect":
                    try:
                        os.system(cleaning)
                        print("You have been disconnected from peer.\n")
                        peer_dc2 = True
                        self.serverconn.send("PCHATEND".encode())
                        self.conn.close()
                    except:
                        print("Server disconnected. Closing.")
                    mainloop_dge = False
                    gotonlines = False
                    exit()

            except socket.error:
                try:
                    if initiator == True:
                        initiator = False
                        self.serverconn.send("PCHATEND".encode())
                        self.conn.close()
                    peer_dc = False
                except:
                    print("Server disconnected. Closing.")
                mainloop_dge = False
                gotonlines = False
                exit()

        peer_dc = False
        try:
            if initiator == True:
                initiator = False
                self.serverconn.send("PCHATEND".encode())
        except:
            print("Server disconnected. Closing.")
        mainloop_dge = False
        gotonlines = False
        exit()

class ListenerThread(threading.Thread):

    def __init__(self, serverconn):
        threading.Thread.__init__(self)
        self.addr = '0.0.0.0'
        self.port = 8082
        self.serverconn = serverconn

    def run(self):
        socketL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketL.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketL.bind((self.addr, self.port))

        global mainloop_dge
        global gotonlines

        while True:
            try:
                socketL.listen(1)
                (conn, (ip, port)) = socketL.accept()
                mainloop_dge = True
                self.serverconn.send("PCRECVD".encode())
                self.serverconn.send(ip.encode())
                tmpstr = "You have a connection request from " + ip + ", would you like to accept? (y/n):"
                accorno = input(tmpstr)

                if accorno == "n":
                    os.system(cleaning)
                    conn.close()
                    self.serverconn.send("PCHATREJ".encode())
                    gotonlines = False
                    mainloop_dge = False
                else:
                    os.system(cleaning)
                    print("You are now connected to ", ip, "\nType in '/disconnect' to disconnect.", sep="")
                    newthread2 = ClientBehaviorThread(conn, self.serverconn, ip, port)
                    newthread2.start()
                    newthread = ServerBehaviorThread(conn, self.serverconn, ip, port)
                    newthread.start()
            except KeyboardInterrupt:
                exit()

if os.name ==  'nt':
    cleaning = 'cls'
else:
    cleaning = 'clear'

os.system(cleaning)
print("\t\t\t\t\t\t.ıilI||| ClientApp |||Iliı.\n")
usr = ""
pw = ""
while True:
    try:
        usr, pw = input("Enter username and password, with whitespace between: ").split(" ")
        break
    except:
        print("You typed in an incorrect input. Please try again.")

logfi = open("OCCP-Log-for-" + usr + ".txt", "w")
logfi.write("")
logfi.close()

socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket2.connect((socket._LOCALHOST, 8080))
usr_pw_couple = usr + " " + pw
socket2.send(usr_pw_couple.encode())
regcomplete = 0
onlinelist = []
oniplist = []
gotonlines = False
dont_send_or_recv = False
yss = False
threadlist = []
peer_dc = False
peer_dc2 = False
initiator = False
mainloop_dge = False
inputlist = ["listen", "search", "connect", "/quit"]

listener = ListenerThread(socket2)
listener.daemon = True
listener.start()

#UDP Boii-----------------------------------------

flag = False
udpthread = UDPHelloThread(socket2.getpeername()[0], socket2.getsockname()[1])
udpthread.start()
threadlist.append(udpthread)

#-------------------------------------------------

while True:
    if mainloop_dge:
        continue
    try:
        if not dont_send_or_recv:
            data = socket2.recv(2048).decode()
            RESPCODE, MSG = data.split("-")

        #Client side of registration
        if ((RESPCODE == "ERR_NARU") or (RESPCODE == "ERR_AON")) and (not dont_send_or_recv):
            print("Server response: ", MSG)

            selection = "a"
            while selection.lower() != "exit":
                selection = input("Enter seleciton here: ")

                if(selection == "r" or selection == "R"):
                    socket2.send(selection.encode())
                    os.system(cleaning)
                    proc = "a"

                    while proc != "y":

                        usr_pw_couple = input("Enter an ID / PW couple, seperated by space: ")
                        print("Your ID / PW is: ", usr_pw_couple, "\nDo you want to proceed? (y/n)", sep="")
                        proc = input()

                    os.system(cleaning)
                    print("Sending your ID / PW to the registry server.")
                    socket2.send(usr_pw_couple.encode())
                    register_stat = socket2.recv(2048).decode()

                    while register_stat != "SUCCESS":
                        print("That ID is in use. Please enter different one.\nEnter here:")
                        usr_pw_couple = input()
                        socket2.send(usr_pw_couple.encode())
                        register_stat = socket2.recv(2048).decode()
                    regcomplete = 1
                    usr, pw = usr_pw_couple.split(" ")
                    print("Successfully registered, logged in.")
                    break

                elif selection.lower() == "/quit":
                    flag = True
                    socket2.send(selection.encode())
                    udpthread.join()
                    exit()

                else:
                    print("Incorrect input.")
        #----------------------------------------------------------------------------------------

        elif (RESPCODE == "RETON") and (not dont_send_or_recv):
            onlinelist = []
            oniplist = []
            onlinelist = MSG.split("\n")
            onlinelist.remove("")

            print("\n")
            for x in onlinelist:
                temp = x.split(" ")
                oniplist.append((temp[0], temp[1]))
                print(x)
            print("\n")
            print("Use 'connect' as instructed to connect one of the users listed above.")
            gotonlines = True


        elif not yss:
            print("Server response: ", MSG)

        yss = False
        dont_send_or_recv = False
        msg = input("To just listen for incoming connections, type 'listen'. To get list of online users, type 'search'. To connect a user, type 'connect' To quit, enter '/quit'.\nEnter Here: ")

        while msg not in inputlist:
            print("Your options are 'listen', 'search', 'connect' and '/quit'. Please use one of these.\nEnter Here: ")
            msg = input()

        if msg == "/quit" and not mainloop_dge:
            flag = True
            socket2.send(msg.encode())
            udpthread.join()
            exit()

        elif msg == "connect" and not mainloop_dge:
            if gotonlines == False:
                print("ERROR: You should search for online users first!")
                dont_send_or_recv = True
                yss = True
            else:
                yss = False
                uname = input("Enter the username of the peer you want to connect: ")

                while uname not in (row[0] for row in oniplist  ):
                    print("That user is not online or does not exist.")
                    uname = input("Enter the username of the peer you want to connect: ")

                peer_ip = ""
                for x in oniplist:
                    if x[0] == uname:
                        peer_ip = x[1]
                        break
                initiator = True
                socketC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socketC.connect((peer_ip, 8082))
                socket2.send("connect".encode())
                socket2.send(uname.encode())
                os.system(cleaning)
                logfi = open("OCCP-Log-for-" + usr + ".txt", "w")
                logfi.write("CHATLOG OF " + usr + " - " + uname + "\n")
                logfi.close()
                print("You are now connected to ", peer_ip, "\nType in '/disconnect' to disconnect.")
                servthread = ServerBehaviorThread(socketC, socket2, peer_ip, socketC.getpeername()[1])
                servthread.start()
                clithread = ClientBehaviorThread(socketC, socket2, peer_ip, socketC.getpeername()[1])
                clithread.start()

        elif not mainloop_dge:
            socket2.send(msg.encode())

    except KeyboardInterrupt:
            flag = True
            udpthread.join()
            socket2.send("CLI_FORCED".encode())
            exit()
    except socket.error:
            print("ERROR: Server disconnected. Closing.")
            flag = True
            exit()



socket2.close()
exit()
