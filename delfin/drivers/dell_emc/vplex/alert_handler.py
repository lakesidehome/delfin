# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from oslo_log import log
from delfin.common import constants
from delfin import exception
from delfin.i18n import _

LOG = log.getLogger(__name__)


class AlertHandler(object):
    TIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%fZ"

    OID_SEVERITY = '1.3.6.1.6.3.1.1.4.1.0'
    OID_NODE = '1.3.6.1.4.1.1139.103.1.18.1.1'
    OID_COMPONENT = '1.3.6.1.4.1.1139.21.1.3'
    #OID_SYMPTOMID = '1.3.6.1.4.1.1139.103.1.18.1.3'
    OID_SYMPTOMTEXT = '1.3.6.1.4.1.1139.21.1.4'
    OID_TIMESTAMP = '1.3.6.1.4.1.1139.103.1.18.1.5'

    TRAP_LEVEL_MAP = {'1.3.6.1.4.1.1139.21.0.1':
                          constants.Severity.CRITICAL,
                      '1.3.6.1.4.1.1139.21.0.2':
                          constants.Severity.MAJOR,
                      '1.3.6.1.4.1.1139.21.0.3':
                          constants.Severity.WARNING,
                      '1.3.6.1.4.1.1139.21.0.4':
                          constants.Severity.INFORMATIONAL
                      }

    SECONDS_TO_MS = 1000

    @staticmethod
    def parse_alert(context, alert):
        try:
            alert_model = dict()
            alert_model['alert_id'] = 0
            alert_model['alert_name'] = alert.get(AlertHandler.OID_COMPONENT)
            alert_model['severity'] = AlertHandler.TRAP_LEVEL_MAP.get(
                alert.get(AlertHandler.OID_SEVERITY),
                constants.Severity.INFORMATIONAL)
            alert_model['category'] = constants.Category.FAULT
            alert_model['type'] = constants.EventType.EQUIPMENT_ALARM
            occur_time = int(time.time()) * AlertHandler.SECONDS_TO_MS
            alert_model['occur_time'] = occur_time
            alert_model['description'] = alert.get(AlertHandler.OID_SYMPTOMTEXT)
            alert_model['resource_type'] = constants.DEFAULT_RESOURCE_TYPE
            alert_model['location'] = ''

            return alert_model
        except Exception as e:
            LOG.error(e)
            msg = (_("Failed to build alert model as some attributes missing "
                     "in alert message."))
            raise exception.InvalidResults(msg)
