#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# author jinxj

# import requests
import json
import datetime
import requests
# import ssl



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
        subdata = []
        for i in range(len(data)):
            # try:
            hostname = data[i]['hostname'].split('.')[0]
            subhost={"#RANCHERHOST":hostname}
            subdata.append(subhost)
        host_dic = {'data': subdata}
        return host_dic









if __name__ == '__main__':
    # 预生产环境key和secret
    access_key = '30D7A3531D10618F6B11'
    secret_key = '69P2DbiH2iQUFHrzG16KheXKkFA8sjokhEvtPRsr'

    code = (access_key, secret_key)
    hosts_url = 'http://10.100.17.124:8080/v2-beta/projects/1a5/hosts?limit=-1'
    account = 'jinxj'

    rancher_hosts = Hosts(hosts_url, code)
    # print(rancher_hosts.doubleformat())
    host_list = rancher_hosts.doubleformat()
    now_time = datetime.datetime.now()
    print(host_list)
    """
    重启主机引用
    """
    # Host = '10.96.140.157'
    # User = 'open\jinxj'
    # Password = 'oa123456'
    # Port = '443'
    # host_list = ['k8s-m']
    # print(host_list)
    # if len(host_list) == 0:
    #     print('{0} {1} rancher集群主机正常!'.format(now_time, host_list))
    # else:
    #     for i in host_list:
    #         reboot_vm(Host, User, Password, Port,i)
    #         result_v = '{0}生产环境rancher集群hosts主机 {1} 重启！！'.format(now_time, i)
    #         print(result_v)
    #         url_send_mail = 'http://10.100.17.175:5555/basic/msg/send_mail_msg'  # 邮件通知
    #         print("邮件通知结果："+send_msg(url_send_mail, account, result_v))
    #
    #         url_send_wechat = 'http://10.100.17.175:5555/basic/msg/send_wechat_msg'  # 微信通知
    #         print("微信通知结果："+send_msg(url_send_wechat, account, result_v))
    #
    #         url_send_sms = 'http://10.100.17.175:5555/basic/msg/send_sms_msg'  # 短信通知
    #         print("短信通知结果："+send_msg(url_send_sms, account, result_v))
