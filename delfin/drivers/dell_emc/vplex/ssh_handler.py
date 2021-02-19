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
import paramiko
from oslo_log import log as logging
from delfin import exception
from delfin import utils
from delfin.drivers.utils.ssh_client import SSHPool

LOG = logging.getLogger(__name__)


class SSHHandler(object):
    """Common class for Hpe 3parStor storage system."""

    VPLEX_COMMAND_USERLIST = 'user list'
    VPLEX_COMMAND_CHECKHEALTH = 'health-check'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    SECONDS_TO_MS = 1000
    ALERT_NOT_FOUND_CODE = 'CMMVC8275E'

    def __init__(self, **kwargs):
        self.ssh_pool = SSHPool(**kwargs)

    @staticmethod
    def handle_split(split_str, split_char, arr_number):
        split_value = ''
        if split_str is not None and split_str != '':
            tmp_value = split_str.split(split_char, 1)
            if arr_number == 1 and len(tmp_value) > 1:
                split_value = tmp_value[arr_number].strip()
            elif arr_number == 0:
                split_value = tmp_value[arr_number].strip()
        return split_value

    def login(self):
        try:
            with self.ssh_pool.item() as ssh:
                SSHHandler.do_exec('VPlexcli user list', ssh)
        except Exception as e:
            LOG.error("Failed to login vplex %s" %
                      (six.text_type(e)))
            raise e

    @staticmethod
    def do_exec(command_str, ssh):
        """Execute command"""
        try:
            utils.check_ssh_injection(command_str)
            if command_str is not None and ssh is not None:
                stdin, stdout, stderr = ssh.exec_command(command_str)
                res, err = stdout.read(), stderr.read()
                re = res if res else err
                result = re.decode()
        except paramiko.AuthenticationException as ae:
            LOG.error('doexec Authentication error:{}'.format(ae))
            raise exception.InvalidUsernameOrPassword()
        except Exception as e:
            err = six.text_type(e)
            LOG.error('doexec InvalidUsernameOrPassword error')
            if 'timed out' in err:
                raise exception.SSHConnectTimeout()
            elif 'No authentication methods available' in err \
                    or 'Authentication failed' in err:
                raise exception.InvalidUsernameOrPassword()
            elif 'not a valid RSA private key file' in err:
                raise exception.InvalidPrivateKey()
            else:
                raise exception.SSHException(err)
        return result

    def exec_ssh_command(self, command):
        try:
            with self.ssh_pool.item() as ssh:
                ssh_info = SSHHandler.do_exec(command, ssh)
            return ssh_info
        except Exception as e:
            msg = "Failed to ssh vplex %s: %s" % \
                  (command, six.text_type(e))
            raise exception.SSHException(msg)

    def parse_string(self, value):
        capacity = 0
        if value:
            if value.isdigit():
                capacity = float(value)
            else:
                unit = value[-2:]
                capacity = float(value[:-2]) * int(
                    self.change_capacity_to_bytes(unit))
        return capacity

    def get_storage(self):
        try:
            system_info = self.exec_ssh_command('VPlexcli health-check')
            storage_map = {}
            self.handle_detail(system_info, storage_map, split=':')
            firmware_version = storage_map.get('Product Version')
            model = storage_map.get('Hardware Type')

            stroage_replenish_map = {}
            stroage_replenish_map["firmware_version"] = firmware_version;
            stroage_replenish_map["model"] = model;
            return stroage_replenish_map
        except exception.DelfinException as e:
            err_msg = "Failed to get storage: %s" % (six.text_type(e.msg))
            LOG.error(err_msg)
            raise e
        except Exception as err:
            err_msg = "Failed to get storage: %s" % (six.text_type(err))
            LOG.error(err_msg)
            raise exception.InvalidResults(err_msg)

    def handle_detail(self, deltail_info, detail_map, split):
        detail_arr = deltail_info.split('\n')
        for detail in detail_arr:
            if detail is not None and detail != '':
                strinfo = detail.split(split, 1)
                key = strinfo[0]
                value = ''
                if len(strinfo) > 1:
                    value = strinfo[1]
                detail_map[key] = value







