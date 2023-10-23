from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from scapy.all import IP, UDP, sr1
import threading
import sys
import pprint

""" Shell Command Traceroute Implementation """


# def traceroute(destination, max_hops=30):
#     command = f"traceroute -m {max_hops} -n {destination}"
#     output = subprocess.check_output(
#         command, shell=True, universal_newlines=True)
#     hops = [hop.split(' ')[3] for hop in output.strip().split('\n')[1:]]
#     print(hops)

""" Scapy Traceroute Implementation """


def traceroute(destination, max_hops=30, dst_port=33434):
    output = []
    for ttl in range(1, max_hops + 1):
        packet = IP(dst=destination, ttl=ttl) / UDP(dport=dst_port)
        reply = sr1(packet, verbose=0, timeout=1)

        # if reply is None:
        #     # print(f"{ttl}: *")
        #     pass

        if reply is not None:
            # print(f"{ttl}: {reply.src}")
            output.append(reply.src)

        if reply is not None and reply.src == destination:
            print(f"Reached destination: {destination}")
            return output

    print(f"Destination unreachable within {max_hops} hops: {destination}") 
    return output

def ip_is_valid(ip):
    return ip.startswith(("10.", "138.238."))

def increase_ip(ip, dif, increments=1):
    # Increment IP Address by dif

    ip = [int(x) for x in ip.split('.')]

    ip_total = ip[3] + ip[2] * 255 + ip[1] * (255 ** 2)

    for i in range(increments):
        ip_total += dif


    ip[2] = ip_total // 256
    ip[1] = ip[2] // 256
    ip[3] = ip_total % 256

    new_ip = [str(x) for x in ip]

    new_ip = '.'.join(new_ip)
        
    return new_ip

def multi_traceroute(first_destination, max_hops, count, nodes):

    ip = first_destination

    for i in range(count):
        # print(ip)
        output = traceroute(ip, max_hops)
        # print(output)

        for i, node in enumerate(output):

            node_id = nodes.find_one({"ip": node})
            if node_id is not None:
                # print(f"Node already exists in database: {node}")

                filter = {"ip": node}

                new_links = set()

                if i != 0 and ip_is_valid(output[i-1]):
                    new_links.add(output[i-1])

                if i != len(output) - 1 and ip_is_valid(output[i+1]):
                    new_links.add(output[i+1])

                update_data = {
                    "$addToSet": {
                        "links": {
                            "$each": list(new_links)
                        }
                    }
                }

                # print(f"Updating entry")
                nodes.update_one(filter, update_data)

            elif ip_is_valid(node):

                ip_node = {
                    "ip": node,
                    "links": set(),
                }

                if i != 0 and ip_is_valid(output[i-1]):
                    ip_node["links"].add(output[i-1])

                if i != len(output) - 1 and ip_is_valid(output[i+1]):
                    ip_node["links"].add(output[i+1])

                ip_node["links"] = list(ip_node["links"])

                node_id = nodes.insert_one(ip_node).inserted_id
        


        # Increment IP Address
        ip = increase_ip(ip, 8)


def mongo_client():
    """ Set Up MongoDB Client """

    db_username = "canicolas"
    db_password = "BlRvmec6R0JzqXM3"
    uri = f"mongodb+srv://{db_username}:{db_password}@cluster0.8gcptj9.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client


if __name__ == '__main__':

    # if len(sys.argv) != 3:
    #     print("Usage: python udp_traceroute.py <destination>")
    #     sys.exit(1)

    destination = sys.argv[1]
    # max_hops = int(sys.argv[2])
    # count = int(sys.argv[3])

    client = mongo_client()
    db = client.IP_Database
    nodes = db.IP_Nodes

    # Create a list to hold the thread objects
    threads = []

    # Define the number of threads you want to create
    num_threads = 200

    # Create and start the threads
    first_destination = destination

    for i in range(num_threads):
        thread = threading.Thread(target=multi_traceroute, args=(first_destination, 13, 10, nodes))
        threads.append(thread)
        thread.start()
        print(f"Starting thread from: {first_destination}")

        first_destination = increase_ip(ip=first_destination, dif=8, increments=10)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All threads have finished")

    # thread1 = threading.Thread(target=multi_traceroute, args=("10.0.0.0", 10, 10, nodes))
    # threads.append(thread1)
    # thread1.start()

    # thread2 = threading.Thread(target=multi_traceroute, args=("10.0.0.80", 10, 10, nodes))
    # threads.append(thread2)
    # thread2.start()

    # thread3 = threading.Thread(target=multi_traceroute, args=("10.0.0.160", 10, 10, nodes))
    # threads.append(thread3)
    # thread3.start()

    # thread4 = threading.Thread(target=multi_traceroute, args=("10.0.0.240", 10, 10, nodes))
    # threads.append(thread4)
    # thread4.start()

    # thread5 = threading.Thread(target=multi_traceroute, args=("10.0.1.70", 10, 10, nodes))
    # threads.append(thread5)
    # thread5.start()

    # thread6 = threading.Thread(target=multi_traceroute, args=("8.8.8.8", 10, 10, nodes))
    # threads.append(thread6)
    # thread6.start()

    # thread7 = threading.Thread(target=multi_traceroute, args=("8.8.8.8", 10, 10, nodes))
    # threads.append(thread7)
    # thread7.start()

    # thread8 = threading.Thread(target=multi_traceroute, args=("8.8.8.8", 10, 10, nodes))
    # threads.append(thread8)
    # thread8.start()

    # thread9 = threading.Thread(target=multi_traceroute, args=("8.8.8.8", 10, 10, nodes))
    # threads.append(thread9)
    # thread9.start()

    # thread0 = threading.Thread(target=multi_traceroute, args=("8.8.8.8", 10, 10, nodes))
    # threads.append(thread0)
    # thread0.start()

