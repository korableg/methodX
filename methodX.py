
#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import esxi
import threading
import subprocess
import sms
from settings import Settings
from cleaner import cleanDiskSpace
from socketserver import *
import time

datastores = esxi.datastoresPath()

if len(datastores) > 0:
    settings = Settings(datastores[0])
else:
    raise Exception("Don't find datastore")

lock = threading.Lock()

class methodXServerHandler(StreamRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024)

        if lock.acquire(False):
            try:
                data = self.data.decode().replace("\r","").replace("\n","")
                if data == settings.Secret:
                    self.request.sendall(b'Ok secret. Starting destroy VMs')
                    sms.send(settings.Phones)
                    handleVMs(destroyVM)
                    time.sleep(5)
                    subprocess.call(["rm", "-rf", "/scratch/vmware/../log/*"], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
                    subprocess.call(["rm", "-rf", settings.Path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.call(["esxcli", "software", "vib", "remove", "-n", "methodX", "--no-live-install"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    threadList = []
                    for datastorePath in datastores:
                        thread = threading.Thread(target = cleanDiskSpace, args = (datastorePath + "/",))
                        threadList.append(thread)
                        thread.start()
                    for thread in threadList:
                        thread.join()
                    self.request.sendall(b'Done')
                elif data == settings.TestSecret:
                    sms.send(settings.Phones)
                    handleVMs(shutdownVM)
                    self.request.sendall(b'Done')
                elif data == "TestConnect":
                	self.request.sendall(b'Connect OK')
                	self.request.sendall(b'Done')
            except Exception as e:
                self.request.sendall(bytes(str(e), "utf-8"))
            finally:
                lock.release()
        else:
            self.request.sendall(b'Process already started ...')


def handleVMs(vmHandleFunc):
    cluster = esxi.connect()
    for ipAddress in settings.VMS:
        vmDescription = esxi.getVmDescriprionByIp(cluster, ipAddress) 
        if vmDescription != None:
            vmHandleFunc(vmDescription)

def destroyVM(vmDescription: dict):
    if (vmDescription["poweredOn"]):
        esxi.powerOff(vmDescription["vmId"])
        time.sleep(1)
    esxi.destroy(vmDescription["vmId"])

def shutdownVM(vmDescription: dict):
    if (vmDescription["poweredOn"]):
        esxi.shutdown(vmDescription["vmId"])

if __name__ == "__main__":

    server = TCPServer(("0.0.0.0", settings.Port), methodXServerHandler)
    try:
        settings.Check()
        server.serve_forever()
    except Exception as e:
        print("Error: %s" % e)
    finally:
        server.server_close()