from django.shortcuts import render

# Create your views here.
from . import models
from django.shortcuts import render
from . import models
import paramiko
import os
from threading import Thread
def login(request):
    return render(request,'gitweb/login.html')
def act(request):
    name=request.POST['name']
    password=request.POST['password']
    data=models.User.objects.get(id=1)
    data_name = data.name.encode()
    data_password = str(data.password)
    if name == data_name and str(password) == data_password:
        return render(request,'gitweb/cg.html')
    else:
        return render(request,'gitweb/login.html', {'err':'the name is not cz or your passwd is err'})
def ssh_com(ip):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, 22, 'root', 'redhat')
    # std_in, std_out, std_err = ssh_client.exec_command(command)
    return ssh_client
def info(ip,command):
    ssh_client = ssh_com(ip)
    std_in, std_out, std_err = ssh_client.exec_command(command)
    for i in std_out:
        a=i.strip("\n").encode()
    return a

def content(request):
    arr=[]
    ssh_client=ssh_com('172.24.2.152')
    std_in, std_out, std_err = ssh_client.exec_command('ls /tmp/version | grep war')
    for line in std_out:
        arr.append(line.strip("\n"))
    ssh_client.close()

    bb1=info('172.24.205.3','cat /etc/redhat-release')
    bb2 = info('172.24.205.13', 'cat /etc/redhat-release')
    mem1 = info('172.24.205.3', 'cat /proc/meminfo | head -n2')
    mem2 = info('172.24.205.13', 'cat /proc/meminfo | head -n2')
    ip1 = info("172.24.205.3", "ifconfig | grep 172 | awk '{print$2}'")
    ip2 = info("172.24.205.13", "ifconfig | grep 172 | awk '{print$2}'")
    io1 = info("172.24.205.3", "iostat | grep avg - cpu - A1")
    io2 = info("172.24.205.13", "iostat | grep avg - cpu - A1")

    return render(request, 'gitweb/content.html',{'io1':io1,'io2':io2,'arr': arr,'ip1':ip1,'ip2':ip2,'bb1':bb1,'bb2':bb2,'mem1':mem1,'mem2':mem2})
def send(ip,local,nali):
    t = paramiko.Transport((ip, 22))
    t.connect(username='root', password='redhat')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local, nali)
    t.close()

def contact(request):
    ssh_client = ssh_com('172.24.205.3')
    ssh_client.exec_command('rm -rf /var/www/www.fz.com/*')
    ssh_client.close()
    ssh_client = ssh_com('172.24.205.13')
    ssh_client.exec_command('rm -rf /var/www/www.fz.com/*')
    ssh_client.close()

    ssh_client = ssh_com('172.24.2.152')
    std_in, std_out, std_err = ssh_client.exec_command('ls /tmp/version | wc -l')
    for i in std_out:
        num=i.strip("\n")
    ssh_client.exec_command('mv /tmp/version/test.war /tmp/version/v{}.war'.format(num))
    local = "/tmp/version/v{}.war".format(num)
    nali = "/var/www/www.fz.com/v{}.war".format(num)
    # ssh_client.close()
    th1 = Thread(target=send, args=('172.24.205.13',local,nali,))
    th2 = Thread(target=send, args=('172.24.205.3',local,nali,))
    th1.start()
    th2.start()

    ssh_client = ssh_com('172.24.205.3')
    ssh_client.exec_command("unzip  /var/www/www.fz.com/v{}.war  -d  /var/www/www.fz.com/".format(num))
    ssh_client.exec_command("rm -rf /var/www/www.fz.com/v{}.war".format(num))
    ssh_client.close()
    # ssh_client = ssh_com('172.24.205.13')
    # ssh_client.exec_command("unzip  /var/www/www.fz.com/v{}.war  -d  /var/www/www.fz.com".format(num))
    # ssh_client.exec_command("rm -rf /var/www/www.fz.com/v{}.war".format(num))
    # ssh_client.close()

    return render(request, 'gitweb/gxcg.html')

def conthg(request):
    ssh_client=ssh_com('172.24.205.3')
    ssh_client.exec_command('rm -rf /var/www/www.fz.com/*')
    ssh_client.close()
    ssh_client = ssh_com('172.24.205.13')
    ssh_client.exec_command('rm -rf /var/www/www.fz.com/*')
    ssh_client.close()

    se_name = request.POST.get('se_name')
    local = "/var/www/www.fz.com/" + se_name
    nali = "/var/www/www.fz.com/" + se_name
    th1 = Thread(target=send, args=('172.24.205.13', local,nali))
    th2 = Thread(target=send, args=('172.24.205.3', local,nali))
    th1.start()
    th2.start()

    ssh_client = ssh_com('172.24.205.3')
    ssh_client.exec_command("unzip /var/www/www.fz.com/{} -d /var/www/www.fz.com/".format(se_name))
    ssh_client.exec_command("rm -rf /var/www/www.fz.com/{}".format(se_name))
    ssh_client.close()
    ssh_client = ssh_com('172.24.205.13')
    ssh_client.exec_command("unzip /var/www/www.fz.com/{} -d /var/www/www.fz.com/".format(se_name))
    ssh_client.exec_command("rm -rf /var/www/www.fz.com/{}".format(se_name))
    ssh_client.close()

    return render(request, 'gitweb/cscg.html')
