#importing libraries
import os,subprocess

#The folder shared via nfs contains the metadata of the master node
#as well as a file called nodes.txt
#The first line in nodes.txt contains the IP of the master node
#The second line in nodes.txt contains the (ex )IP of the node that is currently the master
#The succeeding lines contain the 1st, 2nd and so and so forth apprentices of the master

#IP address of the current system
ip=(subprocess.getoutput("hostname -I").split())[0]
master=""
nfs=input("Enter the ip of the nfs server:")

#setting the system as client for nfs server
print(subprocess.getoutput("umount /data"))
os.system("rm -rvf /data")
os.system("mkdir /data")
print(subprocess.getoutput("mount "+nfs+":/root/Desktop/Cluster /data"))

#Checking if there are any nodes left for substitution
f=open("/data/nodes.txt","r")
x=(f.read()).split()
if len(x)<=2:
	print("Insufficient number of nodes. Please update IPs in /data/nodes.txt file")
	exit()

#comparing it with the IP at the top of nodes.txt
#iterating till our node doesnt become the first apprentice
i_am_not_master=True
while i_am_not_master:
	f=open("/data/nodes.txt","r")
	x=(f.read()).split()
	if len(x)!=0:
		master=x[0]
		if x[2]==ip:
			i_am_not_master=False
			f.close()
			break
		f.close()

#while the master node is working and connected to the network dont do anything
#as soon as it gets disconnected we have to make the current node the new master
while subprocess.getoutput("ping -c 1 "+master+" | grep -i \'host unreachable\'")=="":
	pass

#rewrite the nodes.txt file
f=open("/data/nodes.txt","w")
y=""
count=0
for i in x:
	if count!=1:
		y+=(i+"\n")
	count=count+1
f.write(y)
f.close()

#change the IP of the current system to that of the master
subprocess.getoutput("sed \'s/"+ip+"/"+master+"/g\' /etc/sysconfig/network-scripts/ifcfg-enp0s3")
subprocess.getoutput("systemctl restart network")

#start service
ans=input("Do you wish to format namenode(y/n)?:")
if ans=='y':
	print(subprocess.getoutput("echo Y | hadoop namenode -format"))
print(subprocess.getoutput("hadoop-daemon.sh start namenode"))

#checking
if subprocess.getoutput("jps | grep -i namenode")!="":
	print("Namenode started")
else:
	print("Namenode start failed")

#ASSUMPTIONS
#1.Files are already configured in the apprentice systems
#2.Apprentice systems already have hadoop installed
#3.All systems in the cluster, as well as the apprentice systems have static IPs
#4.NFS server doesnt fail that easily
