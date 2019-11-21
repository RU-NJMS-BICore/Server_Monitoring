import requests, psutil, paramiko, time
import serverslist
import standard_linux, amarel

servers=serverslist.servers
target=serverslist.target

if __name__=='__main__':
    while True:
        for name, ins in servers.items():
            if str(name) != 'Amarel':
                try:
                    output=standard_linux.commands(name, ins[0],ins[1],ins[2], target)
                    print(output)
                except Exception as e:
                    print(e)
            elif str(name) == 'Amarel':
                output=amarel.commands(name, ins[0],ins[1],ins[2], target)
                print(output)
            else:
                print('Theres a new server in town')

        time.sleep(300)
