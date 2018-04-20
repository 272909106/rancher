#!/usr/local/bin/python3.5
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
    # 生产环境key和secret
    access_key = 'xxxxx'
    secret_key = 'xxxxxx'

    code = (access_key, secret_key)
    hosts_url = 'http://x.x.com.cn/v2-beta/projects/1a5/hosts?limit=-1'
    rancher_hosts = Hosts(hosts_url, code)
    host_list = rancher_hosts.doubleformat()
    # print(host_list)

    hostname=sys.argv[1]
    for i in host_list:
        if host_list[i]['hostname'] == hostname and host_list[i]['state'] == 'active':
            print(1)
        elif host_list[i]['hostname'] == hostname and host_list[i]['state'] != 'active':
            print(0)
