import subprocess
import re
import random
import secrets
import time
from tabulate import tabulate
from pyfiglet import Figlet

f = Figlet(font='big')
print('\n' + f.renderText('MacSwapPy'))

interfaces = subprocess.run(['networksetup', '-listallhardwareports'], stdout=subprocess.PIPE)
interfaces = interfaces.stdout.decode('utf-8').split('\n')
iface = interfaces[interfaces.index('Hardware Port: Wi-Fi') + 1].split(': ')[1]
realmac = interfaces[interfaces.index('Hardware Port: Wi-Fi') + 2].split(': ')[1]

currentmac = subprocess.run(['ifconfig', iface], stdout=subprocess.PIPE)
currentmac = currentmac.stdout.decode('utf-8').replace('\t', ' ').split(' ')
currentmac = currentmac[currentmac.index('ether') + 1]

print('True MAC address:', realmac)
print('Current MAC address:', currentmac, '\n')

print(tabulate([[1, 'Bypass login'], [2, 'Bypass restriction'], [3, 'Random'], [4, 'Custom'], [5, 'Reset']], headers=['Number', 'Option']))
option = int(input('\nSelect an option: '))

if option in [1, 2]:
    status = subprocess.run(['ifconfig', iface], stdout=subprocess.PIPE)
    status = status.stdout.decode('utf-8').replace('\t', ' ').split(' ')
    status = status[status.index('status:') + 1].split('\n')[0]
    if status == 'active':
        list = subprocess.run(['arp', '-ani', iface], stdout=subprocess.PIPE)
        list = list.stdout.decode('utf-8')
        list = re.findall('(?:[0-9a-fA-F]:?){12}', list)
        if 'ff:ff:ff:ff:ff:ff' in list: list.remove('ff:ff:ff:ff:ff:ff')
        list.remove(currentmac)
        if list:
            newmac = random.choice(list)

            if option == 2:
                newmac = newmac[:-2] + secrets.token_hex(1)
        else:
            print('No results, wait 30 seconds before trying again')
    else:
        print('Connect to a newtork first, then try again')

if option == 3:
    rand = secrets.token_hex(6)
    rand = iter(rand)
    newmac = ':'.join(a+b for a, b in zip(rand, rand))

if option == 4:
    newmac = input('\nInput a MAC address: ')

if option == 5:
    newmac = realmac

if re.search('(?:[0-9a-fA-F]:?){12}', newmac):
    print('\nChanging MAC address to:', newmac)

    subprocess.run(['sudo', 'ifconfig', iface, 'ether', newmac], stdout=subprocess.PIPE)
    time.sleep(0.5)
    subprocess.run(['sudo', 'ifconfig', iface, 'down'], stdout=subprocess.PIPE)
    time.sleep(1)
    subprocess.run(['sudo', 'ifconfig', iface, 'up'], stdout=subprocess.PIPE)

    print('\nSuccessfully changed MAC address')
else:
    print('\nInvalid format, try again')
