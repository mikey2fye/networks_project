from concurrent.futures import ThreadPoolExecutor
from scapy.all import IP, UDP, sr1
from tqdm import tqdm
import sys
import mongo

# Check if IP address is within a valid address space
def ip_is_valid(ip):
    return ip.startswith(("10.", "138.238.", "66."))

# Increment IP address
def increase_ip(ip, dif=1, increments=1):
    # Increment IP Address by dif

    ip = [int(x) for x in ip.split('.')]

    for i in range(increments):
        ip[3] += dif

        if ip[3] >= 256:
            ip[2] += 1
            ip[3] = ip[3] % 256
        
        if ip[2] == 256:
            ip[1] += 1
            ip[2] = 0

        if ip[1] == 256:
            ip[0] += 1
            ip[1] = 0

    ip = [str(x) for x in ip]

    ip = '.'.join(ip)
        
    return ip

# Get count of ip address to run traceroute to
def get_address_count(start, end, step=1):

    start_total = [int(x) for x in start.split('.')]
    end_total =  [int(x) for x in end.split('.')]

    start_total = start[3] + start[2] * 255 + start[1] * (255 ** 2) + start[0] * (255 ** 3)
    end_total = end[3] + end[2] * 255 + end[1] * (255 ** 2) + end[0] * (255 ** 3)

    if start_total > end_total:
        print("Invalid Address Range")
        exit()

    count = 1
    address = start

    while address != end:
        address = increase_ip(address)
        count += 1

    return count // step

# Scapy Traceroute implementation using UDP protocal
def traceroute(destination, max_hops=30, dst_port=33434):
    output = []
    for ttl in range(1, max_hops + 1):
        packet = IP(dst=destination, ttl=ttl) / UDP(dport=dst_port)
        reply = sr1(packet, verbose=0, timeout=1)

        if reply is not None:
            output.append(reply.src)

            if reply.src == destination:
                # print(f"Reached destination: {destination}")
                return output
        
    return output

# Run traceroutes to a specified range of IP addresses
def multi_traceroute(first_address, max_hops, count, nodes, step=8):

    ip = first_address

    for i in tqdm(range(count), desc=f"{first_address}", unit="traceroute", bar_format="{l_bar}\033[34m{bar}\033[0m|{n_fmt}/{total}"):
        output = traceroute(ip, max_hops)

        for i, ip in enumerate(output):

            if ip_is_valid(ip):

                ip_node = {
                    "ip": ip,
                    "links" : set()
                }

                if i != 0 and ip_is_valid(output[i-1]):
                    ip_node["links"].add(output[i-1])

                if i != len(output) - 1 and ip_is_valid(output[i+1]):
                    ip_node["links"].add(output[i+1])
                
                ip_node["links"] = list(ip_node["links"])

                mongo.create_or_update_node(ip_node, node_collection=nodes)

        
        # Increment IP Address
        ip = increase_ip(ip, step)

def get_thread_distribution(num_threads, address_count):
    return address_count // num_threads

def exec(start, end, step=8, ttl=10, thread_count=1600):

    client = mongo.mongo_client()
    db = client.IP_Database
    node_collection = db.IP_Nodes

    # Define the number of threads you want to create
    num_threads = thread_count

    # Create and start the threads
    first_address = start
    last_address = end

    # Calculation number of traceroutes per thread
    address_count = get_address_count(start=first_address, end=last_address, step=step)
    thread_distribution = get_thread_distribution(num_threads, address_count)
    print(f"{thread_distribution} traceroutes per thread")

    max_threads = 40  # Adjust as needed
    with ThreadPoolExecutor(max_threads) as executor:
        # Create a list to hold the thread objects
        threads = []

        for i in tqdm(range(num_threads), desc="Initializing threads", unit="thread", bar_format="{l_bar}\033[32m{bar}\033[0m|{n_fmt}/{total}"):

            thread = executor.submit(multi_traceroute, first_address, ttl, thread_distribution, node_collection)
            threads.append(thread)
            # print(f"Starting thread from: {first_address}")

            first_address = increase_ip(ip=first_address, dif=8, increments=thread_distribution)

        # Wait for all threads to complete
        for thread in threads:
            thread.result()


    print("All threads have finished")

    client.close()



if __name__ == '__main__':
    exec()