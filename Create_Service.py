import pymysql
import requests
import json
import docker
import logging

"""
获取数据库服务信息函数
"""
def dbinfo():
    """
    链接数据库
    :return:
    """
    db = pymysql.connect(
        host='x.x.x.x',
        port=3306,
        user='xxx',
        passwd='xxx',
        db='xxx',
        charset='utf8')
    return db

def sqlformat(sql):
    """
    sql查询函数
    :param sql:
    :return:
    """
    db = dbinfo()
    cursor = db.cursor()
    cursor.execute(sql)
    sql_result = cursor.fetchall()
    cursor.close()
    db.close()
    return sql_result


def updatedb(sql):
    """
    更新数据库函数
    :param sql:
    :return:
    """
    db = dbinfo()
    cursor = db.cursor()
    # sql = "UPDATE %s set status=%s where developNId=%s" % (table,status, id)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

# 改变高鹏数据库服务中的状态


def chanage_status(num, id):
    """
    更改数据库表状态
    :param num: 状态值
    :param id: 表主键id
    :return:
    """
    change_status_sql = "UPDATE Op_His_Flow_Development_New set status=%s where developNId=%s" % (num, id)
    updatedb(change_status_sql)


def change_num(table_name, table_columns, num, operator):
    """
    根据关键字获取端口和服务序列
    :param table_name:
    :param table_columns:
    :param num:
    :param operator:
    :return:
    """
    if operator == 'add':
        chanage_num_sql = "UPDATE %s set %s = %s where id=1" % (
            table_name, table_columns, int(num) + 1)
    elif operator == 'reduce':
        chanage_num_sql = "UPDATE %s set %s = %s where id=1" % (
            table_name, table_columns, int(num) - 1)
    updatedb(chanage_num_sql)

def createser(postser_url, code, ser_dic):
    """
    创建rancher server服务
    :param postser_url:创建服务url
    :param code: rancher秘钥
    :param ser_dic: post字典
    :return:
    """
    req = requests.post(url=postser_url, data=json.dumps(ser_dic), auth=code)
    result = json.loads(req.text)['type']
    if result == 'error':
        count('reduce')
        chanage_status(5, developNId)
        raise TypeError('%s' % req.text)
    chanage_status(6, developNId)


def count(operator):
    """
    根据关键字获取端口信息和服务序列
    :param operator:add ,reduce
    :return:
    """
    change_num(
        ser_count_table,
        ser_count_table_columns,
        ser_count_num,
        operator)
    change_num(port_count_table, port_table_columns, port_count_num, operator)


def docker_pull_tag_push(input_image):
    """
    拉取镜像、修改名字、推送镜像
    :param input_image:
    :return:
    """
    client = docker.from_env()
    # docker-login 登陆私有仓库

    client.login(username="xxx", password="xxx", registry='http://xxx.com.cn')

    client.login(username="", password="", registry='http://x.x.x.x:5000')
   
    temp_image = input_image.split('/')[-1]
    service_name = temp_image.split(':')[0]
    new_version = temp_image.split(':')[1]

    # docker pull 拉去验证镜像
    try:
        image = client.images.pull(input_image)
        print("拉取镜像成功！")
    except Exception as e:
        print("镜像地址或版本号有误，请重新确认！")
        raise e
    # except docker.errors.APIError as f:
    #     print("项目在私有仓库中不存在，请重新确认！")
    #     raise docker.errors.APIError

    # docker tag 修改镜像版本
    new_repository = 'dxtrepo.sysgroup.open.com.cn/open/' + service_name
    try:
        docker.models.images.Image.tag(
            image, repository=new_repository, tag=new_version)
        print("修改镜像版本成功！")
    except Exception as e:
        print("原镜像地址或版本有误，请重新确认")
        raise e

    # docker push 推送镜像
    result = client.images.push(repository=new_repository, tag=new_version)
    if "not exist" in result:
        raise ("推送镜像失败")
    else:
        print("推送镜像成功！")
    return '%s:%s'%(new_repository,new_version)


if __name__ == '__main__':
    """
    状态值 1 2 3 工单
    4、5、6金
    4 等待状态
    5 失败状态
    6 成功状态
    """

    #日志输出
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        level=logging.DEBUG)
    #前端数据库表名
    ser_table = 'Op_His_Flow_Development_New'
    #查询表内等待调度的服务
    select_ser_sql = "select containerPort,cpuShares,memory,environment,imageName,healthCheck,scale,stackId,developNId from Op_His_Flow_Development_New where `status`=1"
    """
    服务名计数统计表及sql
    """
    ser_count_table = 'Op_SerName_Count'
    ser_count_table_columns = 'ser_name_count'
    select_ser_count_sql = "select ser_name_count from Op_SerName_Count where id = 1"
    """
    服务端口计数统计表及sql
    """
    port_count_table = 'Op_Port_Count'
    port_table_columns = 'port_count'
    select_port_count_sql = "select port_count from Op_Port_Count where id = 1"

    for i in sqlformat(select_ser_sql):
        ser_info = i
        #容器端口
        container_db_Port = ser_info[0]
        #cpu值
        cpuShares = ser_info[1]
        #内存值
        memory = ser_info[2]
        #环境变量
        environment = ser_info[3]
        #镜像地址
        imageName = ser_info[4]
        #健康检查值
        healthCheck = ser_info[5]
        #副本值
        scale = ser_info[6]
        #stack值
        stackId = ser_info[7]
        #前端表主键
        developNId = ser_info[8]

        #设置操作的服务状态为调度等待
        chanage_status(4,developNId)

        #获取新服务命名数
        ser_count_num = sqlformat(select_ser_count_sql)[0][0]
        #获取新服务端口号
        port_count_num = sqlformat(select_port_count_sql)[0][0]
        #获取新服务的端口号和服务命名值d0012——当前基础上各加1
        count('add')

        """
        创建rancher服务
        """
        #生产秘钥
        access_key = 'xxxx'
        secret_key = 'xxxxx'
        code = (access_key, secret_key)
        #预生产服务接口地址
        postser_url = 'http://x.x.x.x:8080/v2-beta/projects/1a5/services'

        # 创建new服务参数
        cpuShares = cpuShares * 1024

        #镜像地址
        image_temp = imageName
        # 拉取改名推送镜像
        image_new_temp = docker_pull_tag_push(image_temp)
        imageUuid = 'docker:' + image_new_temp

        #端口格式化
        #容器端口
        container_port = container_db_Port
        #服务主机端口
        ser_host_port = port_count_num
        ports_temp = str(ser_host_port) + ':' + str(container_port) + '/tcp'
        ports = [
            ports_temp
        ]

        # 七层健康检查，默认检查页/dnotdelet/mom.html
        check_page = '/dnotdelet/mom.html'
        requestLine = "GET \"" + check_page + "\" \"HTTP/1.0\""
        seven_healthCheck = {
            "type": "instanceHealthCheck",
            "healthyThreshold": 2,
            "initializingTimeout": 300000,
            "interval": 10000,
            "port": container_port,
            "reinitializingTimeout": 300000,
            "requestLine": requestLine,
            "responseTimeout": 10000,
            "strategy": "recreate",
            "unhealthyThreshold": 5,
            "name": ''
        }
        four_healthCheck = {
            "type": "instanceHealthCheck",
            "healthyThreshold": 2,
            "initializingTimeout": 300000,
            "interval": 10000,
            "port": ser_host_port,
            "reinitializingTimeout": 300000,
            "requestLine": "",
            "responseTimeout": 10000,
            "strategy": "recreate",
            "unhealthyThreshold": 5
        }
        null_healthCheck = ''
        if healthCheck == 7:
            healthCheck = seven_healthCheck
        elif healthCheck == 4:
            healthCheck = four_healthCheck
        elif healthCheck == 0:
            healthCheck = null_healthCheck

        # 内存4G，2G，不能填写2048,4096
        memory_temp = memory
        memory = memory_temp * 1024 * 1024 * 1024
        # 网络模式，后期会加入host模式
        networkmode = 'managed'
        #日志默认，链接fluentd，输出到elk
        logconfig = {
            "type": "logConfig",
            "config": {
                "fluentd-async-connect": "true"
            },
            "driver": "fluentd"
        }

        #容器服务名生成 ser_name = 'd103studycenterservice'
        ser_name_temp = imageName.split('/')[-1].split(':')[0].replace("-", "")
        ser_name = 'd' + str(ser_count_num) + ser_name_temp


        # 提交服务字典

        ser_dic = {
            # 实例数量
            "scale": scale,
            "launchConfig": {
                # 共享cpu限制
                #            "milliCpuReservation": 1024,  # cpu最少保留资源
                "cpuShares": cpuShares,  # 限制共享cpu资源
                # 服务镜像
                "imageUuid": imageUuid,
                # 环境变量配置
                "environment": json.loads(environment),
                # 健康检查配置
                "healthCheck": healthCheck,

                # 内存限制
                "memory": memory,
                "networkMode": networkmode,
                # 端口配置
                "ports": ports,
                # 日志配置
                "logConfig": logconfig,
            },
            "secondaryLaunchConfigs": [],
            "publicEndpoints": [],
            "assignServiceIpAddress": 'false',
            "lbConfig": "",
            # stack代码必须
            "stackId": stackId,
            # 名字必须
            "name": ser_name,
            # 创建服务立即启动
            #  "startOnCreate": 'true',
        }
        #若不需要健康检查，则删除字典中的healthCheck选项
        if healthCheck == null_healthCheck:
            del ser_dic['launchConfig']['healthCheck']

        # 执行创建rancher服务
        createser(postser_url, code, ser_dic)
        # 服务名写入库
        update_servicename_sql = "UPDATE Op_His_Flow_Development_New set serviceName='%s'  where developNId=%s" % (
            ser_name, developNId)
        updatedb(update_servicename_sql)
        # 服务端口写入库
        update_ser_host_port_sql = "UPDATE Op_His_Flow_Development_New set hostPort='%s'  where developNId=%s" % (
            ser_host_port, developNId)
        updatedb(update_ser_host_port_sql)
