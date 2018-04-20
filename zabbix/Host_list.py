#!/usr/local/bin/python3.5
#coding:utf-8
# author jinxj
import json
import requests
class Hosts():
    def __init__(self, hosts_url, auth):
        self.hosts_url = hosts_url
        self.auth = auth
    def gethostconfig(self):
        req = requests.get(url=self.hosts_url, auth=self.auth)
        return req.text
    def doubleformat(self):
        data = json.loads(self.gethostconfig())['data']
        subdata = []
        for i in range(len(data)):
            # try:
            hostname = data[i]["hostname"].split('.')[0]
            subhost={"{#RANCHERHOST}":hostname}
            subdata.append(subhost)
        host_dic = {"data": subdata}
        return host_dic
if __name__ == '__main__':
    # 预生产环境key和secret
    access_key = 'xxxxx'
    secret_key = 'xxxxxxx'
    code = (access_key, secret_key)
    hosts_url = 'http://x.x.com.cn/v2-beta/projects/1a5/hosts?limit=-1'
    rancher_hosts = Hosts(hosts_url, code)
    host_list = rancher_hosts.doubleformat()
    print(json.dumps(host_list,sort_keys=True,indent=4))
