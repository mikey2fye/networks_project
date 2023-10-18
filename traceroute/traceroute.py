from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from scapy.all import IP, UDP, sr1
import dns
import json
import sys
import subprocess

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


# Example hop
hop = {
    'ip': '192.168.1.1',
    'links': {'172.26.80.1', '71.178.216.1'}
}


def multi_traceroute(first_destination, max_hops, count):

    ip = first_destination
    for i in range(count):
        print(ip)
        output = traceroute(ip, max_hops)
        print(output)

        for i in range(len(output)):
            node = output[i]

            print(f"Serializing {node}")

            if node.startswith("10."):
                ip_node = {
                    "ip": node,
                    "links": set(),
                }

                if i != 0 and output[i-1].startswith("10."):
                    ip_node["links"].add(output[i-1])

                if i != len(output) - 1 and output[i+1].startswith("10."):
                    ip_node["links"].add(output[i+1])

                ip_node["links"] = list(ip_node["links"])

                with open('database.json', 'r') as file:
                    data = json.load(file)

                data["ip_nodes"].append(ip_node)

                with open('database.json', 'w') as file:
                    json.dump(data, file, indent=4)

        ip_split = [int(x) for x in ip.split('.')]

        ip_split[3] += 1

        if ip_split[3] == 256:
            ip_split[3] = 0
            ip_split[2] += 1

        if ip_split[2] == 256:
            ip_split[2] = 0
            ip_split[1] += 1

        ip_split = [str(x) for x in ip_split]

        ip = '.'.join(ip_split)


if __name__ == '__main__':
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

    # if len(sys.argv) != 3:
    #     print("Usage: python udp_traceroute.py <destination>")
    #     sys.exit(1)

    destination = sys.argv[1]
    # max_hops = int(sys.argv[2])
    # count = int(sys.argv[3])
    # traceroute(destination, max_hops)

    multi_traceroute(destination, 8, 1)
