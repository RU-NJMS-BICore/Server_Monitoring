import requests, psutil, paramiko, time

def fluxer(measurement, server, value, target):
    params = (
        ('db', 'school'),
        )
    
    data = '{},host={} value={}'.format(str(measurement),str(server),float(value))
    
    response = requests.post(target+'/write', params=params, data=data)
    return response

def fluxer2(measurement, server, process, value, target):
    params = (
        ('db', 'school'),
        )
    
    data = '{},host={},process={} {}'.format(str(measurement),str(server),str(process),str(value))
    
    response = requests.post(target+'/write', params=params, data=data)
    return response

def commands(server, ip, user, pw, target):
    client=paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user,password=pw)

    stdin, stdout, stderr=client.exec_command("echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')]")
    cpu=[]
    for item in stdout.readlines():
        cpu.append(item.strip('\n'))
    cpuout=str(cpu[0]).strip("'[]")

    stdin, stdout, stderr=client.exec_command("free | grep Mem | awk '{print $3,$2,$3*100/$2 }'")
    ram=[]
    for item in stdout.readlines():
        ram.append(item.strip('\n'))
    ram=str(ram).split(' ')
    ramout=[]
    for item in ram:
        ramout.append(item.strip("'[]"))#Used, Total, percent
    
    if str(server) != 'xdrive':
        stdin, stdout, stderr=client.exec_command("df -hBG --total -x cifs | awk 'END {print $2,$4,$5}'")
        disk=[]
        for item in stdout.readlines():
            disk.append(item.strip('\n'))
        disk=str(disk).split(' ')
        diskout=[]
        for item in disk:
            diskout.append(item.strip("G%'[]"))#total, remaining, percent
    else:
        stdin, stdout, stderr=client.exec_command("df -hBG --total | awk 'END {print $2,$4,$5}'")
        disk=[]
        for item in stdout.readlines():
            disk.append(item.strip('\n'))
        disk=str(disk).split(' ')
        diskout=[]
        for item in disk:
            diskout.append(item.strip("G%'[]"))#total, remaining, percent
    to_flux={'CPU_Usage':cpuout,
             'RAM_Used':ramout[0],
             'RAM_Total':ramout[1],
             'RAM_Percent':ramout[2],
             'Disk_Total':diskout[0],
             'Disk_Remaining':diskout[1],
             'Disk_Percent':diskout[2]}

    for measurement, value in to_flux.items():
        try:
            fluxing=fluxer(measurement, server, value, target)
            print(fluxing)
        except Exception as e:
            print(e)

    stdin, stdout, stderr=client.exec_command("ps aux --sort=-%cpu | awk '$3>0 {print$2,$3,$4,$11}'")#PID, %, command
    tops=[]
    for item in stdout.readlines():
        tops.append(item.strip('\n'))
    for item in tops:
        try:
            line=[]
            item=str(item).split(' ')
            for thing in item:
                line.append(thing.strip("[]'"))
            fluxing=fluxer2('running',server,line[0]+'_'+line[3],'cpu_use='+str(float(line[1]))+',mem_use='+str(float(line[2])), target)
            print(fluxing)
        except Exception as e:
            print(e)


