import fcntl
import netifaces as ni
import socket
import struct
import subprocess as sb
from multiping import MultiPing


def getHwAddr(ifname):
    """
    Getting MAC-adress
    :param ifname:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,
                       struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])


def padding(something):
    """
    Required to complement the binary representation of a
    byte up to 8 characters.
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


def parse_string(string):
    index_1 = string.find('(')
    index_2 = string.rfind(')')
    name = string[:index_1 - 1]
    ip = string[index_1 + 1:index_2]
    mac = string[index_2 + 4:index_2 + 4 + 17]
    index_3 = string.rfind(']')
    interface = string[index_3 + 5:]
    return name, ip, mac, interface


def main(list_of_args):
    """
      Output devices on the local network with their MAC, IP and Name.
      :param list_of_args:
      :param args:
      :return: сonsole output.
    """

    main_dict = {'interface': [], 'ip': [], 'mac': []}

    interfaces = ni.interfaces()  # List of interfaces
    # Generate Header
    print('{0:-^63}'.format('-'))
    print('{0: ^20}|{1: ^20}|{2: ^20}|'.format('Interface', 'IP', 'MAC'))
    print('{0:-^63}'.format('-'))

    for interface in interfaces[:-1]:
        # getting MAC of interface
        mac = getHwAddr(interface)

        # getting ip of interface
        ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']

        print('{0: ^20}|{1: ^20}|{2: ^20}'.format(interface, ip, mac))

        main_dict['interface'].append(interface)
        main_dict['ip'].append(ip)
        main_dict['mac'].append(mac)

    print('{0:-^84}'.format('-'))

    submask = get_int(list_of_args[0])
    ip = list_of_args[1]
    log_file = open('log.txt', 'w')
    sb.run(["nmap", "{0}/{1}".format(ip, (bin(submask)[2:]).count('1'))],
           shell=False, stdout=log_file)

    list_of_devices = sb.Popen('arp -a', shell=True, stdout=sb.PIPE).stdout.read().decode('utf-8').split('\n')
    list_of_devices = [item for item in list_of_devices if item.find('не завершено') == -1 and item != '']

    print('{0: ^20}|{1: ^20}|{2: ^20}|{3: ^20}|'.format('Name', 'IP', 'MAC', 'Interface'))
    print('{0:-^84}'.format('-'))

    for string in list_of_devices:
        print('{0: ^20}|{1: ^20}|{2: ^20}|{3: ^20}|'.format(*parse_string(string)))

    print('{0:-^84}'.format('-'))


if __name__ == '__main__':
    import sys, re

    usage = '\npython3 main.py SUBMASK IP-ADDRESS\n'

    list_of_args = sys.argv[1:]

    if len(list_of_args) != 0:
        if re.match(
                r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
                list_of_args[1]):

            if 0 <= get_int(list_of_args[0]) <= 4294967295:
                main(list_of_args)
            else:
                print(usage)
        else:
            print(usage)
    else:
        print(usage)
