# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
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
import six

from oslo_log import log as logging
from delfin import exception
from delfin import utils
from delfin.drivers.utils.ssh_client import SSHClient

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    """Common class for Hpe 3parStor storage system."""

    VPLEX_COMMAND_USERLIST = 'user list'
    VPLEX_COMMAND_CHECKHEALTH = 'health-check'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_health_check(self):
        """Check the hardware and software health
           status of the storage system

           return: System is healthy
        """
        re = ''
        try:
            ssh_client = SSHClient(**self.kwargs)
            re = ssh_client.do_exec(
                SSHHandler.VPLEX_COMMAND_CHECKHEALTH)
        except Exception as e:
            LOG.error("Get health state error: %s", six.text_type(e))
            raise e
        return re
