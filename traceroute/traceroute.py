from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from scapy.all import IP, UDP, sr1
import dns
import json
import sys
import subprocess
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
            break

    return output

def ip_is_valid(ip):
    return ip.startswith(("10.", "138.238."))

def multi_traceroute(first_destination, max_hops, count):

    client = mongo_client()
    db = client.IP_Database
    nodes = db.IP_Nodes

    ip = first_destination

    for i in range(count):
        print(ip)
        output = traceroute(ip, max_hops)
        print(output)

        for i, node in enumerate(output):

            node_id = nodes.find_one({"ip": ip_node["ip"]})
            if node_id is not None:
                filter = {"ip": node}

                new_links = {}

                if i != 0 and ip_is_valid(output[i-1]):
                    new_links.add(output[i-1])

                if i != len(output) - 1 and ip_is_valid(output[i+1]):
                    new_links.add(output[i+1])

                update_data = {
                    "$push": {
                        "links": {
                            "$each": list(new_links)
                        }
                    }
                }

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
        ip_split = [int(x) for x in ip.split('.')]

        ip_split[3] += 8

        if ip_split[3] >= 256:
            ip_split[3] = 0
            ip_split[2] += 1

        if ip_split[2] >= 256:
            ip_split[2] = 0
            ip_split[1] += 1

        ip_split = [str(x) for x in ip_split]

        ip = '.'.join(ip_split)


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
    # traceroute(destination, max_hops)

    multi_traceroute(destination, max_hops=30, count=1)

    # client = mongo_client()
    # db = client.IP_Database
    # nodes = db.IP_Nodes

    # node_id = '6535e158f47b5684832cb66a'
    # pprint.pprint(nodes.find_one({"ip": "172.26.80.1"}))
