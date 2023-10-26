import traceroute as tr
import argparse

def main():

    # Initialize a command line argument parser
    parser = argparse.ArgumentParser(description="Traceroute Topology Mapper")
    parser.add_argument('start', help='First target address of range')
    parser.add_argument('end', help='End of IP address range')
    parser.add_argument('--step', '-s', help='How many IPs to skip')
    parser.add_argument('--ttl', '-t', help='Time to Live (Max Hops)')

    # Parse arguments
    args = parser.parse_args()

    first_target = args.start
    final_target = args.end
    step = int(args.step if args.step is not None else 1)
    max_hops = int(args.ttl if args.ttl is not None else 10)

    tr.exec(start=first_target, end=final_target, step=step, ttl=max_hops)


if __name__ == "__main__":
    main()


