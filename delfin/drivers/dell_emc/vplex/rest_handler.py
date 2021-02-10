# Copyright 2020 The SODA Authors.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import threading

import requests
import json
import six
import http.client
from oslo_log import log as logging
from delfin import exception
from delfin.common import constants
from delfin.drivers.hitachi.vsp import consts
from delfin.drivers.utils.rest_client import RestClient
from delfin.drivers.dell_emc.vplex.httpapi import HTTPApi

LOG = logging.getLogger(__name__)


class HTTPResponse:
    def __init__(self, status, reason, data):
        self.status = status
        self.reason = reason
        self.data = data


class RestHandler(RestClient):
    BASECONTEXT = '/vplex'

    # def __init__(self, **kwargs):
    #     super(RestHandler, self).__init__(**kwargs)
    #     self.session_lock = threading.Lock()
    #     self.session_id = None
    #     self.storage_device_id = None
    #     self.device_model = None
    #     self.serial_number = None
    def __init__(self, **kwargs):
        rest_access = kwargs.get('rest')
        if rest_access is None:
            raise exception.InvalidInput('Input rest_access is missing')
        self.rest_host = rest_access.get('host')
        self.rest_port = rest_access.get('port')
        self.rest_username = rest_access.get('username')
        self.rest_password = rest_access.get('password')
        self.san_address = 'https://%s:%s' % \
                           (self.rest_host, str(self.rest_port))
        self.session = None
        self.device_id = None
        self.cluster_name = rest_access.get('cluster_name')

        self.verify = kwargs.get('verify', False)
        self.rest_auth_token = None
        self.httpapi = HTTPApi(self.rest_host, self.rest_port, self.rest_username, self.rest_password)
        self.outputas = 'json/xml'  # this can be either json/xml

    def get_all_cluster(self):
        cluster_info = []
        cluster_name_list = self.get_cluster_name();
        if cluster_name_list:
            for cluster_name in cluster_name_list:
                response = self.get_cluster_by_name_resp(cluster_name)
                map = self.get_attribute_map(response)
                cluster = {
                    'name': cluster_name,
                    'description': 'EMC VPlex Storage',
                    'status': map.get('operational-status'),
                    'serial_number': map.get('top-level-assembly'),
                    'firmware_version': '',
                    'location': '',
                    'raw_capacity': '',
                    'total_capacity': '',
                    'used_capacity': '',
                    'free_capacity': ''
                }
                cluster_info.append(cluster)
        return cluster_info

    def get_cluster_resp(self):
        uri = self.BASECONTEXT + "/clusters"
        response = self.httpapi.get(uri)
        return self.getResponseObj("AllCluster", response)

    def get_cluster_by_name_resp(self, cluster_name):
        # cluster_name = self.cluster_name
        url = '/clusters/%s' % \
              (cluster_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("ClusterByName", response)

    def get_all_device(self):
        device_list = []
        cluster_name_list = self.get_cluster_name();
        for cluster_name in cluster_name_list:
            response_device = self.get_devcie_resp(cluster_name)
            map_device_childer = self.get_childern_map(response_device)
            for name, type in map_device_childer.items():
                response_dn = self.get_device_by_name_resp(cluster_name, name)
                map_dn_attribute = self.get_attribute_map(response_dn)

                virtual_volume = map_dn_attribute.get("virtual-volume")
                total_capacity = map_dn_attribute.get("capacity")
                operational_status = map_dn_attribute.get("operational-status")
                used_capacity = 0
                free_capacity = 0
                if virtual_volume:
                    used_capacity = total_capacity
                else:
                    free_capacity = total_capacity

                device = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': map_dn_attribute.get("system-id"),
                    'description': 'EMC VPlex Pool',
                    'status': self.analyse_status(operational_status),
                    'storage_type': constants.StorageType.BLOCK,
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity),
                }
                device_list.append(device)
        return device_list

    def get_devcie_resp(self, cluster_name):
        url = '/clusters/%s/devices' % \
              (cluster_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("device", response)

    def get_device_by_name_resp(self, cluster_name, device_name):
        url = '/clusters/%s/devices/%s' % \
              (cluster_name, device_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("devcieByName", response)

    def get_all_virtual_volume(self):
        vv_list = []
        cluster_name_list = self.get_cluster_name()
        for cluster_name in cluster_name_list:
            resposne_vv = self.get_virtual_volume_resp(cluster_name)
            map_vv_childern = self.get_childern_map(resposne_vv)
            for name, type in map_vv_childern.items():
                response_vvn = self.get_storage_volume_by_name_resp(name)
                map_vvn_attribute = self.get_attribute_map(response_vvn)
                thin_capable = map_vvn_attribute.get("thin-capable")
                thin_enabled = map_vvn_attribute.get("thin-enabled")
                operational_status = map_vvn_attribute.get("operational-status")
                vv = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'description': 'EMC VPlex volume',
                    'status': self.analyse_status(operational_status),
                    'native_volume_id': map_vvn_attribute.get("vpd-id"),
                    'native_storage_pool_id': map_vvn_attribute.get('system-id'),
                    'type': self.analyse_vv_type(thin_capable, thin_enabled),
                    'total_capacity': self.analyse_capacity(map_vvn_attribute.get("capacity")),
                    'used_capacity': 0,
                    'free_capacity': 0,
                    'compressed': False,
                    'deduplicated': False,
                    # 'wwn': ''
                }
                vv_list.append(vv)
        return vv_list

    def get_virtual_volume_resp(self, cluster_name):
        url = '/clusters/%s/virtual-volumes' % \
              (cluster_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("virtualVolume", response)

    def get_virtual_volume_by_name_resp(self, cluster_name, virtual_volume_name):
        url = '/clusters/%s/virtual-volumes/%s' % \
              (cluster_name, virtual_volume_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("VirtualVolume", response)

    def get_all_storage_volume_capacity(self):
        capacity_total = 0
        cluster_name_list = self.get_cluster_name();
        if cluster_name_list:
            for cluster_name in cluster_name_list:
                response_sv = self.get_storage_volume_resp(cluster_name)
                storage_volume_children_list = self.get_childern_map(response_sv)
                for name, type in storage_volume_children_list.items():
                    response_svn = self.get_storage_volume_by_name_resp(cluster_name, name)
                    attribute_map = self.get_attribute_map(response_svn)
                    capacity_original = attribute_map.get("capacity")
                    capacity_current = self.analyse_capacity(capacity_original)
                    capacity_total += capacity_current
        return capacity_total

    def get_storage_volume_resp(self, cluster_name):
        url = '/clusters/%s/storage-elements/storage-volumes' % \
              (cluster_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("AllStorageVolume", response)

    def get_storage_volume_by_name_resp(self, cluster_name, storage_volume_name):
        url = '/clusters/%s/storage-elements/storage-volumes/%s' % \
              (cluster_name, storage_volume_name)
        uri = self.BASECONTEXT + url
        response = self.httpapi.get(uri)
        return self.getResponseObj("StorageVolumeByName", response)

    def getResponseObj(self, type, response):
        if response.status != 200:
            print(
                "Error getting %s(s) \n Server Response %d %s " % (type, response.status, response.reason))
            return None
        responseObj = json.loads(response.data)
        return responseObj.get("response")

    def get_attribute_map(self, response):
        attributes = response.get("context").get("attributes")
        map = {}
        for attribute in attributes:
            key = attribute.get("name")
            value = attributes.get("value")
            map[key] = value
        return map

    def get_childern_map(self, response):
        children = response.get("context").get("children")
        map = {}
        for child in children:
            name = child.get("name")
            type = child.get("type")
            map[name] = type
        return map

    def get_cluster_name(self):
        cluster_name_list = []
        all_cluster = self.getClusterResp()
        if all_cluster:
            childer_clusters = all_cluster.get("context").get("children")
            for childer_cluster in childer_clusters:
                cluster_name = childer_cluster.get("name")
                cluster_name_list.append(cluster_name)
        return cluster_name_list

    def post_rest_info(self, url, data):
        method = "POST"
        # connection = httplib.HTTPSConnection(self.host, self.port)
        connection = http.client.HTTPSConnection(self.host, self.port)
        connection.set_debuglevel(self.debuglvl)
        headers = {"Content-type": "text/json", "username": self.username, "password": self.password}
        connection.request(method, url, data, headers)

        response = connection.getresponse()
        if response.status == 200:
            return HTTPResponse(response.status, response.reason, response.read())
        else:
            return HTTPResponse(response.status, response.reason, None)

    def get_device_id(self):
        try:
            succeed = False
            if self.session is None:
                self.init_http_head()
            storage_systems = self.get_system_info()
            system_info = storage_systems.get('data')
            for system in system_info:
                succeed = True
                if system.get('model') in consts.SUPPORTED_VSP_SERIES:
                    if system.get('ctl1Ip') == self.rest_host or \
                            system.get('ctl2Ip') == self.rest_host:
                        self.storage_device_id = system.get('storageDeviceId')
                        self.device_model = system.get('model')
                        self.serial_number = system.get('serialNumber')
                        break
                elif system.get('svpIp') == self.rest_host:
                    self.storage_device_id = system.get('storageDeviceId')
                    self.device_model = system.get('model')
                    self.serial_number = system.get('serialNumber')
                    break
            if self.storage_device_id is None:
                LOG.error("Get device id fail,model or something is wrong")
            return succeed
        except Exception as e:
            LOG.error("Get device id error: %s", six.text_type(e))
            raise e

    def analyse_capacity(self, capacity_str):
        capacity = 0
        if capacity_str.strip():
            capacity_str_encode = capacity_str.encode('gbk')
            capacity = filter(str.isdigit, capacity_str_encode)
        return capacity

    def analyse_vv_type(self, thin_capable, thin_enabled):
        type = constants.VolumeType.THICK
        if thin_capable == "true":
            if thin_enabled == "available":
                type = constants.VolumeType.THIN
        return type

    def analyse_status(self, status_original):
        status = constants.StorageStatus.OFFLIN
        status_normal = ["ok", "stressed", "starting", "in-service", "completed", "online", "success",
                         "write-protected", "vendor-reserved"]
        if status_original in status_normal:
            status = constants.StorageStatus.NORMAL
        return status
