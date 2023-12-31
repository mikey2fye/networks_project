file_name = "ip_addresses.txt"

with open(file_name, 'w') as file:
    # Write each IP address to the file, one per line
    ip = "10.0.0.0"
    while ip != "10.255.255.255":
        file.write(ip + '\n')

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
