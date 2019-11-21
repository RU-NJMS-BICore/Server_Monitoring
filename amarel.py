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

    stdin, stdout, stderr=client.exec_command("mmlsquota -u "+user+" cache | awk 'END {print $3, $4}'")#used, remaining
    cache=[]
    for item in stdout.readlines():
        cache.append(item.strip('\n'))
    cache=str(cache).split(' ')
    cacheout=[]
    for item in cache:
        cacheout.append(float(item.strip("'[]"))/1024/1024)

    stdin, stdout, stderr=client.exec_command("mmlsquota -u "+user+" newscratch | awk 'END {print $3, $4}'")#used, remaining
    scratch=[]
    for item in stdout.readlines():
        scratch.append(item.strip('\n'))
    scratch=str(scratch).split(' ')
    scratchout=[]
    for item in scratch:
        scratchout.append(float(item.strip("'[]"))/1024/1024)

    to_flux={'Disk_Total':cacheout[1],
                 'Disk_Remaining':float(cacheout[1])-float(cacheout[0]),
                 'Disk_Percent':(float(cacheout[0])/float(cacheout[1]))*100,
            }

    for measurement, value in to_flux.items():
        try:
            fluxing=fluxer(measurement, 'Amarel_Cache', value, target)
            print(fluxing)
        except Exception as e:
            print(e)

    to_flux={'Disk_Total':scratchout[1],
                 'Disk_Remaining':float(scratchout[1])-float(scratchout[0]),
                 'Disk_Percent':(float(scratchout[0])/float(scratchout[1]))*100,
            }

    for measurement, value in to_flux.items():
        try:
            fluxing=fluxer(measurement, 'Amarel_Scratch', value, target)
            print(fluxing)
        except Exception as e:
            print(e)

    to_flux={'Disk_Total':float(cacheout[1])+float(scratchout[1]),
                 'Disk_Remaining':(float(scratchout[1])+float(cacheout[1]))-(float(cacheout[0])+float(scratchout[0])),
                 'Disk_Percent':((float(cacheout[0])+float(scratchout[0]))/(float(scratchout[1])+float(cacheout[1])))*100,
            }

    for measurement, value in to_flux.items():
        try:
            fluxing=fluxer(measurement, 'Amarel_Total', value, target)
            print(fluxing)
        except Exception as e:
            print(e)
    

    stdin, stdout, stderr=client.exec_command("squeue -u "+user+" | awk ' {print $1, $3, $5}'")#job id, name, status
    queue=[]
    for item in stdout.readlines():
        queue.append(item.strip('\n'))
    for item in queue[1:]:
        try:
            line=[]
            item=str(item.split(' '))
            for thing in item:
                line.append(thing.strip("[]'"))
            fluxing=fluxer2('running',server,line[0]+'_'+line[1],'status='+line[2], target)
        except Exception as e:
            print(e)
