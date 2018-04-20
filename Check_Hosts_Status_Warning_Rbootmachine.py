#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# author jinxj

# import requests
import json
import datetime
# import ssl

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import requests
import ssl
from pyVmomi import vmodl

requests.packages.urllib3.disable_warnings()

# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE

class Hosts():

    def __init__(self, hosts_url, auth):
        self.hosts_url = hosts_url
        self.auth = auth

    """
    获取集群整个服务信息：
    1、通过get方式获取总服务信息；
    2、格式化信息并保存所有服务和自身id；
    3、对照总服务字典排除非平台服务，若为本平台服务，直接放回服务id
    """
    # 通过get方式获取总服务信息；

    def gethostconfig(self):
        req = requests.get(url=self.hosts_url, auth=self.auth)
        return req.text

    # 格式化信息并保存服务名字，id，实例数，stack链接（stack名字可以返回，但速度慢）；
    def doubleformat(self):
        data = json.loads(self.gethostconfig())['data']
        host_dic = {}
        for i in range(len(data)):
            try:
                host = data[i]['hostname']
                host_dic[host] = {}
                host_dic[host]['hostname'] = data[i]['hostname'].split('.')[0]
                host_dic[host]['id'] = data[i]['id']
                host_dic[host]['state'] = data[i]['state']
                host_dic[host]['agentIpAddress'] = data[i]['agentIpAddress']
                host_dic[host]['memTotal'] = data[i]['info']['memoryInfo']['memTotal']
                host_dic[host]['memfbc'] = data[i]['info']['memoryInfo']['buffers'] + \
                    data[i]['info']['memoryInfo']['memFree'] + data[i]['info']['memoryInfo']['cached']
                host_dic[host]['dockerversion'] = data[i]['info']['osInfo']['dockerVersion']
                host_dic[host]['kernelVersion'] = data[i]['info']['osInfo']['kernelVersion']
                host_dic[host]['operatingSystem'] = data[i]['info']['osInfo']['operatingSystem']
                host_dic[host]['dockerStorageDriver'] = data[i]['info']['diskInfo']['dockerStorageDriver']
                host_dic[host]['cpucount'] = data[i]['info']['cpuInfo']['count']
            except KeyError:
                continue
        return host_dic

    def checkhost(self):
        host_dic = self.doubleformat()
        host_error_list = []
        # print(host_dic)
        for i in host_dic:
            # print(host_dic[i])
            if host_dic[i]['state'] == 'active':
                host_error_list.append(host_dic[i]['hostname'])
        return host_error_list


def send_msg(url, account, msg):
    """发送邮件, 微信, 端口"""
    payload = {
        'account': account,
        'title': 'rancher reboot hosts result',
        'msg': msg}
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    r = requests.post(url, data=payload, headers=headers)
    # return r.status_code
    return r.text

def reboot_vm(Host, User, Password, Port, DnsName):
    """重启虚拟机"""


    def wait_for_tasks(service_instance, tasks):
        """Given the service instance si and tasks, it returns after all the tasks are complete"""
        property_collector = service_instance.content.propertyCollector
        task_list = [str(task) for task in tasks]
        # Create filter
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                     for task in tasks]
        property_spec = vmodl.query.PropertyCollector.PropertySpec(
            type=vim.Task, pathSet=[], all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [property_spec]
        pcfilter = property_collector.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            # Loop looking for updates till the state moves to a completed
            # state.
            while len(task_list):
                update = property_collector.WaitForUpdates(version)
                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue
                            if not str(task) in task_list:
                                continue
                            if state == vim.TaskInfo.State.success:
                                # Remove task from taskList
                                task_list.remove(str(task))
                            elif state == vim.TaskInfo.State.error:
                                raise task.info.error
                # Move to next version
                version = update.version
        finally:
            if pcfilter:
                pcfilter.Destroy()
    si = SmartConnect(host=Host,
                      user=User,
                      pwd=Password,
                      port=Port, sslContext=context)
    atexit.register(Disconnect, si)
    if not si:
        raise SystemExit("Unable to connect to host with supplied info.")

    VM = si.content.searchIndex.FindByDnsName(None, DnsName, True)
    if VM is None:
        raise SystemExit("Unable to locate VirtualMachine.")
    print("Found: {0}".format(VM.name))
    print("The current powerState is: {0}".format(VM.runtime.powerState))
    if VM.runtime.powerState == 'poweredOn':
        TASK = VM.ResetVM_Task()
        wait_for_tasks(si, [TASK])
    else:
        VM.PowerOn()
    return "reboot vmware {0} ok.".format(VM.name)


if __name__ == '__main__':
    # 环境key和secret
    access_key = 'xxx'
    secret_key = 'xxx'

    code = (access_key, secret_key)
    hosts_url = 'http://x.x.x.:8080/v2-beta/projects/1a5/hosts?limit=-1'
    account = 'xxx'

    rancher_hosts = Hosts(hosts_url, code)
    # print(rancher_hosts.doubleformat())
    host_list = rancher_hosts.checkhost()
    now_time = datetime.datetime.now()

    """
    重启主机引用
	Host vmware 主机地址
	User vmware 主机用户
	Password  vmware 主机密码
	Port  vmware 主机端口
	Host_list 虚拟主机名字
    """
    Host = 'x.x.x.x'
    User = 'xxx'
    Password = 'xxxx'
    Port = '443'
    host_list = ['k8s-m']
    if len(host_list) == 0:
        print('{0} {1} rancher集群主机正常!'.format(now_time, host_list))
    else:
        for i in host_list:
            reboot_vm(Host, User, Password, Port,i)
            result_v = '{0}生产环境rancher集群hosts主机 {1} 重启！！'.format(now_time, i)
            print(result_v)
            url_send_mail = 'http://x.x.x.x/basic/msg/send_mail_msg'  # 邮件通知
            print("邮件通知结果："+send_msg(url_send_mail, account, result_v))

            url_send_wechat = 'http://x.x.x.x/basic/msg/send_wechat_msg'  # 微信通知
            print("微信通知结果："+send_msg(url_send_wechat, account, result_v))

            url_send_sms = 'http://x.x.x.x/basic/msg/send_sms_msg'  # 短信通知
            print("短信通知结果："+send_msg(url_send_sms, account, result_v))
