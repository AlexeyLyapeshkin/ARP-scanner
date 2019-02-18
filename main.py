import socket
from getmac import get_mac_address
from multiping import MultiPing

# Alexey Lyapeshkin 2018 (c)
usage = 'Usage: python main.py submask'


def padding(something):
    """
    Required to complement the binary representation of a byte up to 8 characters.
    :param something:
    :return: a string that contains the required number of characters.
    """
    if len(something) >= 8:
        return something
    else:
        return '0' * (8 - len(something)) + something


def get_int(string):
    """
    Gets the numerical value of an IP address from a string representation.
    :param string:
    :return: int ['192.168.0.255' -> 3232235775]
    """
    not_bin = string.split('.')
    mask = ''
    for byte in not_bin:
        mask += padding(bin(int(byte))[2:])
    return int(mask, 2)


def get_str(integer):
    """
    Gets the string value of an IP address from a numerical representation.
    :param integer:
    :return: string [3232235775 -> '192.168.0.255']
    """
    integer = bin(integer)[2:]
    if len(integer) < 32:
        integer = '0' * (32 - len(integer)) + integer
    list_ = []
    string = ''
    for i in range(32):
        if i % 8 != 0:
            if i != 0:
                string += integer[i]
        elif i == 0:
            string += integer[i]
        elif i % 8 == 0:
            list_.append(str(int(string, 2)))
            string = ''
            string += integer[i]
    else:
        list_.append(str(int(string, 2)))

    return '.'.join(list_)


def _main(args):
    """
    Output devices on the local network with their MAC, IP and Name.
    :param args:
    :return: сonsole output.
    """
    # PREPARATION
    my_ip = socket.gethostbyname(socket.getfqdn())  # MY IP
    my_mac = get_mac_address(ip=my_ip)

    # MAIN
    print('{0:^19}|{1:^20}'.format('My IP: ','My MAC-adress: '))
    print('-'*40)
    print('{0:^18} - {1:^20}'.format(my_ip, my_mac))
    print('-'*40)
    if not args:
        print(usage)
    else:
        submask = args[0]
        my_ip = get_int(my_ip)
        submask = get_int(submask)
        broadcast = my_ip | (4294967295 ^ submask)

        print('Broadcast adress: {0}'.format(get_str(broadcast)))
        adr = my_ip & submask

        ips = [get_str(x) for x in range(adr, broadcast)]

        mp = MultiPing(ips)
        mp.send()
        responses, no_responses = mp.receive(0.5)
        main_list_motherfucker = list(responses.keys())  # local ips

        # OUTPUT

        print('_' * 56)
        print('{0:^18}|{1:^20}|{2:^15}'.format('IP', 'MAC', 'NAME'))
        print('¯' * 56)
        for ip in main_list_motherfucker:
            mac = get_mac_address(ip=ip)
            host = socket.gethostbyaddr(ip)[0]
            if host == ip:
                print('{0:^18}|{1:^20}|{2:40}'.format(ip, mac, 'Can\'t get name'))
            else:
                print('{0:^18}|{1:^20}|{2:40}'.format(ip, mac, host))


if __name__ == '__main__':
    import sys

    list_of_args = sys.argv[1:]
    _main(list_of_args)
