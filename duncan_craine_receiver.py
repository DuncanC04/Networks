#Duncan Craine
#PA4 Receiver
#3-5-26

#Packages
import socket
import sys
import random
import struct

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 duncan_craine_receiver.py <listen_port> <output_filename> <loss_probability>")
        return

    listen_port = int(sys.argv[1])
    output_filename = sys.argv[2]
    loss_probability = float(sys.argv[3])
    limit = 1024 
    expected_seq = 0
    buffer = {}

    #Create UDP socket and bind to port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", listen_port))

    print(f"Receiver listening on port {listen_port} with loss probability {loss_probability}")

    # outer try handles keyboard interrupts during socket operations or file handling
    try:
        with open(output_filename, "wb") as f: #Open output file for writing binary data
            while True:
                packet, addr = sock.recvfrom(limit)

                #Simulation loss
                if random.random() < loss_probability:
                    continue

                #Unpack Header: 4 for seq, 2 for length
                header = packet[:6]
                seq, length = struct.unpack("!IH", header) 
                payload = packet[6:6+length]

                if seq >= expected_seq:
                    buffer[seq] = payload

                while expected_seq in buffer:
                    f.write(buffer[expected_seq]) #Write the payload to the file
                    f.flush() #Ensure data is written to disk
                    del buffer[expected_seq] #Remove from buffer after writing
                    expected_seq += 1

                ack_packet = struct.pack("!I", expected_seq) #ACK the next expected sequence number
                sock.sendto(ack_packet, addr) #Send ACK back to sender

    except KeyboardInterrupt:
        print("\nReceiver shutting down.")

if __name__ == "__main__":
    main()