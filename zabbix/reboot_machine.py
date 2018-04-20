#!/usr/local/bin/python3.5
# -*- coding:utf-8 -*-
# author jinxj

from pyVmomi import vim

from pyVim.connect import SmartConnect, Disconnect
import atexit
import requests
import ssl
import sys
from pyVmomi import vmodl

requests.packages.urllib3.disable_warnings()

# Disabling SSL certificate verification
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


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
    print(si)
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
	#vmare主机ip
    Host = 'x.x.x.x'
	#vmware 用户名和密码
    User = 'xxx'
    Password = 'xxx'
	#vmare 端口
    Port = '443'
	# DnsName = 'k8sm' 主机名 
    DnsName = sys.argv[1]
    reboot_vm(Host, User, Password, Port, DnsName)

