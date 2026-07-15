#Duncan Craine
#PA2 Server
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
clients = []
lock = threading.Lock() #Lock to synchronize access to clients list

def broadcast(msg, sender_socket): #Broadcast a message to all clients except the sender
    with lock: #Acquire lock to access clients list
        for client in clients: 
            if client != sender_socket: #Don't send the message back to the sender
                client.sendall(msg)
                

def manage_client(sock):
    buffer = b"" #Buffer to hold incoming data
    while True:
        try:
            data = sock.recv(limit) 
            if not data:
                break
            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1) #Split the buffer into a complete message and the remaining buffer
                broadcast(line + b"\n", sock) #Broadcast the complete message to all clients except the sender
        except:
            break

    with lock:
        if sock in clients:
            clients.remove(sock)
    sock.close()

def main():
    if len(sys.argv) != 2: #Check for correct number of arguments
        print("Usage: python3 duncan_craine_pa2_server.py <port>")
        sys.exit(1) #Exit

    port = int(sys.argv[1]) #Get port from command line

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create socket
    server_sock.bind(("", port)) #Bind socket to port
    server_sock.listen() #Start listening for incoming connections
    print(f"Listening on port {port}")

    while True:
        client_sock, addr = server_sock.accept() #Accept incoming connection
        with lock:
            clients.append(client_sock) #Add client socket to clients list
        threading.Thread(target=manage_client, args=(client_sock,), daemon=True).start() #Start thread to manage client

if __name__ == "__main__":
    main()
