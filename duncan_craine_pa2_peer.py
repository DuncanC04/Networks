#Duncan Craine
#PA2 P2P
#2-12-26

#Sources
#https://www.w3schools.com/python/ref_module_socket.asp
#https://www.w3schools.com/python/ref_module_threading.asp
#https://www.geeksforgeeks.org/python/socket-programming-multi-threading-python/
#https://docs.python.org/3/howto/sockets.html


#Packages
import socket
import threading
import sys

limit = 1024 #Limit for message length
peers = []

def recv_loop(sock): #Receive messages from a peer
    buffer = b""
    while True:
        try:
            data = sock.recv(limit) #Receive data from the peer
            if not data:
                break
            buffer += data #Add received data to buffer
            while b"\n" in buffer: #While there is a complete message in the buffer
                line, buffer = buffer.split(b"\n", 1) #Split the buffer into a complete message and the remaining buffer
                print(line.decode())
        except:
            break

    if sock in peers: #Remove peer from peers list if connection is closed
        peers.remove(sock)
    sock.close()

def broadcast(msg): #Broadcast a message to all peers
    for peer in peers:
        peer.send(msg)

def listen_loop(port): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port)) #Bind socket to port
    s.listen()

    while True:
        peer, _ = s.accept() #Accept incoming connection
        peers.append(peer)
        threading.Thread(target=recv_loop, args=(peer,), daemon=True).start() #Start thread to receive messages from the new peer

def connect_peer(host, port): #Connect to a new peer
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        peers.append(s)
        threading.Thread(target=recv_loop, args=(s,), daemon=True).start()
    except:
        print("Could not connect to", host, port)

def send_loop(username): #Send messages to peers
    while True:
        try:
            msg = input()
        except:
            break
        line = "[" + username + "]: " + msg + "\n" #[jim]: hi there
        broadcast(line.encode())

def main():
    if len(sys.argv) < 3: #Check for correct number of arguments
        print("Usage: python3 duncan_craine_pa2_peer.py <username> <port> [host:port ...]")
        return

    username = sys.argv[1]
    port = int(sys.argv[2])

    threading.Thread(target=listen_loop, args=(port,), daemon=True).start() #Start thread

    for arg in sys.argv[3:]:
        if ":" in arg:
            host, port = arg.split(":") #
            connect_peer(host, int(port))

    send_loop(username)

main()
