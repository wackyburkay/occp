import socket
import threading
import os
import time

if os.name ==  'nt':
    cleaning = 'cls'
else:
    cleaning = 'clear'

class ClientUDPThread(threading.Thread):

    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("New UDP thread also started for client ", ip, ":", port)

    def run(self):
        global quitted
        starttime = time.time()
        data = "none"
        udptimeout = 0
        udpsock = sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsock.bind(('0.0.0.0', self.port))
        udpsock.setblocking(0)
        while udptimeout < 6:
            try:
                data = udpsock.recvfrom(1024)[0].decode()
                udptimeout = 0
                starttime = time.time()
            except:
                udptimeout = time.time() - starttime
                time.sleep(0.25)
                data = "none"

        if not quitted:
            print("LOG:TIMED_OUT-", self.ip, ":", self.port)

        if quitted:
            quitted = False

        exit()

class ClientHandlerThread(threading.Thread):

    def __init__(self, conn, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        if self.ip == '127.0.0.1':
            self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.conn = conn
        print("New handler thread started for client ", ip, ":", port)

    def run(self):
        global busylist
        global quitted
        camefromregister = 0
        notregisteredq = False
        broke_register = False
        t_usr, t_pw = self.conn.recv(2048).decode().split(" ")
        logfile = open("OCCP-SERVER-LOG.txt", "a")
        logfile.write("LOG:CONN_ATTEMPT-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
        logfile.close()
        print("LOG:CONN_ATTEMPT-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
        peerchat_peer = []

        udepetred = ClientUDPThread(self.ip, self.port)
        udepetred.start()

        registry = [t_usr, t_pw, 0, 0]
        registry_on = [t_usr, t_pw, 1, self.ip]

        if ((registry in clientlist) or camefromregister) and (registry_on not in onlinelist):
            self.conn.send("MSG-You are now connected to registry server.".encode())
            logfile = open("OCCP-SERVER-LOG.txt", "a")
            logfile.write("LOG:CONNECTED_USR-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
            logfile.close()
            print("LOG:CONNECTED_USR-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
            onlinelist.append(registry_on)

        else:
            try:
                if registry_on in onlinelist:
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:CONN_REJ_AON-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                    logfile.close()
                    print("LOG:CONN_REJ_AON-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                    self.conn.send("ERR_NARU-That account is already online. Type 'r' to register with different account, or '/quit' to close connection.".encode())
                else:
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:CONN_REJ_NARU-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                    logfile.close()
                    print("LOG:CONN_REJ_NARU-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                    self.conn.send("ERR_NARU-You are not a registered user. Type 'r' to register, or '/quit' to close connection.".encode())
                client_selection = self.conn.recv(2048).decode()
                if client_selection == "/quit":
                    notregisteredq = True
                elif client_selection.lower() == "r":
                    r_usr, r_pw = self.conn.recv(2048).decode().split(" ")
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:REGISTER_REQUEST-" + self.ip + ":" + str(self.port) + "-un:" + r_usr + "-pw:" + r_pw + "\n")
                    logfile.close()
                    print("LOG:REGISTER_REQUEST-", self.ip, ":", self.port, "-un:", r_usr, "-pw:", r_pw, sep="")
                    registry = [r_usr, r_pw, 0, 0]
                    registry_on = [r_usr, r_pw, 1, self.ip]

                    while ((registry[0] in (row[0] for row in clientlist)) or (registry_on[0] in (row[0] for row in onlinelist))):
                        logfile = open("OCCP-SERVER-LOG.txt", "a")
                        logfile.write("LOG:USRPW_IN_USE-" + self.ip + ":" + str(self.port) + "-un:" + r_usr + "-pw:" + r_pw + "\n")
                        logfile.close()
                        print("LOG:USRPW_IN_USE-", self.ip, ":", self.port, "-un:", r_usr, "-pw:", r_pw, sep="")
                        self.conn.send("IN_USE".encode())
                        r_usr, r_pw = self.conn.recv(2084).decode().split(" ")
                        registry = [r_usr, r_pw, 0, 0]
                        registry_on = [r_usr, r_pw, 1, self.ip]

                    broke_register = True
                    onlinelist.append(registry_on)
                    self.conn.send("SUCCESS".encode())
                    t_usr = r_usr
                    t_pw = r_pw
                    camefromregister = 1
                    #print(clientlist, onlinelist)

            except socket.error:
                time.sleep(6.08)
                logfile = open("OCCP-SERVER-LOG.txt", "a")
                logfile.write("LOG:USR_FORCED_DC-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                logfile.close()
                print("LOG:USR_FORCED_DC-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                if broke_register:
                    onlinelist.remove(registry_on)
                    if registry not in clientlist:
                        clientlist.append(registry)
                    file_writer(clientlist)
                exit()

            if notregisteredq:
                logfile = open("OCCP-SERVER-LOG.txt", "a")
                logfile.write("LOG:USER_QUITTED_REG-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                logfile.close()
                print("LOG:USER_QUITTED_REG-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                quitted = True
                exit()

        broke_register = False
        while True:
            try:
                data = self.conn.recv(2048).decode()

                if data == "PCHATEND" or data == "PCHATREJ":
                    if(peerchat_peer not in onlinelist) and (registry_on not in onlinelist):
                        onlinelist.append(peerchat_peer)
                        onlinelist.append(registry_on)
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:PEER_CHAT_ENDED-p1:" + registry_on[0] + "-p2:" + peerchat_peer[0] + "\n")
                    logfile.close()
                    print("LOG:PEER_CHAT_ENDED-p1:", registry_on[0], "-p2:", peerchat_peer[0], sep="")
                    self.conn.send("MSG-You are now connected to registry server.".encode())

                elif data == "PCRECVD":
                    tmpip = self.conn.recv(2048).decode()
                    print(tmpip)
                    time.sleep(2)

                    for ipo in busylist:
                        if ipo[3] == tmpip:
                            peerchat_peer = ipo
                            break

                elif data == "/quit":
                    quitted = True
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:USR_QUIT-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                    logfile.close()
                    print("LOG:USR_QUIT-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                    onlinelist.remove(registry_on)
                    if registry not in clientlist:
                        clientlist.append(registry)
                    file_writer(clientlist)
                    exit()

                elif data == "listen":
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:USR_LISTEN-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                    logfile.close()
                    print("LOG:USR_LISTEN-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")

                elif data == "search":
                    retonlist = ""
                    for x in range(len(onlinelist)):
                        retonlist = retonlist + onlinelist[x][0] + " " + onlinelist[x][3] + "\n"
                    self.conn.send(("RETON-" + retonlist).encode())

                elif data == "connect":
                    uname = self.conn.recv(2048).decode()
                    for u in onlinelist:
                        if u[0] == uname:
                            peerchat_peer = u
                            break
                    onlinelist.remove(registry_on)
                    onlinelist.remove(peerchat_peer)
                    busylist.append(registry_on)
                    busylist.append(peerchat_peer)
                    print(busylist)
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:PEER_CHAT_STARTED-p1:" + registry_on[0] + "-p2:" + peerchat_peer[0] + "\n")
                    logfile.close()
                    print("LOG:PEER_CHAT_STARTED-p1:", registry_on[0], "-p2:", peerchat_peer[0], sep="")

                elif data == "CLI_FORCED":
                    time.sleep(6.08)
                    logfile = open("OCCP-SERVER-LOG.txt", "a")
                    logfile.write("LOG:USR_FORCED_DC-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                    logfile.close()
                    print("LOG:USR_FORCED_DC-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                    onlinelist.remove(registry_on)
                    if registry not in clientlist:
                        clientlist.append(registry)
                    file_writer(clientlist)
                    exit()

                else:
                    print(data)
                    #conn.send(("MSG-" + input()).encode())
            except socket.error:
                time.sleep(6.08)
                logfile = open("OCCP-SERVER-LOG.txt", "a")
                logfile.write("LOG:USR_FORCED_DC-" + self.ip + ":" + str(self.port) + "-un:" + t_usr + "-pw:" + t_pw + "\n")
                logfile.close()
                print("LOG:USR_FORCED_DC-", self.ip, ":", self.port, "-un:", t_usr, "-pw:", t_pw, sep="")
                if registry_on in onlinelist:
                    onlinelist.remove(registry_on)
                if registry not in clientlist:
                    clientlist.append(registry)
                file_writer(clientlist)
                exit()


#for writing client list to file
def file_writer(clist):

    client_list_f = open("clientlist.txt", "w")

    for client in clist:
        client_list_f.write(client[0]+ " " + client[1] + "\n")

    client_list_f.close()

#for reading client list from file into clientlist
def file_reader(clist):

    client_list_f = open("clientlist.txt", "r")

    for line in client_list_f:
        a, b = line.strip("\n").split(" ")
        clist.append([a, b, 0, 0])

    client_list_f.close()

os.system(cleaning)
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind(('0.0.0.0', 8080))
quitted = False
threadlist = []
clientlist = []
onlinelist = []
busylist = []
loglock = threading.Lock()

logfilu = open("OCCP-SERVER-LOG.txt", "w")
logfilu.write("")
logfilu.close()

file_reader(clientlist)

#print(clientlist)
#print(onlinelist)

while True:
    try:
        serversock.listen(4)
        (conn, (ip, port)) = serversock.accept()
        newthread = ClientHandlerThread(conn, ip, port)
        newthread.start()
        threadlist.append(newthread)
    except KeyboardInterrupt:
        if threadlist.len() == 0:
            file_writer(clientlist)
        exit()
