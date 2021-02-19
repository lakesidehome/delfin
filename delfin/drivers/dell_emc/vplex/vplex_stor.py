# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import alert_util
from delfin.common import constants
from delfin.drivers import driver
#from delfin.drivers.dell_emc.vplex import ssh_handler
from delfin.drivers.dell_emc.vplex import rest_handler
from delfin.drivers.dell_emc.vplex import alert_handler

LOG = log.getLogger(__name__)


class VplexStorageDriver(driver.StorageDriver):
    """VplexStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.rest_handler.login()
        #self.ssh_handler = ssh_handler.SSHHandler(**kwargs)

    def reset_connection(self, context, **kwargs):
        self.rest_handler.verify = kwargs.get('verify', False)

    def get_storage(self, context):
        # storage_map = ssh_handler.get_storage()
        # firmware_version = storage_map.get("firmware_version")
        # model = storage_map.get("model")
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = self.get_resource_names(all_cluster)
        if cluster_name_list:
            for cluster_name in cluster_name_list:
                response = self.rest_handler.get_cluster_by_name_resp(
                    cluster_name)
                map = self.get_attribute_map(response)
                status = self.analyse_status(map.get('operational-status'))
                raw_capacity = self.get_cluster_raw_capacity(cluster_name)
                total_capacity = self.get_cluster_total_capacity(cluster_name)
                used_capacity = self.get_cluster_used_capacity(cluster_name)
                free_capacity = total_capacity - used_capacity
                if free_capacity < 0:
                    free_capacity = 0
                cluster = {
                    'name': cluster_name,
                    'vendor': 'DELL EMC',
                    'description': 'EMC VPlex Storage',
                    'status': status,
                    'serial_number': map.get('top-level-assembly'),
                    'firmware_version': '',
                    'model': '',
                    'location': '',
                    'subscribed_capacity': 0,
                    'raw_capacity': int(raw_capacity),
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity),
                    'subscribed_capacity': 0
                }
                break
        return cluster

    def list_storage_pools(self, context):
        device_list = []
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = self.get_resource_names(all_cluster)
        for cluster_name in cluster_name_list:
            response_device = self.rest_handler.get_devcie_resp(cluster_name)
            map_device_childer = self.get_children_map(response_device)
            for name, type in map_device_childer.items():
                response_dn = self.rest_handler.get_device_by_name_resp(
                    cluster_name, name)
                map_dn_attribute = self.get_attribute_map(response_dn)
                virtual_volume = map_dn_attribute.get("virtual-volume")
                total_capacity_str = map_dn_attribute.get("capacity")
                total_capacity = self.analyse_capacity(total_capacity_str)
                operational_status = map_dn_attribute.get(
                    "operational-status")
                used_capacity = 0
                free_capacity = 0
                if virtual_volume:
                    used_capacity = total_capacity
                else:
                    free_capacity = total_capacity

                device = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'native_storage_pool_id': map_dn_attribute.get(
                        "system-id"),
                    'description': 'EMC VPlex Pool',
                    'status': self.analyse_status(operational_status),
                    'storage_type': constants.StorageType.BLOCK,
                    'total_capacity': int(total_capacity),
                    'used_capacity': int(used_capacity),
                    'free_capacity': int(free_capacity),
                    'subscribed_capacity': 0
                }
                device_list.append(device)
        return device_list

    def list_volumes(self, context):
        vv_list = []
        all_cluster = self.rest_handler.get_cluster_resp()
        cluster_name_list = self.get_resource_names(all_cluster)
        for cluster_name in cluster_name_list:
            resposne_vv = self.rest_handler.get_virtual_volume_resp(
                cluster_name)
            map_vv_children = self.get_children_map(resposne_vv)
            for name, type in map_vv_children.items():
                response_vvn = self.rest_handler.get_storage_volume_by_name_resp(
                    cluster_name, name)
                map_vvn_attribute = self.get_attribute_map(response_vvn)
                thin_capable = map_vvn_attribute.get("thin-capable")
                thin_enabled = map_vvn_attribute.get("thin-enabled")
                operational_status = map_vvn_attribute.get(
                    "operational-status")
                total_capacity = self.analyse_capacity(
                    map_vvn_attribute.get("capacity"))
                vpd_id = map_vvn_attribute.get("vpd-id")
                cells = vpd_id.split(":")
                wwn = ''
                if len(cells) > 1:
                    wwn = cells[1]
                vv = {
                    'name': name,
                    'storage_id': self.storage_id,
                    'description': 'EMC VPlex volume',
                    'status': self.analyse_status(operational_status),
                    'native_volume_id': vpd_id,
                    'native_storage_pool_id': map_vvn_attribute.get(
                        'system-id'),
                    'type': self.analyse_vv_type(thin_capable, thin_enabled),
                    'total_capacity': int(total_capacity),
                    'used_capacity': 0,
                    'free_capacity': 0,
                    'compressed': False,
                    'deduplicated': False,
                    'wwn': wwn
                }
                vv_list.append(vv)
        return vv_list

    def get_cluster_raw_capacity(self, cluster_name):
        raw = 0
        resposne_sv = self.rest_handler.get_storage_volume_resp(cluster_name)
        if resposne_sv is not None:
            map_sv_children = self.get_children_map(resposne_sv)
            for name, type in map_sv_children.items():
                response_svn = self.rest_handler.get_storage_volume_by_name_resp(
                    cluster_name, name)
                map_svn_attribute = self.get_attribute_map(response_svn)
                capacity = map_svn_attribute.get("capacity")
                capacity_int = int(self.analyse_capacity(capacity))
                raw += capacity_int
        return raw

    def get_cluster_total_capacity(self, cluster_name):
        total = 0
        resposne_device = self.rest_handler.get_devcie_resp(cluster_name)
        if resposne_device is not None:
            map_dv_children = self.get_children_map(resposne_device)
            for name, type in map_dv_children.items():
                resposne_dvn = self.rest_handler.get_device_by_name_resp(
                    cluster_name, name)
                map_dvn_attribute = self.get_attribute_map(resposne_dvn)
                capacity = map_dvn_attribute.get("capacity")
                capacity_int = int(self.analyse_capacity(capacity))
                total += capacity_int
        return total

    def get_cluster_used_capacity(self, cluster_name):
        used = 0
        response_vv = self.rest_handler.get_virtual_volume_resp(cluster_name)
        if response_vv is not None:
            map_vv_children = self.get_children_map(response_vv)
            for name, type in map_vv_children.items():
                resposne_vvn = self.rest_handler.get_virtual_volume_by_name_resp(
                    cluster_name, name)
                map_vvn_attribute = self.get_attribute_map(resposne_vvn)
                capacity = map_vvn_attribute.get("capacity")
                capacity_int = int(self.analyse_capacity(capacity))
                used += capacity_int
        return used

    def get_attribute_map(self, response):
        map = {}
        contexts = response.get("context")
        for context in contexts:
            attributes = context.get("attributes")
            for attribute in attributes:
                key = attribute.get("name")
                value = attribute.get("value")
                map[key] = value
        return map

    def get_children_map(self, response):
        map = {}
        contexts = response.get("context")
        for context in contexts:
            childrens = context.get("children")
            for children in childrens:
                name = children.get("name")
                type = children.get("type")
                map[name] = type
        return map

    def get_resource_names(self, response):
        resource_name_list = []
        if response:
            contexts = response.get("context")
            for context in contexts:
                childer_clusters = context.get("children")
                for childer_cluster in childer_clusters:
                    cluster_name = childer_cluster.get("name")
                    resource_name_list.append(cluster_name)
        return resource_name_list

    def analyse_capacity(self, capacity_str):
        capacity = 0
        if capacity_str.strip():
            # capacity_str_encode = capacity_str.encode('gbk')
            # capacity = filter(str.isdigit, capacity_str_encode)
            capacity = re.findall("\d+", capacity_str)[0]
        return capacity

    def analyse_vv_type(self, thin_capable, thin_enabled):
        type = constants.VolumeType.THICK
        if thin_capable == "true":
            if thin_enabled == "available":
                type = constants.VolumeType.THIN
        return type

    def analyse_status(self, status_original):
        status = constants.StorageStatus.OFFLINE
        status_normal = ["ok", "stressed", "starting", "in-service",
                         "completed", "online", "success",
                         "write-protected", "vendor-reserved"]
        if status_original in status_normal:
            status = constants.StorageStatus.NORMAL
        return status

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def list_alerts(self, context, query_para=None):
        pass

    def clear_alert(self, context, alert):
        pass
