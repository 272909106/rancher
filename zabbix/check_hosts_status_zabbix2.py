#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# author jinxj


import json
import datetime
import requests
# import ssl
import sys



class Hosts():
   def __init__(self, hosts_url,auth):
        self.hosts_url = hosts_url
        self.auth = auth

   def gethostconfig(self):
        req = requests.get(url=self.hosts_url, auth=self.auth)
        return req.text

   def doubleformat(self):
        data = json.loads(self.gethostconfig())['data']
        host_dic = {}
        for i in range(len(data)):
            try:
                host = data[i]['hostname']
                host_dic[host] = {}
                host_dic[host]['hostname'] = data[i]['hostname'].split('.')[0]
                # host_dic[host]['id'] = data[i]['id']
                host_dic[host]['state'] = data[i]['state']
                # host_dic[host]['agentIpAddress'] = data[i]['agentIpAddress']
                # host_dic[host]['memTotal'] = data[i]['info']['memoryInfo']['memTotal']
                # host_dic[host]['memfbc'] = data[i]['info']['memoryInfo']['buffers'] + \
                #     data[i]['info']['memoryInfo']['memFree'] + data[i]['info']['memoryInfo']['cached']
                # host_dic[host]['dockerversion'] = data[i]['info']['osInfo']['dockerVersion']
                # host_dic[host]['kernelVersion'] = data[i]['info']['osInfo']['kernelVersion']
                # host_dic[host]['operatingSystem'] = data[i]['info']['osInfo']['operatingSystem']
                # host_dic[host]['dockerStorageDriver'] = data[i]['info']['diskInfo']['dockerStorageDriver']
                # host_dic[host]['cpucount'] = data[i]['info']['cpuInfo']['count']
            except KeyError:
                continue
        return host_dic


if __name__ == '__main__':
    # 预生产环境key和secret
    access_key = '30D7A3531D10618F6B11'
    secret_key = '69P2DbiH2iQUFHrzG16KheXKkFA8sjokhEvtPRsr'

    code = (access_key, secret_key)
    hosts_url = 'http://10.100.17.124:8080/v2-beta/projects/1a5/hosts?limit=-1'
    rancher_hosts = Hosts(hosts_url, code)
    host_list = rancher_hosts.doubleformat()
    # print(host_list)


    # def checkhost(self):
    #     host_dic = self.doubleformat()
    #     host_error_list = []
    #     # print(host_dic)
    #
    #     for i in host_dic:
    #         # print(host_dic[i])
    #         if host_dic[i]['state'] == 'active':
    #             host_error_list.append(host_dic[i]['hostname'])
    #     return host_error_list
    # hostname=sys.argv[1]
    hostname='vmlin5791'
    for i in host_list:
        # print(i)
        # print(host_list[i]['hostname'])
        # print(host_list[i]['state'])
        if host_list[i]['hostname'] == hostname and host_list[i]['state'] == 'active':
            print(1)
        elif host_list[i]['hostname'] == hostname and host_list[i]['state'] != 'active':
            print(0)