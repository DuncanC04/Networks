#Duncan Craine
#PA4 Sender
#3-5-26

#Packages
import socket
import time
import sys
import struct

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 duncan_craine_sender.py <receiver_host> <receiver_port> <input_filename> <window_size>")
        return

    receiver_host = sys.argv[1]
    receiver_port = int(sys.argv[2])
    input_filename = sys.argv[3]
    window_size = int(sys.argv[4])
    timeout = 2 #Seconds
    segment_size = 1000 #Bytes

    #File into binary segments
    segments = []
    with open(input_filename, "rb") as f: #Open file in binary mode
        while True:
            chunk = f.read(segment_size) #Read segment_size bytes
            if not chunk: #End of the file
                break
            segments.append(chunk)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket
    sock.settimeout(timeout) #Set timeout for ACKs

    #Sliding Window
    base = 0
    next_seq = 0
    retransmissions = 0
    start_time = time.time() 

    while base < len(segments):
        while (next_seq < base + window_size) and (next_seq < len(segments)): #Send segments in the window
            payload = segments[next_seq]
            header = struct.pack("!IH", next_seq, len(payload))
            packet = header + payload
            sock.sendto(packet, (receiver_host, receiver_port))
            next_seq += 1

        try:
            ack_packet, _ = sock.recvfrom(4) #4 bytes for the sequence number
            ack_num = struct.unpack("!I", ack_packet)[0] #Get ACK number

            if ack_num > base: #Move the window forward if ACK is for a new segment
                base = ack_num

        except socket.timeout: #Retransmit all segments in the window if timeout occurs
            retransmissions += (next_seq - base)
            next_seq = base

    #Output stats
    end_time = time.time()
    total_time = end_time - start_time
    file_size = sum(len(s) for s in segments) #Calculate total file size in bytes
    if total_time > 0: #Prevent division by zero
        throughput = file_size / total_time
    else:
        throughput = 0

    print(f"Total Retransmissions: {retransmissions}")
    print(f"Total Transfer Time: {total_time:.2f} seconds")
    print(f"Effective Throughput: {throughput:.2f} bytes/sec")

if __name__ == "__main__":
    main()