import sys
import json
import urllib
from delfin.drivers.dell_emc.vplex.httpapi import HTTPApi
from drivers.dell_emc.vplex import util

__author__ = "Farooq Khan"
__copyright__ = "Copyright (c) 2012 EMC Corporation"
__version__ = "D20.0.0.0"
__status__ = "Sample Code"

class VPlexApi():
    BASECONTEXT = '/vplex'
    debuglvl = 0
    def __init__(self, config):
        self.httpapi = HTTPApi(config.host, config.port, config.username, config.password)
        self.outputas = config.outputas # this can be either json/xml
    #########################################################
    # Gets a object by its name for the specified cluster
    #########################################################
    def getClusterObjectByName(self, cluster, type, name):
        uri = self.BASECONTEXT + "/clusters/" + cluster
        if type == "virtual-volume":
            uri += "/virtual-volumes"
        elif type == "storage-volume":
            uri += "/storage-elements/storage-volumes"
        elif type == "extent":
            uri += "/storage-elements/extents"
        elif type == "device":
            uri += "/devices"
            uri += "/" + name
            response = self.httpapi.get(uri)
        if response.status != 200:
            print ("Error getting %s : '%s' \n Server Response %d %s " % (type, name, response.status, response.reason))
            return None
        responseObj = json.loads(response.data) # Will return a python Dict object
        return responseObj.get("response")
    #########################################################
    # Gets a object by its type for the specified cluster
    #########################################################
    def getClusterObjectsByType(self, cluster, type):
        uri = self.BASECONTEXT + "/clusters/" + cluster
        if type == "virtual-volume":
            uri += "/virtual-volumes"
        elif type == "storage-volume":
            uri += "/storage-elements/storage-volumes"
        elif type == "extent":
            uri += "/storage-elements/extents"
        response = self.httpapi.get(uri)
        if response.status != 200:
            print("Error getting %s(s) \n Server Response %d %s " % (type, response.status, response.reason))
            return None
        responseObj = json.loads(response.data)
        return responseObj.get("response")
    #########################################################
    # Executes the specified command
    #########################################################
    def executeCmd(self, cmd, args):
        #URL encoding in python is not straight forward below two lines do it.
        tmp = urllib.urlencode({'x':cmd})
        uri = self.BASECONTEXT + "/" + tmp[2:]
        response = self.httpapi.post(uri, args)
        if response.status != 200:
            print("Error executing cmd : '%s' with arguments :'%s' Server Response %d %s :" % (cmd, args, response.status, response.reason))
            return None
        responseObj = json.loads(response.data)
        return responseObj.get("response")
    # Cluster API's
    def clusterListAll(self):
        uri = self.BASECONTEXT + "/clusters"
        response = self.httpapi.get(uri)
        if response.status != 200:
            print("Error getting %s(s) \n Server Response %d %s " % (type, response.status, response.reason))
            return None
        responseObj = json.loads(response.data)
        util.printResponse(responseObj.get("response"), self.outputas)
    def clusterStatus(self):
        response = self.executeCmd("cluster status", None)
        if response:
            util.printCommandResponse(response)
    #########################################################
    # Creates a new extent and returns the new extent
    #
    # Figuring out a just created extent is difficult. RESTful
    # API has no support for it yet.
    #
    # returns extent name
    #########################################################
    def createExtent(self, storageVolName):
        extsBefore = self.getClusterObjectsByType("cluster-1", "extent")
        extsChildrenBefore = None
        if (extsBefore != None):
            extsChildrenBefore = extsBefore.get("context").get("children")
        print("\nCreating a new extent")
        self.executeCmd("extent create", "{\"args\" : \"-d " + storageVolName + " -s 5242880\"}")
        #RESTful API has a bug it does not refresh unless below is done.
        # x = raw_input("Execute 'll' in the extents context in CLI and then Press Enter to continue...")
        x = input("Execute 'll' in the extents context in CLI and then Press Enter to continue...")
        extsAfter = self.getClusterObjectsByType("cluster-1", "extent")
        if (extsAfter != None):
            extsChildrenAfter = extsAfter.get("context").get("children")
        newExtent = None
        for item in extsChildrenAfter:
            if not item in extsChildrenBefore:
                newExtent=item
            break;
        if (newExtent != None):
            print("Created a new extent :", newExtent.get("name"))
        else:
            print("Failed to create extent")
        return newExtent.get("name")
    #########################################################
    # Creates a new device and returns the new device
    #
    # returns device name
    #########################################################
    def createDevice(self, deviceSuffix, geom, extName):
        print("Creating device on extent :", extName)
        deviceName = "device_" + deviceSuffix
        print("\nCreating a new device")
        resp = self.executeCmd("local-device create", "{\"args\" : \"" + deviceName +""+ geom +
        " " + extName + "\"}")
        if(resp != None):
            print("Created a new device :", deviceName)
            return deviceName
        else:
            print("Failed to create device")
        return None
    #########################################################
    # Creates a new virtual-volume and returns the new volume
    #
    # returns volume name
    #########################################################
    def createVirtualVolume(self, deviceName):
        volBefore = self.getClusterObjectsByType("cluster-1", "virtual-volume")
        volChildrenBefore = None
        if (volBefore != None):
            volChildrenBefore = volBefore.get("context").get("children")
        print("\nCreating a new volume")
        self.executeCmd("virtual-volume create", "{\"args\" : \" " + deviceName +"\"}")
        #RESTful API has a bug it does not refresh unless a below is done.
        # x = raw_input("Execute 'll' in the volume context in CLI and then Press Enter to continue...")
        x = input("Execute 'll' in the volume context in CLI and then Press Enter to continue...")
        volAfter = self.getClusterObjectsByType("cluster-1", "virtual-volume")
        if (volAfter != None):
            volChildrenAfter = volAfter.get("context").get("children")
        newVol = None
        for item in volChildrenAfter:
            if not item in volChildrenBefore:
                newVol=item
                break;
        print("Created a new volume :", newVol.get("name"))
        return newVol.get("name")
    #########################################################
    # Auto provision storage.
    # Hardcoded to create create 5 MB extents
    #########################################################
    def autoProvision(self, storageVolName, deviceSuffix):
        storageVolObj = self.getClusterObjectByName("cluster-1", "storage-volume", storageVolName)
        if(storageVolObj == None):
            print("storage-volume '%s' not found." % (storageVolName))
            sys.exit(2)
        attributes = storageVolObj.get("context").get("attributes")
        freeSpace = 0
        usedBy = None
        for item in attributes:
            if item.get("name") == "total-free-space":
                freeSpace = int(item.get("value")[0:-1])  # Will be a String
            elif item.get("name") == "used-by":
                usedBy = item.get("value")  # Will be a python List
        print("Available Space on storage-volume %s : %s Bytes or %.2f GB" % (storageVolName,
                                                                        freeSpace, freeSpace / (1024 * 1024 * 1024)))
        if freeSpace < 5242880:
            print("Provisioning failed. Insufficient space")
            sys.exit(2)
        extName = self.createExtent(storageVolName)
        if (extName == None):
            print("Provisioning failed. Unable to create extent.")
            sys.exit(2)
        devName = self.createDevice(deviceSuffix, "raid-0", extName)
        if (devName == None):
            print("Provisioning failed. Unable to create device.")
            sys.exit(2)
        vol = self.createVirtualVolume(devName)
        if (vol == None):
            print("Provisioning failed. Unable to create vol.")
            sys.exit(2)