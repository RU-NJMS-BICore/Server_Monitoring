# Server_Monitoring
Repository for server monitoring scrips

This uses a Raspberry Pi server to host an InfluxDB and Grafana server. 
There is also a "serverslist.py" file that contains a list of the servers and associated credentials, as well as the target address for the server to put the information. I have it push to a database called "school" since thats what this is for. Creative eh?

## To run
Once you've set up your serverslist.py file, your DB and grafana, execute by calling the server_monitor.py script. 

This is currently designed to talk with:
* Any Linux server with ssh enabled
* The Amarel HPC cluster at Rutgers (need an account)
