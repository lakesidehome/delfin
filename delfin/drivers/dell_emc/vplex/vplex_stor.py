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

import time

import six
from oslo_log import log
from oslo_utils import units

from delfin import exception
from delfin.common import alert_util
from delfin.common import constants
from delfin.drivers import driver
from delfin.drivers.dell_emc.vplex import ssh_handler
from delfin.drivers.dell_emc.vplex import rest_handler
from delfin.drivers.dell_emc.vplex import alert_handler

LOG = log.getLogger(__name__)


class VplexStorageDriver(driver.StorageDriver):
    """VplexStorageDriver implement the DELL EMC Storage driver,
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rest_handler = rest_handler.RestHandler(**kwargs)
        self.ssh_handler = ssh_handler.SSHHandler(**kwargs)

    def get_storage(self, context):
        return self.rest_handler.get_all_cluster()

    def list_storage_pools(self, context):
        return self.rest_handler.get_all_device()

    def list_volumes(self, context):
        return self.rest_handler.get_all_virtual_volume()

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return alert_handler.AlertHandler().parse_alert(context, alert)

    def clear_alert(self, context, alert):
        pass
