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

import json
import six
from oslo_log import log as logging

# from delfin import cryptor
from delfin import exception
# from delfin import ssl_utils
from delfin.drivers.dell_emc.unity import consts
from delfin.drivers.utils.rest_client import RestClient

LOG = logging.getLogger(__name__)


class RestHandler(RestClient):
    BASECONTEXT = '/vplex'
    REST_AUTH_URL = '/vplex/clusters'

    def __init__(self, **kwargs):
        super(RestHandler, self).__init__(**kwargs)

    def call(self, url, data=None, method=None):
        try:
            res = self.do_call(url, data, method,
                               calltimeout=consts.SOCKET_TIMEOUT)
            if (res.status_code == consts.ERROR_SESSION_INVALID_CODE
                    or res.status_code ==
                    consts.ERROR_SESSION_IS_BEING_USED_CODE):
                LOG.error(
                    "Failed to get token=={0}=={1},get it again".format(
                        res.status_code, res.text))
                self.rest_auth_token = None
                access_session = self.login()
                # if get token，Revisit url
                if access_session is not None:
                    res = self. \
                        do_call(url, data, method,
                                calltimeout=consts.SOCKET_TIMEOUT)
                else:
                    LOG.error('Login session is none')
            elif res.status_code == 503:
                raise exception.InvalidResults(res.text)
            return res
        except Exception as e:
            err_msg = "Get restHandler.call failed: %s" % (six.text_type(e))
            LOG.error(err_msg)
            raise e

    def get_rest_info(self, url, data=None, method='GET'):
        result_json = None
        res = self.do_call(url, data, method)
        if res.status_code == 200:
            result_json = res.json()
        return result_json

    def login(self):
        try:
            if self.rest_auth_token is None:
                url = RestHandler.REST_AUTH_URL
                data = {}
                self.init_http_head()
                self.session.headers.update({
                    "username": self.rest_username,
                    # "password": cryptor.decode(self.rest_password)})
                    "password": self.rest_password})
                res = self. \
                    do_call(url, data, 'GET',
                            calltimeout=consts.SOCKET_TIMEOUT)
                if res.status_code != 200:
                    LOG.error("Login error. URL: %(url)s\n"
                              "Reason: %(reason)s.",
                              {"url": url, "reason": res.text})
                    if 'User authentication failed' in res.text:
                        raise exception.InvalidUsernameOrPassword()
                    else:
                        raise exception.BadResponse(res.text)
            else:
                LOG.error('Login Parameter error')
        except Exception as e:
            LOG.error("Login error: %s", six.text_type(e))
            raise e

    def get_cluster_resp(self):
        uri = '%s/clusters' % self.BASECONTEXT
        response = self.get_rest_info(uri)
        # return response
        return self.get_response_obj("GetAllCluster", response)

    def get_cluster_by_name_resp(self, cluster_name):
        url = '%s/clusters/%s' % (self.BASECONTEXT, cluster_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("ClusterByName", response)

    def get_devcie_resp(self, cluster_name):
        url = '%s/clusters/%s/devices' % (self.BASECONTEXT, cluster_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("device", response)

    def get_device_by_name_resp(self, cluster_name, device_name):
        url = '%s/clusters/%s/devices/%s' % (
            self.BASECONTEXT, cluster_name, device_name)
        response = self.get_rest_info(url)
        return self.get_response_obj("devcieByName", response)

    def get_virtual_volume_resp(self, cluster_name):
        url = '%s/clusters/%s/virtual-volumes' % (
            self.BASECONTEXT, cluster_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("virtualVolume", response)

    def get_virtual_volume_by_name_resp(self, cluster_name,
                                        virtual_volume_name):
        url = '%s/clusters/%s/virtual-volumes/%s' % \
              (self.BASECONTEXT, cluster_name, virtual_volume_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("VirtualVolume", response)

    def get_storage_volume_resp(self, cluster_name):
        url = '%s/clusters/%s/storage-elements/storage-volumes' % (
            self.BASECONTEXT, cluster_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("AllStorageVolume", response)

    def get_storage_volume_by_name_resp(self, cluster_name,
                                        storage_volume_name):
        url = '%s/clusters/%s/storage-elements/storage-volumes/%s' % \
              (self.BASECONTEXT, cluster_name, storage_volume_name)
        response = self.get_rest_info(url)
        # return response
        return self.get_response_obj("StorageVolumeByName", response)

    def get_response_obj(self, type, response):
        # if response.status != 200:
        #     print(
        #         "Error getting %s(s) \n Server Response %d %s " % (
        #             type, response.status, response.reason))
        #     return None
        # responseObj = json.loads(response.data)
        # return responseObj.get("response")

        resp = response.get("response")
        return resp
