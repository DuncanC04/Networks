#Duncan Craine
#PA2 Client
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

def recv(sock): #Receive messages from the server
    buffer = b"" #Buffer to hold incoming data
    while True: #While connection is open
        try:
            data = sock.recv(limit) #Receive data from the server
            if not data: #If no data is received, the connection is closed
                break
            buffer += data #Add received data to buffer
            while b"\n" in buffer: #While there is a complete message in the buffer
                line, buffer = buffer.split(b"\n", 1) #Split the buffer into a complete message and the remaining buffer
                print(line.decode(), flush=True) #Print the complete message and flush the output
        except:
            break

def send(sock, username): #Send messages to the server
    while True: 
        msg = input() 
        full = f"{username}: {msg}\n" #[jim]: hi there
        try:
            sock.sendall(full.encode()) #Send the message to the server
        except:
            break

def main():
    if len(sys.argv) != 4: #Check for correct number of arguments
        print("Usage: python duncan_craine_pa2_client.py <host> <port> <username>")
        sys.exit(1) #Exit

    host = sys.argv[1] #Get host from command line
    port = int(sys.argv[2]) #Get port from command line
    username = sys.argv[3] #Get username from command line
    print(f"Connected to server on port {port}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create socket
    sock.connect((host, port)) 
    threading.Thread(target=recv, args=(sock,), daemon=True).start() #Start thread to receive messages
    send(sock, username)

if __name__ == "__main__":
    main()
