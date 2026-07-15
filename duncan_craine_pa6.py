#!/usr/bin/env python3
"""COM315ARENA client.

Usage: python3 duncan_craine_pa6.py <host> <port> <name>

Does the server respond to commands that weren't in the PA5 documentation?
It responds with Error: Bad arguments for everything I tried.

Is there information the server has that it isn't giving you? Can you ask for it?
The server has the full map and player positions, but it doesn't give you that information. 
It only gives you your own position and the map size.

How does the server know who you are? Can you mess with that?
The scoring json file is by player name, but it is server controlled besides sending the name in the JOIN command.

Can you connect more than once at the same time?
Yes I can connect many times with same or different names, just using different terminals.

What do ERROR responses tell you about what the server expected?
I was only able to get "Error: Bad arguments" responses.
The server checks for the number of arguments, empty arguments, and invalid commands.

There may have been hidden commands or more clever ways to win the game,
but I came up with a simple strategy of just connecting 10 dummy enemies to the server to create more point scoring opportunities for myself.
By not giving them gamestate, they will just stay idle and be easy targets for me to kill, giving me points. I suppose if others are also playing it,
they could also kill the dummy enemies, but they will only be on the server when I am playing.
"""



import json
import socket
import sys
import threading
import time

from strategy import decide

#Simple dummy enemy class
class DummyEnemy:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        
    def connect_and_idle(self): #Connect to the server and do nothing, just stay idle
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.sendall(f"JOIN {self.name}\n".encode())
            
            while True:
                time.sleep(1) #Just keep connection alive, don't send anything
                
        except:
            pass

num_dummies = 10
def start_dummy_enemies(host, port, base_name):
    for i in range(num_dummies):
        enemy = DummyEnemy(f"{base_name}Enemy{i}", host, port) #Create a dummy enemy with a unique name based on the base name
        threading.Thread(target=enemy.connect_and_idle, daemon=True).start() #Start a thread for each dummy enemy to connect and stay idle


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <host> <port> <name>")
        sys.exit(1)

    host, port, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create TCP socket
    sock.connect((host, port)) #Connect to the server at the specified host and port
    sock.sendall(f"JOIN {name}\n".encode()) #Send the JOIN command with the player's name, encoded as bytes

    buffer = ""
    while "\n" not in buffer: #Wait for the welcome message, which ends with a newline
        data = sock.recv(4096) #Receive welcome
        if not data: #If the connection is closed before we receive a welcome message, exit with an error
            sock.close()
            sys.exit(1)
        buffer += data.decode("utf-8") #Append the received data to the buffer, decoding it from bytes to a string
        

    welcome, buffer = buffer.split("\n", 1) #Split at the first newline to get the welcome message
    welcome = welcome.rstrip("\r") #Remove any carriage return characters from the welcome message
    if not welcome.startswith("WELCOME "): #Check if the welcome message is in the expected format
        print(f"Error with welcome message: {welcome}")
        sock.close()
        sys.exit(1)


    try:
        json_str = welcome[8:] #Everything after "WELCOME "
        welcome = json.loads(json_str) #Get player ID, initial position, map size, and walls from JSON
        player_id = welcome["id"]
        print(f"Joined as player {player_id} at {welcome['pos']}") #Print initial position and player ID
        print(f"Map size: {welcome['map']}, Walls: {len(welcome['walls'])} walls") #Print map size and number of walls
    
    except Exception as e:
        print(f"Error in parsing JSON: {e}")
        sys.exit(1)

    # Start dummy enemies
    start_dummy_enemies(host, port, name)
    print("Started 10 dummy enemies")

    while True:
        try:
            data = sock.recv(4096) #Receive game data from the server
            if not data: #If the connection is closed, exit the loop
                print("Server closed connection")
                break
            buffer += data.decode('utf-8') #Append received data to the buffer

            while '\n' in buffer: #Process complete lines in the buffer
                line, buffer = buffer.split('\n', 1) #Split at the first newline to get a complete message
                line = line.rstrip('\r') #Removes extra
                if not line: #Ignore empty lines
                    continue

                #Handle different message types based on the prefix of the line
                #not sure if there is a better way to do this
                if line.startswith("GAMESTATE"):
                    handle_gamestate(line, sock)
                elif line.startswith("HIT"):
                    handle_hit(line)
                elif line.startswith("DEATH"):
                    handle_death(line)
                elif line.startswith("KILL"):
                    handle_kill(line)
                elif line.startswith("RESPAWN"):
                    handle_respawn(line)
                elif line.startswith("CHAT"):
                    handle_chat(line)
                elif line.startswith("ERROR"):
                    handle_error(line)
                else:
                    print(f"Unknown message: {line}")

        except KeyboardInterrupt: #Allow the user to exit with Ctrl+C
            print("Interrupted by user")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    sock.close()
    print("Disconnected")
import time

def handle_gamestate(line, sock):
    try:
        

        # Extract JSON
        json_str = line[10:]
        game_state = json.loads(json_str)
        command = decide(game_state)
        if command:
            sock.sendall((command + "\n").encode())


        

    except Exception as e:
        print(f"Error with handle_gamestate: {e}")

def handle_hit(line):
    try:
        parts = line.split(" ", 2) #Split into max 3 parts: "HIT", damage, and optionally attacker
        damage = parts[1] #Second part is the damage taken
        attacker = parts[2] if len(parts) > 2 else "unknown" #Third part is the attacker, if it exists
        print(f"Hit: Took {damage} damage from {attacker}")
    except Exception as e:
        print(f"Error with handle_hit: {e}")


def handle_death(line):
    try:
        parts = line.split(" ", 1) #Split into max 2 parts: "DEATH" and optionally the killer
        killer = parts[1] if len(parts) > 1 else "unknown" #Second part is the killer, if it exists
        print(f"Death: Killed by {killer}")
    except Exception as e:
        print(f"Error with handle_death: {e}")


def handle_kill(line):
    try:
        parts = line.split(" ", 1) #Split into max 2 parts: "KILL" and optionally the victim
        victim = parts[1] if len(parts) > 1 else "unknown" #Second part is the victim, if it exists
        print(f"Kill: Eliminated {victim} (+50 points)")
    except Exception as e:
        print(f"Error with handle_kill: {e}")


def handle_respawn(line):
    try:
        parts = line.split(" ") #Split into parts: "RESPAWN", x, and y
        x, y = float(parts[1]), float(parts[2]) #Second and third parts are the new coordinates after respawn
        print(f"Respawn: Respawned at ({x}, {y})") 
    except Exception as e:
        print(f"Error with handle_respawn: {e}")


def handle_chat(line):
    try:
        parts = line.split(" ", 2) #Split into max 3 parts: "CHAT", sender, and message
        sender = parts[1] #Second part is the sender of the chat message
        message = parts[2] if len(parts) > 2 else "" #Third part is the message is it exists
        print(f"{sender}: {message}") #Print the chat message in the format "sender: message"
    except Exception as e:
        print(f"Error with handle_chat: {e}")


def handle_error(line):
    try:
        message = line[6:] if len(line) > 6 else "unknown error" #Everything after "ERROR " is the error message, if it exists
        print(f"Error: {message}")
    except Exception as e:
        print(f"Error with handle_error: {e}")

if __name__ == "__main__":
    main()