
from pyVim import connect as pyVimConnect
import subprocess

def connect():
    return pyVimConnect.Connect("localhost", 443, "root", "<tkstDjhjnybxrb")
    #return pyVimConnect.ConnectNoSSL("192.168.1.19", 443, "root", "<tkstDjhjnybxrb")

def getVmDescriprionByIp(cluster, ipAddress):
    
    vmDescription = dict()
    vmDescription["vmId"] = None
    vmDescription["poweredOn"] = None
    vmDescription["vmxPath"] = None
    vmDescription["vmPath"] = set()
    vmDescription["vmdkPath"] = []
    vmDescription["vmDatastorePath"] = []

    vm = cluster.content.searchIndex.FindByIp(None, ipAddress, True)
    if vm != None:
        vmDescription["poweredOn"] = True if str(vm.runtime.powerState) == "poweredOn" else False
        vmDescription["vmId"] = vm._moId
        for ds in vm.config.datastoreUrl:
            dsName = "[" + ds.name + "]"
            if vm.config.files.vmPathName.find(dsName) > -1:
                vmDescription["vmxPath"] = vm.config.files.vmPathName.replace(dsName + " ", ds.url)
                rootPath = vmDescription["vmxPath"][:vmDescription["vmxPath"].rfind("/") + 1]
                #vmDescription["vmxPathTemp"] = "./Ubuntu_Test.vmx" #Отладка

                vmxFile = open(vmDescription["vmxPath"])
                vmxConfigLine = vmxFile.readline()
                trap = False
                
                while vmxConfigLine:
                    if trap:
                        vmdkPath = vmxConfigLine.replace(vmxConfigLine[ : vmxConfigLine.find("=") + 3], "")[:-2]
                        if vmdkPath[0] != "/":
                            vmdkPath = rootPath + vmdkPath
                        vmDescription["vmdkPath"].append(vmdkPath)
                        vmDescription["vmPath"].add(vmdkPath[:vmdkPath.rfind("/") + 1])
                        trap = False
                    else:
                        if vmxConfigLine.find("hardDisk") > -1:
                            trap = True
                    
                    vmxConfigLine = vmxFile.readline()

                vmxFile.close()
                
                break
        for ds in vm.config.datastoreUrl:
            if ds.url in " ".join(vmDescription["vmdkPath"]):
                vmDescription["vmDatastorePath"].append(ds.url)

        return vmDescription

    return None

def shutdown(vmId):
    return subprocess.call(["vim-cmd", "vmsvc/power.shutdown", vmId], stdout = subprocess.DEVNULL)

def powerOff(vmId):
    return subprocess.call(["vim-cmd", "vmsvc/power.off", vmId], stdout = subprocess.DEVNULL)

def destroy(vmId):
    return subprocess.call(["vim-cmd", "vmsvc/destroy", vmId], stdout = subprocess.DEVNULL)

def datastoresPath():
    
    dsList = []

    for datastore in connect().content.rootFolder.childEntity[0].datastoreFolder.childEntity:
        dsList.append(datastore.info.url)

    return dsList