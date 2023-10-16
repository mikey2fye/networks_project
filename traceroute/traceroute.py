from scapy.all import IP, UDP, sr1
import sys
import subprocess

""" Shell Command Traceroute Implementation """


def traceroute(destination):
    command = f"traceroute -n {destination}"
    output = subprocess.check_output(
        command, shell=True, universal_newlines=True)
    hops = [hop.split(' ')[3] for hop in output.strip().split('\n')[1:]]
    print(hops)


# Example hop
hop = {
    'ip': '192.168.1.1',
    'links': ['172.26.80.1', '71.178.216.1']
}

""" Scapy Traceroute Implementation """


# def traceroute(destination, max_hops=30, dst_port=33434):
#     for ttl in range(1, max_hops + 1):
#         packet = IP(dst=destination, ttl=ttl) / UDP(dport=dst_port)
#         reply = sr1(packet, verbose=0, timeout=1)

#         if reply is None:
#             print(f"{ttl}: *")
#         else:
#             print(f"{ttl}: {reply.src}")

#         if reply is not None and reply.src == destination:
#             print(f"Reached destination: {destination}")
#             break


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python udp_traceroute.py <destination>")
        sys.exit(1)

    destination = sys.argv[1]
    traceroute(destination)
