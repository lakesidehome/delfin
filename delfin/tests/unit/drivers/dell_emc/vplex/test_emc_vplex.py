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

from unittest import TestCase, mock
from requests import Session
from delfin import context
from delfin.drivers.dell_emc.vplex.rest_handler import RestHandler
from delfin.drivers.dell_emc.vplex.vplex_stor import VplexStorageDriver

class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "dell_emc",
    "model": "vplex",
    "rest": {
        "host": "8.44.162.250",
        "port": 443,
        "username": "service",
        "password": "Huawei@123"
    },
    "extra_attributes": {
        "array_id": "00112233"
    }
}
GET_STORAGE = {
    "response": {
        "context": [
            {
                "type": "cluster",
                "parent": "/clusters",
                "attributes": [
                    {
                        "name": "allow-auto-join",
                        "value": "true"
                    },
                    {
                        "name": "auto-expel-count",
                        "value": "0"
                    },
                    {
                        "name": "auto-expel-period",
                        "value": "0"
                    },
                    {
                        "name": "auto-join-delay",
                        "value": "0"
                    },
                    {
                        "name": "cluster-id",
                        "value": "1"
                    },
                    {
                        "name": "connected",
                        "value": "true"
                    },
                    {
                        "name": "default-cache-mode",
                        "value": "synchronous"
                    },
                    {
                        "name": "default-caw-template",
                        "value": "true"
                    },
                    {
                        "name": "default-director",
                        "value": "director-1-2-B"
                    },
                    {
                        "name": "default-write-same-16-template",
                        "value": "true"
                    },
                    {
                        "name": "default-xcopy-template",
                        "value": "true"
                    },
                    {
                        "name": "director-names",
                        "value": [
                            "director-1-2-B",
                            "director-1-1-A",
                            "director-1-1-B",
                            "director-1-2-A"
                        ]
                    },
                    {
                        "name": "health-indications",
                        "value": [
                            "engine-1-2 : director-1-2-B : B2-FC : The specified device is in a degraded state. ",
                            "engine-1-1 : director-1-1-A : stand-by-power-supply-A : The specified FRU is not present. ",
                            "engine-1-2 : director-1-2-A : stand-by-power-supply-A : The specified FRU is not present. ",
                            "86 unhealthy Devices or storage-volumes",
                            "storage-volume unreachable",
                            "engine-1-1 : director-1-1-B : stand-by-power-supply-B : The specified FRU is not present. "
                        ]
                    },
                    {
                        "name": "health-state",
                        "value": "major-failure"
                    },
                    {
                        "name": "island-id",
                        "value": "1"
                    },
                    {
                        "name": "name",
                        "value": "cluster-1"
                    },
                    {
                        "name": "operational-status",
                        "value": "degraded"
                    },
                    {
                        "name": "top-level-assembly",
                        "value": "FNM00121700047"
                    },
                    {
                        "name": "transition-indications",
                        "value": [
                            "disk(s) not visible from all directors"
                        ]
                    },
                    {
                        "name": "transition-progress",
                        "value": []
                    }
                ],
                "children": [
                    {
                        "name": "connectivity",
                        "type": "connectivity"
                    },
                    {
                        "name": "consistency-groups",
                        "type": "consistency-groups"
                    },
                    {
                        "name": "devices",
                        "type": "devices"
                    },
                    {
                        "name": "exports",
                        "type": "exports"
                    },
                    {
                        "name": "performance-policies",
                        "type": "performance-policies"
                    },
                    {
                        "name": "storage-elements",
                        "type": "storage-elements"
                    },
                    {
                        "name": "system-volumes",
                        "type": "system-volumes"
                    },
                    {
                        "name": "uninterruptible-power-supplies",
                        "type": "uninterruptible-power-supplies"
                    },
                    {
                        "name": "virtual-volumes",
                        "type": "virtual-volumes"
                    }
                ]
            }
        ],
        "message": '',
        "exception": '',
        "custom-data": ''
    }
}
GET_ALL_CLUSTER = {
    "response": {
        "context": [
            {
                "type": "clusters",
                "parent": "/",
                "attributes": [
                    {
                        "name": "name",
                        "value": "clusters"
                    }
                ],
                "children": [
                    {
                        "name": "cluster-1",
                        "type": "cluster"
                    }
                ]
            }
        ],
        "message": "",
        "exception": "",
        "custom-data": ""
    }
}
GET_CLUSTER = {
    "response": {
        "context": [
            {
                "type": "cluster",
                "parent": "/clusters",
                "attributes": [
                    {
                        "name": "cluster-id",
                        "value": "1"
                    },
                    {
                        "name": "connected",
                        "value": "true"
                    },
                    {
                        "name": "health-state",
                        "value": "major-failure"
                    },
                    {
                        "name": "name",
                        "value": "cluster-1"
                    },
                    {
                        "name": "operational-status",
                        "value": "degraded"
                    },
                    {
                        "name": "top-level-assembly",
                        "value": "FNM00121700047"
                    },
                    {
                        "name": "transition-indications",
                        "value": [
                            "disk(s) not visible from all directors"
                        ]
                    },
                    {
                        "name": "transition-progress",
                        "value": []
                    }
                ],
                "children": [
                    {
                        "name": "devices",
                        "type": "devices"
                    },
                    {
                        "name": "storage-elements",
                        "type": "storage-elements"
                    },
                    {
                        "name": "system-volumes",
                        "type": "system-volumes"
                    },
                    {
                        "name": "virtual-volumes",
                        "type": "virtual-volumes"
                    }
                ]
            }
        ],
        "message": "",
        "exception": "",
        "custom-data": ""
    }
}
GET_ALL_STORAGE_VOLUME = {
    "response": {
        "context": [
            {
                "type": "storage-volumes",
                "parent": "/clusters/cluster-1/storage-elements",
                "attributes": [
                    {
                        "name": "name",
                        "value": "storage-volumes"
                    }
                ],
                "children": [
                    {
                        "name": "VPD83T3:6006016028f036006984a47112b0e911",
                        "type": "storage-volume"
                    }
                ]
            }
        ],
        "message": None,
        "exception": None,
        "custom-data": None
    }
}
GET_STORAGE_VOLUME = {
    "response": {
        "context": [
            {
                "type": "storage-volume",
                "parent": "/clusters/cluster-1/storage-elements/storage-volumes",
                "attributes": [
                    {
                        "name": "application-consistent",
                        "value": "false"
                    },
                    {
                        "name": "block-count",
                        "value": "26214144"
                    },
                    {
                        "name": "block-size",
                        "value": "4096B"
                    },
                    {
                        "name": "capacity",
                        "value": "907373133824B"
                    },
                    {
                        "name": "description",
                        "value": None
                    },
                    {
                        "name": "free-chunks",
                        "value": []
                    },
                    {
                        "name": "health-indications",
                        "value": []
                    },
                    {
                        "name": "health-state",
                        "value": "ok"
                    },
                    {
                        "name": "io-status",
                        "value": "alive"
                    },
                    {
                        "name": "largest-free-chunk",
                        "value": None
                    },
                    {
                        "name": "locality",
                        "value": None
                    },
                    {
                        "name": "name",
                        "value": "VPD83T3:6006016028f036006984a47112b0e911"
                    },
                    {
                        "name": "operational-status",
                        "value": "ok"
                    },
                    {
                        "name": "provision-type",
                        "value": "legacy"
                    },
                    {
                        "name": "storage-array-family",
                        "value": "clariion"
                    },
                    {
                        "name": "storage-array-name",
                        "value": "EMC-CLARiiON-CETV2135000041"
                    },
                    {
                        "name": "storage-volumetype",
                        "value": "traditional"
                    },
                    {
                        "name": "system-id",
                        "value": "VPD83T3:6006016028f036006984a47112b0e911"
                    },
                    {
                        "name": "thin-capable",
                        "value": "true"
                    },
                    {
                        "name": "thin-rebuild",
                        "value": "false"
                    },
                    {
                        "name": "total-free-space",
                        "value": None
                    },
                    {
                        "name": "underlying-storage-block-size",
                        "value": "512"
                    },
                    {
                        "name": "use",
                        "value": "meta-data"
                    },
                    {
                        "name": "used-by",
                        "value": [
                            "metadata_VNX5400_3PAR"
                        ]
                    },
                    {
                        "name": "vendor-specific-name",
                        "value": "DGC"
                    }
                ],
                "children": []
            }
        ],
        "message": None,
        "exception": None,
        "custom-data": None
    }
}
GET_ALL_POOLS = {
    "response": {
        "context": [
            {
                "type": "devices",
                "parent": "/clusters/cluster-1",
                "attributes": [
                    {
                        "name": "name",
                        "value": "devices"
                    }
                ],
                "children": [
                    {
                        "name": "Device_CLARiiON0041_KLM_test01",
                        "type": "local-device"
                    }
                ]
            }
        ],
        "message": None,
        "exception": None,
        "custom-data": None
    }
}
GET_POOL = {
    "response": {
        "context": [
            {
                "type": "local-device",
                "parent": "/clusters/cluster-1/devices",
                "attributes": [
                    {
                        "name": "application-consistent",
                        "value": "false"
                    },
                    {
                        "name": "auto-resume",
                        "value": ''
                    },
                    {
                        "name": "block-count",
                        "value": "7864320"
                    },
                    {
                        "name": "block-offset",
                        "value": "0"
                    },
                    {
                        "name": "block-size",
                        "value": "4096B"
                    },
                    {
                        "name": "capacity",
                        "value": "732212254720B"
                    },
                    {
                        "name": "geometry",
                        "value": "raid-0"
                    },
                    {
                        "name": "health-indications",
                        "value": []
                    },
                    {
                        "name": "health-state",
                        "value": "ok"
                    },
                    {
                        "name": "locality",
                        "value": "local"
                    },
                    {
                        "name": "name",
                        "value": "Device_CLARiiON0041_KLM_test01"
                    },
                    {
                        "name": "operational-status",
                        "value": "ok"
                    },
                    {
                        "name": "rebuild-allowed",
                        "value": ''
                    },
                    {
                        "name": "rebuild-eta",
                        "value": ''
                    },
                    {
                        "name": "rebuild-progress",
                        "value": ''
                    },
                    {
                        "name": "rebuild-status",
                        "value": ''
                    },
                    {
                        "name": "rebuild-type",
                        "value": ''
                    },
                    {
                        "name": "rule-set-name",
                        "value": ''
                    },
                    {
                        "name": "service-status",
                        "value": "running"
                    },
                    {
                        "name": "storage-array-family",
                        "value": "clariion"
                    },
                    {
                        "name": "stripe-depth",
                        "value": "4096B"
                    },
                    {
                        "name": "system-id",
                        "value": "Device_CLARiiON0041_KLM_test01"
                    },
                    {
                        "name": "thin-capable",
                        "value": "false"
                    },
                    {
                        "name": "transfer-size",
                        "value": ''
                    },
                    {
                        "name": "virtual-volume",
                        "value": "Volume_CLARiiON0041_KLM_test01"
                    },
                    {
                        "name": "visibility",
                        "value": "local"
                    }
                ],
                "children": [
                    {
                        "name": "components",
                        "type": "components"
                    }
                ]
            }
        ],
        "message": '',
        "exception": '',
        "custom-data": ''
    }
}
GET_ALL_LUNS = {
    "response": {
        "context": [
            {
                "type": "virtual-volumes",
                "parent": "/clusters/cluster-1",
                "attributes": [
                    {
                        "name": "name",
                        "value": "virtual-volumes"
                    }
                ],
                "children": [
                    {
                        "name": "device_CLAIM_CL_6800V3_VPLEX_LUN0_1_vol",
                        "type": "virtual-volume"
                    }
                ]
            }
        ],
        "message": "",
        "exception": "",
        "custom-data": ""
    }
}
GET_LUN = {
    "response": {
        "context": [
            {
                "type": "virtual-volume",
                "parent": "/clusters/cluster-1/virtual-volumes",
                "attributes": [
                    {
                        "name": "block-count",
                        "value": "157286400"
                    },
                    {
                        "name": "block-size",
                        "value": "4096B"
                    },
                    {
                        "name": "cache-mode",
                        "value": "synchronous"
                    },
                    {
                        "name": "capacity",
                        "value": "644245094400B"
                    },
                    {
                        "name": "consistency-group",
                        "value": ''
                    },
                    {
                        "name": "expandable",
                        "value": "true"
                    },
                    {
                        "name": "expandable-capacity",
                        "value": "0B"
                    },
                    {
                        "name": "expansion-method",
                        "value": "storage-volume"
                    },
                    {
                        "name": "expansion-status",
                        "value": ''
                    },
                    {
                        "name": "health-indications",
                        "value": []
                    },
                    {
                        "name": "health-state",
                        "value": "ok"
                    },
                    {
                        "name": "initialization-status",
                        "value": ''
                    },
                    {
                        "name": "locality",
                        "value": "local"
                    },
                    {
                        "name": "name",
                        "value": "device_CLAIM_CL_6800V3_VPLEX_LUN0_1_vol"
                    },
                    {
                        "name": "operational-status",
                        "value": "ok"
                    },
                    {
                        "name": "recoverpoint-protection-at",
                        "value": []
                    },
                    {
                        "name": "recoverpoint-usage",
                        "value": ''
                    },
                    {
                        "name": "scsi-release-delay",
                        "value": "0"
                    },
                    {
                        "name": "service-status",
                        "value": "running"
                    },
                    {
                        "name": "storage-array-family",
                        "value": "other"
                    },
                    {
                        "name": "storage-tier",
                        "value": ''
                    },
                    {
                        "name": "supporting-device",
                        "value": "device_CLAIM_CL_6800V3_VPLEX_LUN0_1"
                    },
                    {
                        "name": "system-id",
                        "value": "device_CLAIM_CL_6800V3_VPLEX_LUN0_1_vol"
                    },
                    {
                        "name": "thin-capable",
                        "value": "false"
                    },
                    {
                        "name": "thin-enabled",
                        "value": "unavailable"
                    },
                    {
                        "name": "volume-type",
                        "value": "virtual-volume"
                    },
                    {
                        "name": "vpd-id",
                        "value": "VPD83T3:60001440000000103029208322b81b8c"
                    }
                ],
                "children": []
            }
        ],
        "message": '',
        "exception": '',
        "custom-data": ''
    }
}
GET_ALL_LUNS_NULL = {
    "response": {
        "context": [
            {
                "type": "virtual-volume",
                "parent": "/clusters/cluster-1/virtual-volumes",
                "attributes": [],
                "children": []
            }
        ],
        "message": '',
        "exception": '',
        "custom-data": ''
    }
}
GET_CAPACITY = {
    "response": {
        "context": [
            {
                "type": "storage-volume",
                "parent": "/clusters/cluster-1/storage-elements/storage-volumes",
                "attributes": [
                    {
                        "name": "application-consistent",
                        "value": "false"
                    },
                    {
                        "name": "block-count",
                        "value": "26214144"
                    },
                    {
                        "name": "block-size",
                        "value": "4096B"
                    },
                    {
                        "name": "capacity",
                        "value": "107373133824B"
                    },
                    {
                        "name": "description",
                        "value": ''
                    },
                    {
                        "name": "free-chunks",
                        "value": []
                    },
                    {
                        "name": "health-indications",
                        "value": []
                    },
                    {
                        "name": "health-state",
                        "value": "ok"
                    },
                    {
                        "name": "io-status",
                        "value": "alive"
                    },
                    {
                        "name": "itls",
                        "value": [
                            "0x500014429029e910/0x500601690864241e/0",
                            "0x500014429029e912/0x500601610864241e/0",
                            "0x500014429029e912/0x500601690864241e/0",
                            "0x500014429029e910/0x500601610864241e/0",
                            "0x5000144280292012/0x500601610864241e/0",
                            "0x5000144280292012/0x500601690864241e/0",
                            "0x5000144280292010/0x500601690864241e/0",
                            "0x5000144280292010/0x500601610864241e/0",
                            "0x500014428029e910/0x500601690864241e/0",
                            "0x500014428029e912/0x500601610864241e/0",
                            "0x500014428029e910/0x500601610864241e/0",
                            "0x500014428029e912/0x500601690864241e/0",
                            "0x5000144290292010/0x500601690864241e/0",
                            "0x5000144290292012/0x500601610864241e/0",
                            "0x5000144290292012/0x500601690864241e/0",
                            "0x5000144290292010/0x500601610864241e/0"
                        ]
                    },
                    {
                        "name": "largest-free-chunk",
                        "value": ''
                    },
                    {
                        "name": "locality",
                        "value": ''
                    },
                    {
                        "name": "name",
                        "value": "VPD83T3:6006016028f036006984a47112b0e911"
                    },
                    {
                        "name": "operational-status",
                        "value": "ok"
                    },
                    {
                        "name": "provision-type",
                        "value": "legacy"
                    },
                    {
                        "name": "storage-array-family",
                        "value": "clariion"
                    },
                    {
                        "name": "storage-array-name",
                        "value": "EMC-CLARiiON-CETV2135000041"
                    },
                    {
                        "name": "storage-volumetype",
                        "value": "traditional"
                    },
                    {
                        "name": "system-id",
                        "value": "VPD83T3:6006016028f036006984a47112b0e911"
                    },
                    {
                        "name": "thin-capable",
                        "value": "true"
                    },
                    {
                        "name": "thin-rebuild",
                        "value": "false"
                    },
                    {
                        "name": "total-free-space",
                        "value": ''
                    },
                    {
                        "name": "underlying-storage-block-size",
                        "value": "512"
                    },
                    {
                        "name": "use",
                        "value": "meta-data"
                    },
                    {
                        "name": "used-by",
                        "value": [
                            "metadata_VNX5400_3PAR"
                        ]
                    },
                    {
                        "name": "vendor-specific-name",
                        "value": "DGC"
                    }
                ],
                "children": []
            }
        ],
        "message": '',
        "exception": '',
        "custom-data": ''
    }
}
TRAP_INFO = {
    "1.3.6.1.2.1.1.3.0": "0",
    '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.1139.21.0',
    '1.3.6.1.4.1.1139.21.1.4': 'this is test',
    '1.3.6.1.4.1.1139.21.1.3': 'test'
}
ALERT_INFO = [
    {
        'location': "test",
        'alertId': '223232',
        'alertIndex': '1111111',
        'errorDetail': 'test alert',
        'errorSection': 'someting wrong',
        'occurenceTime': '2021-02-10T10:10:10',
        'errorLevel': 'Serious'
    }
]
storage_result = {
    'name': 'cluster-1',
    'vendor': 'DELL EMC',
    'description': 'EMC VPlex Storage',
    'status': 'offline',
    'serial_number': 'FNM00121700047',
    'firmware_version': '',
    'model': '',
    'location': '',
    'subscribed_capacity': 0,
    'raw_capacity': 907373133824,
    'total_capacity': 732212254720,
    'used_capacity': 644245094400,
    'free_capacity': 87967160320
}
pool_result = [
    {
        'name': 'Device_CLARiiON0041_KLM_test01',
        'storage_id': '12345',
        'native_storage_pool_id': 'Device_CLARiiON0041_KLM_test01',
        'description': 'EMC VPlex Pool',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 732212254720,
        'used_capacity': 732212254720,
        'free_capacity': 0,
        'subscribed_capacity': 0
    }
]
volume_result = [
    {
        'name': 'device_CLAIM_CL_6800V3_VPLEX_LUN0_1_vol',
        'storage_id': '12345',
        'description': 'EMC VPlex volume',
        'status': 'normal',
        'native_volume_id': 'VPD83T3:60001440000000103029208322b81b8c',
        'native_storage_pool_id': 'device_CLAIM_CL_6800V3_VPLEX_LUN0_1_vol',
        'type': 'thick',
        'total_capacity': 644245094400,
        'used_capacity': 0,
        'free_capacity': 0,
        'compressed': False,
        'deduplicated': False,
        'wwn': '60001440000000103029208322b81b8c'
    }
]
trap_result = {
    'alert_id': 'ddddddd',
    'alert_name': 'test',
    'severity': 'Critical',
    'category': 'Fault',
    'type': 'EquipmentAlarm',
    'occur_time': 1605852610000,
    'description': 'this is test',
    'resource_type': 'Storage',
    'location': 'eeeeeeeee'
}

def create_driver():
    kwargs = ACCESS_INFO
    m = mock.MagicMock(status_code=200)
    with mock.patch.object(Session, 'get', return_value=m):
        m.raise_for_status.return_value = 200
        return VplexStorageDriver(**kwargs)

class TestVplexStorDriver(TestCase):
    driver = create_driver()

    def test_initrest(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 200
            kwargs = ACCESS_INFO
            re = RestHandler(**kwargs)
            self.assertIsNotNone(re)

    def test_get_storage(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_ALL_CLUSTER, GET_CLUSTER, GET_ALL_STORAGE_VOLUME,
                         GET_STORAGE_VOLUME, GET_ALL_POOLS, GET_POOL,
                         GET_ALL_LUNS, GET_LUN])
        storage = self.driver.get_storage(context)
        self.assertDictEqual(storage, storage_result)

    def test_list_storage_pools(self):
        RestHandler.get_rest_info = mock.Mock(
            side_effect=[GET_ALL_CLUSTER, GET_ALL_POOLS, GET_POOL])
        pool = self.driver.list_storage_pools(context)
        self.assertDictEqual(pool[0], pool_result[0])

    def test_list_volumes(self):
        RestHandler.get_rest_info = mock.Mock(side_effect=[
            GET_ALL_CLUSTER, GET_ALL_LUNS, GET_LUN])
        volume = self.driver.list_volumes(context)
        self.assertDictEqual(volume[0], volume_result[0])

    def test_parse_alert(self):
        trap = self.driver.parse_alert(context, TRAP_INFO)
        self.assertEqual(trap.get('alert_id'), trap_result.get('alert_id'))

    def test_rest_close_connection(self):
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'post', return_value=m):
            m.raise_for_status.return_value = 200
            m.json.return_value = None
            re = self.driver.close_connection()
            self.assertIsNone(re)

    def test_rest_handler_call(self):
        m = mock.MagicMock(status_code=403)
        with self.assertRaises(Exception) as exc:
            with mock.patch.object(Session, 'get', return_value=m):
                m.raise_for_status.return_value = 403
                m.json.return_value = None
                url = 'http://test'
                self.driver.rest_handler.call(url, '', 'GET')
        self.assertIn('Bad response from server', str(exc.exception))

    def test_reset_connection(self):
        RestHandler.logout = mock.Mock(return_value={})
        m = mock.MagicMock(status_code=200)
        with mock.patch.object(Session, 'get', return_value=m):
            m.raise_for_status.return_value = 201
            kwargs = ACCESS_INFO
            re = self.driver.reset_connection(context, **kwargs)
            self.assertIsNone(re)
