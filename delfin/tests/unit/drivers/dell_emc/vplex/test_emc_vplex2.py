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
from requests.sessions import Session
from delfin import exception
from delfin import context
from delfin.common import config # noqa
from drivers.dell_emc.vplex.rest_handler import RestHandler
from drivers.dell_emc.vplex.vplex_stor import VplexStorageDriver


class Request:
    def __init__(self):
        self.environ = {'delfin.context': context.RequestContext()}
        pass


VPLEX_STORAGE_CONF = {
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

class TestVplexStorageDriver(TestCase):

    @mock.patch.object(RestHandler, 'get_array_detail')
    @mock.patch.object(RestHandler, 'get_uni_version')
    @mock.patch.object(RestHandler, 'get_unisphere_version')
    def test_init(self, mock_unisphere_version,
                  mock_version, mock_array):
        kwargs = VPLEX_STORAGE_CONF

        mock_version.return_value = ['6.1.0.01.00.13', '90']
        mock_unisphere_version.return_value = ['6.1.0.01.00.13', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}

        driver = VplexStorageDriver(**kwargs)
        self.assertEqual(driver.client.uni_version, '90')
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        with self.assertRaises(Exception) as exc:
            mock_version.side_effect = exception.InvalidIpOrPort
            VplexStorageDriver(**kwargs)
        self.assertIn('Invalid ip or port', str(exc.exception))

        with self.assertRaises(Exception) as exc:
            mock_version.side_effect = exception.InvalidUsernameOrPassword
            VplexStorageDriver(**kwargs)
        self.assertIn('Invalid username or password.', str(exc.exception))

    @mock.patch.object(RestHandler, 'get_all_cluster')
    @mock.patch.object(RestHandler, 'get_vmax_array_details')
    @mock.patch.object(RestHandler, 'get_array_detail')
    @mock.patch.object(RestHandler, 'get_uni_version')
    @mock.patch.object(RestHandler, 'get_unisphere_version')
    def test_get_storage(self, mock_unisphere_version,
                         mock_version, mock_array,
                         mock_array_details, mock_capacity):
        expected = {
            'name': 'cluster-1',
            'vendor': 'Dell EMC',
            'description': '',
            'model': 'VPLEX',
            'firmware_version': '6.1.0.01.00.13',
            'status': 'normal',
            'serial_number': 'FNM00121700047',
            'location': '',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400,
            'raw_capacity': 1610612736000,
            'subscribed_capacity': 0
        }
        system_capacity = {
            'system_capacity': {
                'usable_total_tb': 100,
                'usable_used_tb': 75,
                'subscribed_total_tb': 200
            },
            'physicalCapacity': {
                'total_capacity_gb': 1500

            }
        }
        kwargs = VPLEX_STORAGE_CONF

        mock_version.return_value = ['6.1.0.01.00.13', '90']
        mock_unisphere_version.return_value = ['6.1.0.01.00.13', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_array_details.return_value = {
            'model': 'VPLEX',
            'ucode': '5978.221.221',
            'display_name': 'cluster-1'}
        mock_capacity.return_value = system_capacity

        driver = VplexStorageDriver(**kwargs)

        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        ret = driver.get_storage(context)
        self.assertDictEqual(ret, expected)

        mock_array_details.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            driver.get_storage(context)

        self.assertIn('Failed to get array details from VPLEX',
                      str(exc.exception))

        mock_array_details.side_effect = [{
            'model': 'VPLEX',
            'ucode': '5978.221.221',
            'display_name': 'cluster-1'}]

        mock_capacity.side_effect = exception.StorageBackendException
        with self.assertRaises(Exception) as exc:
            driver.get_storage(context)

        self.assertIn('Failed to get capacity from VPLEX',
                      str(exc.exception))

    @mock.patch.object(RestHandler, 'get_srp_by_name')
    @mock.patch.object(RestHandler, 'get_array_detail')
    @mock.patch.object(RestHandler, 'get_uni_version')
    @mock.patch.object(RestHandler, 'get_unisphere_version')
    def test_list_storage_pools(self, mock_unisphere_version,
                                mock_version,
                                mock_array, mock_srp):
        expected = [{
            'name': 'SRP_1',
            'storage_id': '12345',
            'native_storage_pool_id': 'SRP_ID',
            'description': 'Dell EMC VPLEX Pool',
            'status': 'normal',
            'storage_type': 'block',
            'total_capacity': 109951162777600,
            'used_capacity': 82463372083200,
            'free_capacity': 27487790694400,
            'subscribed_capacity': 219902325555200
        }]
        pool_info = {
            'srp_capacity': {
                'usable_total_tb': 100,
                'usable_used_tb': 75,
                'subscribed_total_tb': 200
            },
            'srpId': 'SRP_ID'
        }
        kwargs = VPLEX_STORAGE_CONF
        mock_version.return_value = ['6.1.0.01.00.13', '90']
        mock_unisphere_version.return_value = ['6.1.0.01.00.13', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_srp.side_effect = [{'srpId': ['SRP_1']}, pool_info]

        driver = VplexStorageDriver(**kwargs)
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        ret = driver.list_storage_pools(context)
        self.assertDictEqual(ret[0], expected[0])

        mock_srp.side_effect = [{'srpId': ['SRP_1']},
                                exception.StorageBackendException]
        with self.assertRaises(Exception) as exc:
            driver.list_storage_pools(context)

        self.assertIn('Failed to get pool metrics from VPLEX',
                      str(exc.exception))

        mock_srp.side_effect = [exception.StorageBackendException, pool_info]
        with self.assertRaises(Exception) as exc:
            driver.list_storage_pools(context)

        self.assertIn('Failed to get pool metrics from VPLEX',
                      str(exc.exception))

    @mock.patch.object(RestHandler, 'get_system_capacity')
    @mock.patch.object(RestHandler, 'get_storage_group')
    @mock.patch.object(RestHandler, 'get_volume')
    @mock.patch.object(RestHandler, 'get_volume_list')
    @mock.patch.object(RestHandler, 'get_array_detail')
    @mock.patch.object(RestHandler, 'get_uni_version')
    @mock.patch.object(RestHandler, 'get_unisphere_version')
    def test_list_volumes(self, mock_unisphere_version,
                          mock_version, mock_array,
                          mock_vols, mock_vol, mock_sg, mock_capacity):
        expected = [{
            'name': 'volume_1',
            'storage_id': '12345',
            'description': "Dell EMC VMAX 'thin device' volume",
            'type': 'thin',
            'status': 'available',
            'native_volume_id': '00001',
            'wwn': 'wwn123',
            'total_capacity': 104857600,
            'used_capacity': 10485760,
            'free_capacity': 94371840,
            'native_storage_pool_id': 'SRP_1',
            'compressed': True
        },
            {
            'name': 'volume_2:id',
            'storage_id': '12345',
            'description': "Dell EMC VMAX 'thin device' volume",
            'type': 'thin',
            'status': 'available',
            'native_volume_id': '00002',
            'wwn': 'wwn1234',
            'total_capacity': 104857600,
            'used_capacity': 10485760,
            'free_capacity': 94371840,
            'native_storage_pool_id': 'SRP_1'
        }]
        volumes = {
            'volumeId': '00001',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn123',
            'num_of_storage_groups': 1,
            'storageGroupId': ['SG_001'],
            'emulation': 'FBA'
        }
        volumes1 = {
            'volumeId': '00002',
            'volume_identifier': 'id',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn1234',
            'num_of_storage_groups': 0,
            'storageGroupId': [],
            'emulation': 'FBA'
        }
        volumes2 = {
            'volumeId': '00003',
            'cap_mb': 100,
            'allocated_percent': 10,
            'status': 'Ready',
            'type': 'TDEV',
            'wwn': 'wwn1234',
            'num_of_storage_groups': 0,
            'storageGroupId': [],
            'emulation': 'CKD'
        }
        storage_group_info = {
            'srp': 'SRP_1',
            'compression': True
        }
        default_srps = {
            'default_fba_srp': 'SRP_1',
            'default_ckd_srp': 'SRP_2'
        }
        kwargs = VPLEX_STORAGE_CONF
        mock_version.return_value = ['6.1.0.01.00.13', '90']
        mock_unisphere_version.return_value = ['6.1.0.01.00.13', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}
        mock_vols.side_effect = [['volume_1', 'volume_2', 'volume_3']]
        mock_vol.side_effect = [volumes, volumes1, volumes2]
        mock_sg.side_effect = [storage_group_info]
        mock_capacity.return_value = default_srps

        driver = VplexStorageDriver(**kwargs)
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")
        ret = driver.list_volumes(context)
        self.assertDictEqual(ret[0], expected[0])
        self.assertDictEqual(ret[1], expected[1])

        mock_vols.side_effect = [['volume_1']]
        mock_vol.side_effect = [volumes]
        mock_sg.side_effect = [exception.StorageBackendException]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VPLEX',
                      str(exc.exception))

        mock_vols.side_effect = [['volume_1']]
        mock_vol.side_effect = [exception.StorageBackendException]
        mock_sg.side_effect = [storage_group_info]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VPLEX',
                      str(exc.exception))

        mock_vols.side_effect = [exception.StorageBackendException]
        mock_vol.side_effect = [volumes]
        mock_sg.side_effect = [storage_group_info]
        with self.assertRaises(Exception) as exc:
            driver.list_volumes(context)

        self.assertIn('Failed to get list volumes from VPLEX',
                      str(exc.exception))

    @mock.patch.object(Session, 'request')
    @mock.patch.object(RestHandler, 'get_array_detail')
    @mock.patch.object(RestHandler, 'get_uni_version')
    @mock.patch.object(RestHandler, 'get_unisphere_version')
    def test_rest(self, mock_unisphere_version,
                  mock_version, mock_array,
                  mock_request):
        kwargs = VPLEX_STORAGE_CONF

        mock_version.return_value = ['6.1.0.01.00.13', '90']
        mock_unisphere_version.return_value = ['6.1.0.01.00.13', '90']
        mock_array.return_value = {'symmetrixId': ['00112233']}

        driver = VplexStorageDriver(**kwargs)
        self.assertEqual(driver.client.uni_version, '90')
        self.assertEqual(driver.storage_id, "12345")
        self.assertEqual(driver.client.array_id, "00112233")

        mock_request.return_value = mock.Mock()
        mock_request.return_value.json = mock.Mock(return_value={})
        driver.reset_connection(context, **kwargs)
        driver.client.rest.session = None
        driver.client.rest.request('/session', 'GET')
        self.assertEqual(driver.client.uni_version, '90')
