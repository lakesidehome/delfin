import sys

#import ConfigParser
import configparser
import json
import copy
from xml.dom.minidom import Document

import readConfig as readConfig
from pip._vendor.distlib.compat import raw_input

__author__ = "Farooq Khan"
__copyright__ = "Copyright (c) 2012 EMC Corporation"
__version__ = "D20.0.0.0"
__status__ = "Sample Code"

class dict2xml(object):
    doc = Document()
    def __init__(self, structure, sort_keys):
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)
            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName], sort_keys)
    def build(self, father, structure, sort_keys):
        if type(structure) == dict:
            if sort_keys:
                for key in sorted(structure.iterkeys()):
                    tag = self.doc.createElement(key)
                    father.appendChild(tag)
                    self.build(tag, structure[key], sort_keys)
            else:
                for k in structure:
                    tag = self.doc.createElement(k)
                    father.appendChild(tag)
                    self.build(tag, structure[k])
        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            if sort_keys:
                for l in sorted(structure):
                    tag = self.doc.createElement(tagName)
                    self.build(tag, l, sort_keys)
                    grandFather.appendChild(tag)
            else:
                for l in structure:
                    tag = self.doc.createElement(tagName)
                    self.build(tag, l, sort_keys)
                    grandFather.appendChild(tag)
        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)
    def printXML(self, indent):
        print(self.doc.toprettyxml(indent=" "))
class Config:
    def __init__(self, host, port, username, password, outputas):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.outputas = outputas

    #########################################################
    # Pretty Prints the passed JSON Object
    #########################################################
    def printResponse(response, outputas):
        if outputas == "JSON":
            print(json.dumps(response, sort_keys=True, indent=2))
        elif outputas == "XML":
            xml = dict2xml(response, sort_keys=True)
            print(xml.printXML(indent=" "))
        else:
            print( "Error unknow output type :" + outputas)

    def printCommandResponse(response):
        exception = response.get('exception')
        if exception:
            print('Encountered Exception: ' + exception + '\n')
        message = response.get('message')
        if message:
            print('Messages: ' + message + '\n')
        cdata = response.get("custom-data")
        if cdata:
            print(cdata)
    #########################################################
    # Reads the specified ini file and returns the settings.
    #########################################################
    def readConfig(configfilename):
        #config = ConfigParser.RawConfigParser()
        config = configparser.RawConfigParser()
        try:
            with open(configfilename, 'r') as configfile:
                config.readfp(configfile)
        except IOError as e:
            return
        host = None
        port = None
        username = None
        password = None
        outputas = None
        if config.has_section('SERVER'):
            host = config.get('SERVER', 'host')
            port = config.get('SERVER', 'port')
            username = config.get('SERVER', 'username')
            password = config.get('SERVER', 'password')
            if config.has_section('CLIENT'):
                outputas = config.get('CLIENT', 'outputas')
            return Config(host, port, username, password, outputas)

    def readConfigOrFail(configfilename):
        config = readConfig(configfilename)
        if None in (config.host, config.port, config.username, config.password, config.outputas):
            print( 'Missing one or more settngs.\nPlease re-run \"./main.py configuresettings\"')
            sys.exit(2)
        return config

    def promptConfig(prompt, existing):
        xstr = lambda p, e: p + ': ' if e is None else p + '[' + str(e) + ']: '
        first_prompt = 'Please specify ' + xstr(prompt, existing)
        successive_prompt = 'You must specify ' + xstr(prompt, existing)
        setting = raw_input(first_prompt)
        if not setting:
            setting = existing
        count = 0;
        while not setting:
            setting = raw_input(successive_prompt)
            count += 1
            if count == 4:
                print( 'Aborting after too many failed attempts. No changes made to ' + SETTINGS_FILE)
            sys.exit(2)
        return setting


    def writeConfig(configfileName, new_host, new_port, new_username, new_password, new_outputas):
        #config = ConfigParser.RawConfigParser()
        config = configparser.RawConfigParser()
        config.add_section('SERVER')
        config.set('SERVER', 'password', new_password)
        config.set('SERVER', 'username', new_username)
        config.set('SERVER', 'port', new_port)
        config.set('SERVER', 'host', new_host)
        config.add_section('CLIENT')
        config.set('CLIENT', 'outputas', new_outputas)
        with open(configfileName, 'wb') as configfile:
            config.write(configfile)