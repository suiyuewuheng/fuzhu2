# start a new view
from django.http import HttpResponse
from django.shortcuts import render, redirect
from faker import Faker
from polls.models import *
import sys, os, re
from subprocess import Popen, PIPE
import time
import datetime
from math import ceil
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
import paramiko
import importlib

importlib.reload(sys)
import threading, socket


#################kvm info ###########################

def session(host, uname, pwd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=uname, password=pwd)
        print("Login %s is successful" % host)
        return ssh
    except Exception as e:
        print(e.message)


def get_hostname(host, uname, pwd):
    cmd_hostname = "hostname"
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command(cmd_hostname, get_pty=True)
    hostname = stdout.read()
    return hostname

    # 获取Linux网络ipv4信息


def get_ifconfig(host, uname, pwd):
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command("sudo ifconfig eth0 | grep 'inet ' | awk '{ print $2 }' ", get_pty=True)
    data = stdout.read().decode('utf-8')

    return data


# 获取Linux系统版本信息
def get_version(host, uname, pwd):
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command("sudo cat /etc/redhat-release", get_pty=True)
    data = stdout.read()
    return data


# 获取Linux系统CPU信息
def get_cpu(host, uname, pwd):
    cpunum = 0
    processor = 0
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command("sudo cat /proc/cpuinfo", get_pty=True)
    cpuinfo = stdout.readlines()
    # with stdout.read() as cpuinfo:
    for i in cpuinfo:
        if i.startswith('physical id'):
            cpunum = i.split(":")[1]
        if i.startswith('processor'):
            processor = processor + 1
        if i.startswith('model name'):
            cpumode = i.split(":")[1]
    return int(cpunum) + 1, processor, cpumode


# 获取Linux系统memory信息
def get_memory(host, uname, pwd):
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command("sudo cat /proc/meminfo", get_pty=True)
    meminfo = stdout.readlines()
    # with open('/proc/meminfo') as meminfo:
    for i in meminfo:
        if i.startswith('MemTotal'):
            memory = int(i.split()[1].strip())
            memory = '%.f' % (memory / 1024.0) + 'MB'
        else:
            pass
        return memory


# 获取Linux系统网卡信息
def get_ethernet(host, uname, pwd):
    client = session(host, uname, pwd)
    stdin, stdout, stderr = client.exec_command("sudo lspci", get_pty=True)
    data = stdout.read().decode('utf-8')
    ret = re.compile('Eth[^\d].*')
    eth = ret.search(data).group()
    return eth


######################################################


######################remote_to_remote##################
class HostInfo:
    def __init__(self, host, port, username, password, location):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.location = location


def sftp_remote_to_remote(remote_from, remote_to):
    sf_from = paramiko.Transport((remote_from.host, remote_from.port))
    sf_from.connect(username=remote_from.username, password=remote_from.password)
    sftp_from = paramiko.SFTPClient.from_transport(sf_from)

    sf_to = paramiko.Transport((remote_to.host, remote_to.port))
    sf_to.connect(username=remote_to.username, password=remote_to.password)
    sftp_to = paramiko.SFTPClient.from_transport(sf_to)

    with sftp_to.file(remote_to.location, 'wb') as fl:
        fl.set_pipelined(True)

        file_size = sftp_from.stat(remote_from.location).st_size
        with sftp_from.open(remote_from.location, 'rb') as fr:
            fr.prefetch(file_size)
            return sftp_from._transfer_with_callback(
                reader=fr, writer=fl, file_size=file_size, callback=None
            )


#########################################################

def index(request):
    now = datetime.datetime.now()
    f = Faker()
    # total = Question.objects.count()
    # x = ceil(total/10.0)
    # y = range(1,int(x)+1)
    # all_q = Question.objects.order_by('-pub_date')[:10]
    return render(request, 'release/index.html')


def aboutus(request):
    values = {}
    return render(request, 'release/aboutus.html', values)


def my_login_required(func):
    def inside(request):
        if request.user.is_authenticated():
            return func(request)
            # return HttpResponse('successfully...')
        else:
            # return render(request,'polls/loginpage.html')
            return redirect(reverse('release:aboutus'))

    return inside


@my_login_required
def backup(request):
    now_time = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    backup_name = request.POST.get('backup_name')
    os.system('mv /release/source/%s /release/source/cloud_%s' % (backup_name, now_time))

    return redirect(reverse('release:jobmenu'))


@my_login_required
def scan(request):
    return jobmenu(request)


@my_login_required
def start_release(request):
    release_name = request.POST.get('release_name')
    ################# remote_to_remote ###########
    try:
        remote_from = HostInfo('172.24.45.45', 22, 'student', 'redhat', '/release/source/%s' % release_name)
        remote_to = HostInfo('172.24.205.1', 22, 'admin', 'redhat', '/var/www/www.fz.com/cloud_last')
        thr1 = threading.Thread(target=sftp_remote_to_remote(remote_from, remote_to))
        thr1.start()
        # time.sleep(2)
        remote_to2 = HostInfo('172.24.45.14', 22, 'admin', 'redhat', '/var/www/www.fz.com/cloud_last')
        thr2 = threading.Thread(target=sftp_remote_to_remote(remote_from, remote_to2))
        thr2.start()
        get_result = "sucessfully..."
    except:
        get_result = "failer..."
    return render(request, 'release/result.html',{'get_result':get_result})


@my_login_required
def jobmenu(request):
    dir = os.listdir("/release/source")
    return render(request, 'release/jobmenu.html',{'dir': dir})

@my_login_required
def hosts(request):
    ####################kvm info##################
    # host = sys.argv[1]
    try:
        host = "172.24.205.1"
        uname = "admin"
        pwd = "redhat"
        port = 22
        # host = raw_input("please input the hostname: ")
        # result = GetLinuxMessage()
        result1 = get_hostname(host, uname, pwd)
        result2 = get_ifconfig(host, uname, pwd)
        result3 = get_version(host, uname, pwd)
        result4, result5, result6 = get_cpu(host, uname, pwd)
        result7 = get_memory(host, uname, pwd)
        result8 = get_ethernet(host, uname, pwd)
        #################################################
        host_2 = "172.24.45.14"
        uname_2 = "admin"
        pwd_2 = "redhat"
        result2_1 = get_hostname(host_2, uname_2, pwd_2)
        result2_2 = get_ifconfig(host_2, uname_2, pwd_2)
        result2_3 = get_version(host_2, uname_2, pwd_2)
        result2_4, result2_5, result2_6 = get_cpu(host_2, uname_2, pwd_2)
        result2_7 = get_memory(host_2, uname_2, pwd_2)
        result2_8 = get_ethernet(host_2, uname_2, pwd_2)
    except:
        print("...")
    return render(request, 'release/hosts.html',{ 'result1': result1, 'result2': result2, 'result3': result3, 'result4': result4,'result5': result5, 'result6': result6, 'result7': result7, 'result8': result8,'result2_1': result2_1, 'result2_2': result2_2, 'result2_3': result2_3, 'result2_4': result2_4,'result2_5': result2_5, 'result2_6': result2_6, 'result2_7': result2_7, 'result2_8': result2_8, })


@my_login_required
def pre_jobmenu(request):
    return render(request, 'release/pre_jobmenu.html')


def checklogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        request.session.set_expiry(0)
        login(request, user)
        return pre_jobmenu(request)
    else:
        # return HttpResponse('Wrong...')
        return render(request, 'release/loginpage.html')


def loginpage(request):
    return render(request, 'release/loginpage.html')


def first(request):
    return render(request,'release/loginpage.html')