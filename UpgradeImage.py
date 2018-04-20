#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# author jinxj

import requests
import json
import time
import sys
import docker
import datetime
#import logging


def docker_pull_tag_push(input_image):
    # logging.basicConfig(level=logging.DEBUG)
    client=docker.from_env()

    #docker-login 登陆私有仓库(可配置多个私有仓库)
    client.login(username="xxx",password="xx",registry='http://xx.xxx.com.cn')
    client.login(username="",password="",registry='http://x.x.x.x:5000')
    temp_image = input_image.split('/')[-1]
    service_name = temp_image.split(':')[0]
    new_version = temp_image.split(':')[1]

    # docker pull 拉去验证镜像
    try:
        image = client.images.pull(input_image)
        print("拉取镜像成功！")
    except docker.errors.NotFound as e:
        print("镜像地址或版本号有误，请重新确认！")
        raise docker.errors.NotFound
    except docker.errors.APIError as f:
        print("项目在私有仓库中不存在，请重新确认！")
        raise docker.errors.APIError

    # docker tag 修改镜像版本
    new_repository = 'dxtrepo.sysgroup.open.com.cn/open/'+service_name
    try:
        docker.models.images.Image.tag(image, repository=new_repository, tag=new_version)
        print("修改镜像版本成功！")
    except Exception as e:
        print("原镜像地址或版本有误，请重新确认")
        raise docker.errors

    # docker push 推送镜像
    result = client.images.push(repository=new_repository, tag=new_version)
    if "not exist" in result:
        print("推送镜像失败")
        raise docker.errors
    else:
        print("推送镜像成功！")
    return "ok"


class CheckSer:

    def __init__(self, server_url, auth):
        self.server_url = server_url
        self.auth = auth

    """
    获取集群整个服务信息：
    1、通过get方式获取总服务信息；
    2、格式化信息并保存所有服务和自身id；
    3、对照总服务字典排除非平台服务，若为本平台服务，直接放回服务id
    """
    def getserconfig(self):
        """通过get方式获取总服务信息"""
        req=requests.get(url=self.server_url,auth=self.auth)
        return req.text

    def doubleformat(self):
        """格式化信息并保存服务名字，id，实例数，stack链接（stack名字可以返回，但速度慢）"""
        data = json.loads(self.getserconfig())['data']
        ser_dic = {}
        for i in range(len(data)):
            try:
                ser_name = data[i]['launchConfig']['imageUuid'].split('/')[-1].split(':')[0]
                ser_dic[ser_name]={}
                ser_dic[ser_name]['name']=data[i]['name']
                ser_dic[ser_name]['id']=data[i]['id']
                ser_dic[ser_name]['currentScale']=data[i]['currentScale']
                # 获取stack名字程序响应3秒左右
                ser_dic[ser_name]['stack']=data[i]['links']['stack']
            except KeyError:
                continue
        return ser_dic

    def getstack(self,stack_url):
        """返回stack名字,因响应慢，暂未使用"""
        req = requests.get(url=stack_url, auth=self.auth)
        data=json.loads(req.text)
        stack_name=data['name']
        return stack_name

    def returncode(self,service_name):
        """对照总服务字典排除非平台服务，若为本平台服务，直接放回服务相关字典信息"""
        ser_dic=self.doubleformat()
        try:
            ser_dic[service_name]
            return ser_dic[service_name]
        except KeyError:
            print('镜像未部署过，请检查镜像名称')
            exit()


class ServiceUpgrade():
    """初始化服务url和认证信息"""
    def __init__(self, service_url, auth):
        self.service_url = service_url
        self.auth = auth

    def getlaughconfig(self):
        """获取服务配置"""
        req=requests.get(url=self.service_url, auth=self.auth)
        return req.text

    def postupgrade(self, new_version):
        """输入新的镜像版本，post方式进行升级服务操作"""
        data=json.loads(self.getlaughconfig())
        # 获取先有镜像信息
        try:
            ser_image=data['upgrade']['inServiceStrategy']['launchConfig']['imageUuid']

        except TypeError :
            # 第一次部署的服务，无upgrade属性，造成升级失败，报异时将获取laugh从laughconfig配置
            ser_image=data['launchConfig']['imageUuid']
        # 获取镜像地址和上一次版本
        image_name=ser_image.split(':')[1]
        old_image_version = ser_image.split(':')[2]
        # 新版本赋值
        image_new_version=new_version
        # 格式化新的镜像
        ser_image_new='docker'+':'+image_name+':'+image_new_version
        # 将新的镜像版本赋值到配置中
        try:
            data['upgrade']['inServiceStrategy']['launchConfig']['imageUuid'] = ser_image_new
            # post操作数据
            post_data = {'launchConfig': data['upgrade']['inServiceStrategy']['launchConfig']}
        except TypeError:
            # 第一次部署的服务，无upgrade属性，造成升级失败，报异时将获取laugh从laughconfig配置
            data['launchConfig']['imageUuid'] = ser_image_new
            # post操作数据
            post_data = {'launchConfig': data['launchConfig']}

        # post升级操作
        data = {
            "inServiceStrategy": post_data,
            "toServiceStrategy": 'null'
        }
        post_url = self.service_url+'/?action=upgrade'
        req = requests.post(post_url, data=json.dumps(data), auth=self.auth)
        return req.text,old_image_version

    def getserstatus(self):
        """获取服务状态"""
        data=json.loads(self.getlaughconfig())
        service_status=data['state']
        return service_status

    def geterrormsg(self):
        """获取服务错误状态码"""
        data=json.loads(self.getlaughconfig())
        service_transitioning = data['transitioning']
        service_transitioning_msg = data['transitioningMessage']
        error_msg={
            'service_transitioning': service_transitioning,
            'service_transitioning_msg': service_transitioning_msg
        }
        return error_msg

    def finishupgrade(self):
        """服务状态为upgrade时，点击完成升级按钮"""
        post_url=self.service_url+'/?action=finishupgrade'
        req=requests.post(post_url, data={}, auth=self.auth)
        service_status = json.loads(req.text)
        return service_status['state']

    def rollback(self):
        """回滚程序操作"""
        post_url = self.service_url+'/?action=rollback'
        req = requests.post(post_url, data={}, auth=self.auth)
        service_status = json.loads(req.text)
        return service_status['state']

    def checkstatus(self):
        """查看服务状态和错误状态"""
        print(self.getserstatus())
        print(self.geterrormsg())

    def getscale(self):
        """获取服务当前实例数"""
        current_scale = json.loads(self.getlaughconfig())['scale']
        return current_scale

    def putscale(self, scale):
        """put方式更新实例数"""
        data = json.loads(self.getlaughconfig())
        data['scale'] = scale
        req=requests.put(self.service_url,data=data,auth=self.auth)
        return req


if __name__ == '__main__':
    """
       active     服务激活状态
       upgrading  服务升级状态
       upgraded   服务升级完状态

       :return: 
       """

    # 生产环境key和secret
    access_key = 'xxxxx'
    secret_key = 'xxxx'

    code = (access_key, secret_key)
    # 生产环境
    ser_url = 'http://xx.xx.com.cn/v2-beta/projects/1a5/services?limit=-1'


    # 总服务实例化
    rancher_service = CheckSer(ser_url, code)
    ser_temp=ser_url.split('?')[0]

    # 获取镜像名字、新版本号，服务名字
    input_image = sys.argv[1]
    temp_image = input_image.split('/')[-1]
    service_name = temp_image.split(':')[0]
    new_version = temp_image.split(':')[1]
    service_url = ser_temp+'/'+rancher_service.returncode(service_name)['id']
    rancher_ser_name=rancher_service.returncode(service_name)['name']

    # 镜像拉去、修改tag，推送到生产私有仓库
    docker_pull_tag_push(input_image)

    # 服务实例化
    up_service = ServiceUpgrade(service_url, code)
    current_scale = up_service.getscale()
    stime=datetime.datetime.now()
    print(stime)
    if up_service.getserstatus() == 'active':
        if current_scale > 2:
            up_service.putscale(2)
            time.sleep(5)
    # 通过返回值获取旧版本
        old_image_version = up_service.postupgrade(new_version)[1]
        while True:
            etime=datetime.datetime.now()
            print(etime)
            estime=(etime-stime).seconds
            if estime < 1800:
                """
                升级时间大于1800秒=30分钟直接回滚操作
                """
                if up_service.getserstatus() == 'upgrading':
                    up_service.checkstatus()
                    time.sleep(5)
                elif up_service.getserstatus() == 'upgraded':
                    up_service.checkstatus()
                    up_service.finishupgrade()
                    time.sleep(5)
                    if current_scale > 2:
                        up_service.putscale(current_scale)
                    break
            else:
                print(up_service.geterrormsg())
                print(up_service.rollback())
				if current_scale > 2:
                        up_service.putscale(current_scale)
    # elif up_service.getserstatus() == 'upgraded':
    #     print(up_service.finishupgrade())
    #     print(up_service.geterrormsg())
    # elif up_service.getserstatus() == 'upgrading':
    #     print(up_service.geterrormsg())
    #     print(up_service.rollback())