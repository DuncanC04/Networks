#Duncan Craine
#PA3 HTTP Server
#2-24-26

#Sources
#https://docs.python.org/3/library/socket.html
#https://docs.python.org/3/library/threading.html
#PA2

#Packages
import socket
import threading
import sys

limit = 1024  #Limit for message length

def send404(conn):
    body = b"<html><body><h1>404 Not Found</h1></body></html>"
    response = (
        "HTTP/1.1 404 Not Found\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + body
    conn.sendall(response)

def send400(conn):
    body = b"<html><body><h1>400 Bad Request</h1></body></html>"
    response = (
        "HTTP/1.1 400 Bad Request\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + body
    conn.sendall(response)

def manage_client(conn): #Handle one browser connection
    buffer = b"" 
    #Until end of HTTP headers
    while b"\r\n\r\n" not in buffer:
        data = conn.recv(limit) #Receive data from client
        if not data: 
            conn.close()
            return
        buffer += data 

    try: #Parse HTTP request
        request_line = buffer.split(b"\r\n")[0].decode()
        parts = request_line.split() 
        method = parts[0] #GET
        path = parts[1] #/index.html or /internet.jpg
    except:
        send400(conn)
        conn.close()
        return

    if method != "GET": #Only support GET method
        send400(conn)
        conn.close()
        return

    if path == "/index.html" or path == "/":
        filename = "index.html"
        content_type = "text/html; charset=utf-8"
        with open(filename, "r", encoding="utf-8") as f:
            body = f.read().encode()

    elif path == "/internet.jpg":
        filename = "internet.jpg"
        content_type = "image/jpeg"
        with open(filename, "rb") as f:
            body = f.read()

    else:
        send404(conn)
        conn.close()
        return

    #HTTP response
    header = (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()

    conn.sendall(header + body) #Send header and body together
    conn.close() #Close connection after sending response

def main():
    if len(sys.argv) != 2: #Check for correct number of arguments
        print("Usage: python duncan_craine_pa3.py <port>")
        sys.exit(1) #Exit

    port = int(sys.argv[1]) #Get port from command line
    print(f"Server on port {port}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Helps reuse of address
    server.bind(("localhost", port))  #Bind socket to port
    server.listen() #Start listening for incoming connections

    while True: 
        conn, addr = server.accept() #Accept incoming connection
        threading.Thread(target=manage_client, args=(conn,), daemon=True).start() #Start thread

if __name__ == "__main__":
    main()
