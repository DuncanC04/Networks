#Duncan Craine
#2-5-26
#Networks Programming Assignment 1
def networkSim(payload_bytes):
    fileSize = 5 * 2**20 #bytes
    headerSize = 100 #bytes
    packet_size_bits = (payload_bytes + headerSize) * 8 #bits

    path = [(10, 10), (5, 20), (20, 5)] #(bandwidth in Mbps, propagation in ms)

    #Part A
    #Packetization + basic delays
    num_packets = (fileSize + payload_bytes - 1) // payload_bytes


    #Transmission delay per link
    transmission_delays = []
    for link in path:
        bandwidth = link[0] * 10**6 #bits per second
        total_delay = packet_size_bits / bandwidth #seconds
        transmission_delays.append(total_delay)

    #Propagation delay per link
    propagation_delays = []
    for link in path:
        latency = link[1] / 1000 #seconds
        propagation_delays.append(latency)


    #Part B
    #First packet end-to-end delay (store-and-forward)
    first_packet_arrival_s = 0
    for link in path:
        bandwidth = link[0] * 10**6 #bits per second
        prop_delay = link[1] / 1000 #seconds
        first_packet_arrival_s += ((packet_size_bits / bandwidth) + prop_delay) #seconds

    #Part C
    #Full file arrival time (pipelined)
    bottleneck_delay = max(transmission_delays)
    file_arrival_s = first_packet_arrival_s + ((num_packets - 1) * bottleneck_delay) #seconds
    

    #Part D
    #Throughput + link utilization
    throughput_mbps = (fileSize * 8) / file_arrival_s / 10**6 #Mbps
    utilization = []
    for link in path:
        utilization.append(throughput_mbps/link[0]) #Ui = throughput / Ri

    
    #Output
    print(f"Payload Size: {payload_bytes} bytes, Number of Packets: {num_packets} packets, Packet size: {packet_size_bits} bits.")
    print(f"First Packet Arrival Time: {first_packet_arrival_s:.4f} seconds, File Arrival Time: {file_arrival_s:.4f} seconds.")
    print(f"Throughput: {throughput_mbps:.2f} Mbps, Bottleneck Bandwidth: {bottleneck_delay} Mbps")
    print(f"Link Utilization: {utilization[0]:.4f}, {utilization[1]:.4f}, {utilization[2]:.4f}")

#Part E
#Packet size tradeoff study
def main():
    payloadSizes = [700, 1400, 2800] #bytes
    for payload_bytes in payloadSizes:
        networkSim(payload_bytes)
        print()

if __name__ == "__main__":
    main()