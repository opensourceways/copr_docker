#!/usr/bin/python3
import argparse
import json
import logging
import os
import requests
import sys
import time
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# init logger
logger = logging.getLogger(__name__)

# init retry
retries = Retry(total=3, backoff_factor=0.1)
session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=retries))
timeout = 5

@dataclass
class ServerCreateConfig:
    """服务器创建配置参数"""
    key_name: str
    count: int
    flavorRef: str
    imageRef: str
    name: str
    vpcid: str
    subnet_id: str
    security_group_id: str
    volumetype: str
    user_data: Optional[str] = None  # 可选参数可设置默认值

class ECSServers(object):
    """
    wrapped HUAWEI CLOUD ECS Servers APIs
    """

    def __init__(self, conf_path):
        super(ECSServers, self).__init__()
        self.conf_path = conf_path
        info = {}
        try:
            with open(self.conf_path, 'r', encoding='utf-8') as fp:
                info = yaml.safe_load(fp)
        except yaml.MarkedYAMLError as e1:
            logger.error(e1)
        except FileNotFoundError as e2:
            logger.error(e2)
        if info:
            self.region = info.get('region')
            self.project_id = info.get('projectId')
            self.headers = self.get_auth_header(self.region)
            self.name_prefix = info.get('name_prefix')
            self.vpcId = info.get('vpcId')
            self.subnetId = info.get('subnetId')
            self.security_group_id = info.get('security_group_id')
            self.volumetype = info.get('volumetype')
            self.waiting_time = info.get('waiting_time')
            self.query_times = info.get('query_times')
            self.server_boot_time = info.get('server_boot_time')
            self.max_servers_number = info.get('max_servers_number')
            self.max_list_number = info.get('max_list_number')
            self.flavorMapping = info.get('flavorMapping')
            self.archMapping = info.get('archMapping')
            self.key_name = info.get('key_name')
            self.user_data = info.get('user_data')

    @staticmethod
    def get_auth_header(project_region):
        """
        Get authorization header
        :param project_region: region of project
        :return: authorized header
        """
        url = os.getenv("AUTH_URL", "https://iam.myhuaweicloud.com/v3/auth/tokens")
        data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": os.getenv("IAM_DOMAIN", "")
                            },
                            "name": os.getenv("IAM_USER", ""),
                            "password": os.getenv("IAM_PASSWORD", "")
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": project_region
                    }
                }
            }
        }
        response = session.post(url, data=json.dumps(data), timeout=timeout)
        try:
            token = response.headers["X-Subject-Token"]
            header = {'X-Auth-Token': token}
            logger.info('Get authorized header: Successful')
            return header
        except KeyError:
            logger.error(f'Get authorized token: Fail to get auth token, ret: {response.status_code} msg: {response.json()}')
            raise

    @staticmethod
    def get_create_data(config: ServerCreateConfig) -> Dict[str, Any]:
        """通过具名配置对象生成服务器创建数据"""
        return {
            'server': {
                'count': config.count,
                'key_name': config.key_name,
                'flavorRef': config.flavorRef,
                'imageRef': config.imageRef,
                'name': config.name,
                'user_data': config.user_data,
                'nics': [{'subnet_id': config.subnet_id}],
                'root_volume': {'volumetype': config.volumetype},
                'security_groups': [{'id': config.security_group_id}],
                'vpcid': config.vpcid
            }
        }

    def validate_create_fields(self, arch, flavor_level, count):
        """
        Validation of the created fields
        :param arch: architecture of servers
        :param flavor_level: specifies the flavor level of servers
        :param count: numbers of servers
        :return:
        """
        if arch not in self.flavorMapping.keys():
            result = {'code': 400, 'error': 'Unmatched architecture name.'}
            logger.error('Create servers: {}'.format(result))
            return result
        if flavor_level not in ['l1', 'l2', 'l3']:
            result = {'code': 400, 'error': 'The flavor_level must be one of ["l1", "l2", "l3"].'}
            logger.error('Create servers: {}'.format(result))
            return result
        if not (isinstance(count, int) and count > 0):
            result = {'code': 400, 'error': 'The count must be a positive integer.'}
            logger.error('Create servers: {}'.format(result))
            return result
        max_number_can_create = self.get_max_number_can_create()
        if max_number_can_create == 0:
            result = {'code': 400, 'error': 'Cannot get maximum number of servers that can be created.'}
            logger.error('Create servers: {}'.format(result))
            return result
        if count > max_number_can_create:
            result = {'code': 400, 'error': 'Exceeds maximum number of servers that can be created.'}
            logger.error('Create servers: {}'.format(result))
            return result

        return None

    def create_servers(self, arch, flavor_level, name, count=1):
        """
        Create servers
        :param arch: architecture of servers
        :param flavor_level: specifies the flavor level of servers
        :param count: numbers of servers
        :return: a list of IP address of the available servers
        """
        start_time = time.time()
        logger.info("Starting create_servers method")

        result = self.validate_create_fields(arch, flavor_level, count)
        if result:
            end_time = time.time()
            logger.info(f"validate_create_fields took {end_time - start_time:.2f} seconds")
            return result
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers'.format(self.region, self.project_id)
        try:
            start_time = time.time()
            flavorRef = self.flavorMapping.get(arch).get(flavor_level)
            imageRef = self.flavorMapping.get(arch).get('imageRef')
            end_time = time.time()
            logger.info(f"Flavor and Image reference lookup took {end_time - start_time:.2f} seconds")
        except AttributeError as e:
            logger.error(e)
            result = {'code': 400, 'error': e}
            return result

        if name is None:
            result = {'code': 400, 'error': 'The name of server cannot be empty.'}
            return result

        vpcid = self.vpcId
        subnet_id = self.subnetId
        security_group_id = self.security_group_id
        volumetype = self.volumetype
        waiting_time = self.waiting_time
        query_times = self.query_times
        server_boot_time = self.server_boot_time
        config = ServerCreateConfig(
            key_name = self.key_name,
            count = count,
            flavorRef = flavorRef,
            imageRef = imageRef,
            name = name,
            vpcid = vpcid,
            subnet_id = subnet_id,
            security_group_id = security_group_id,
            volumetype = volumetype,
            user_data = self.user_data
        )

        start_time = time.time()
        data = self.get_create_data(config)
        end_time = time.time()
        logger.info(f"Preparing create data took {end_time - start_time:.2f} seconds")

        start_time = time.time()
        response = session.post(url, headers=self.headers, data=json.dumps(data), timeout=timeout)
        end_time = time.time()
        logger.info(f"POST request to ECS API took {end_time - start_time:.2f} seconds")

        if response.status_code == 200:
            serverIds = response.json()['serverIds']
            total_queries = query_times  # 记录总查询次数
            loop_count = 0  # 记录当前循环次数

            while query_times > 0:
                start_time = time.time()  # 记录循环开始时间
                server_ips = self.get_server_ips(serverIds)
                elapsed_time = time.time() - start_time  # 计算循环耗时
                loop_count += 1  # 增加循环计数

                if len(server_ips) == len(serverIds):
                    result = {'code': 200, 'server_ips': server_ips}
                    logger.info(f'Create servers: {result}')
                    logger.info(f'Loop exited on attempt {loop_count} out of {total_queries}')
                    logger.info(f'Time spent in last loop: {elapsed_time} seconds')
                    # return after servers startup
                    time.sleep(server_boot_time)
                    return result
                else:
                    query_times -= 1
                    logger.info(f'Attempt {loop_count} failed, {query_times} attempts left, time spent in loop: {elapsed_time} seconds, waiting for {waiting_time} seconds')
                    time.sleep(waiting_time)
        else:
            result = {'code': 400, 'error': response.content}
            logger.error('Create servers: {}'.format(result))
            return result

    def get_format_server(self, server, status='ACTIVE'):
        """
        Get formatted data of a server
        :param server: a dict of server data
        :param status: running status of the server
        :return: a dict contained id, name, ip, status, flavor and arch
        """
        format_server = {
            'id': server.get('id'),
            'name': server.get('name'),
            'ip': server.get('addresses').get(list(server.get('addresses').keys())[0])[0].get('addr') if server.get(
                'addresses') else '',
            'status': status,
            'flavor': {
                'vcpus': server.get('flavor').get('vcpus'),
                'ram': server.get('flavor').get('ram')
            },
            'arch': self.get_arch(server.get('flavor').get('name'))
        }
        return format_server

    def list_servers(self):
        """
        List all active servers about obs
        :return: a list of all server details
        """
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/detail?limit={}&status=ACTIVE&name={}'.format(
            self.region, self.project_id, self.max_list_number, self.name_prefix)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code == 200:
            servers = []
            for server in response.json().get('servers'):
                if server.get('addresses'):
                    format_server = self.get_format_server(server)
                    servers.append(format_server)
            result = {'code': 200, 'servers': servers}
        else:
            result = {'code': 400, 'error': response.json()}
        return result


    def get_server_id_by_name(self, name):
        """
        Get a server detail by server_ip
        :param server_ip: IP address
        :return: server detail
        """
        if not name:
            logger.error('Get server: name is empty.')
            return None
        url = ' https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/detail?status=ACTIVE&name={}'.format(self.region, self.project_id, name)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code == 200:
            if response.json().get('count') > 1:
                logger.error('Get server: name {} is not unique.'.format(name))
                return None
            if response.json().get('count') == 0:
                logger.error('Get server: name {} does not exists.'.format(name))
                return None
            servers = response.json().get('servers')
            result = servers[0]
        else:
            result = None
        return result

    def get_server(self, server_ip):
        """
        Get a server detail by server_ip
        :param server_ip: IP address
        :return: server detail
        """
        server_id = self.get_server_id(server_ip)
        if not server_id:
            logger.error('Get server: IP {} does not exists.'.format(server_ip))
            return {'code': 400, 'error': 'Not exist'}
        url = ' https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/{}'.format(self.region, self.project_id, server_id)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code == 200:
            server = response.json().get('server')
            status = server.get('status')
            if status == 'BUILD':
                status = 'BUILDING'
            elif status not in ['BUILDING', 'ACTIVE', 'DELETED']:
                status = 'OTHER'
            format_server = self.get_format_server(server, status)
            result = {'code': 200, 'server': format_server}
            logger.info('Get server: {}'.format(result))
        else:
            result = {'code': 400, 'error': response.json()}
            logger.error('Get server: {}'.format(result))
        return result

    def delete_server_by_name(self, name):
        """
        Delete server by name
        :param name: the name of the ecs server
        :return:
        """
        server = self.get_server_id_by_name(name=name)
        if server is None:
            return {'code': 400, 'error': 'Not exist'}
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/delete'.format(self.region, self.project_id)
        servers = [{'id': server['id']}]
        data = {
            'delete_publicip': True,
            'delete_volume': True,
            'servers': servers
        }
        response = session.post(url, headers=self.headers, data=json.dumps(data), timeout=timeout)
        if response.status_code == 200:
            result = {'code': 200, 'message': 'Delete successfully'}
            logger.info('Delete servers: {}'.format(server['name']))
        else:
            result = {'code': 400, 'error': response.json()}
            logger.error('Delete servers: {}'.format(result))
        return result

    def delete_servers(self, serverIps):
        """
        Delete servers
        :param serverIps: a list of IP address
        :return:
        """
        serverIds = self.get_server_ids(serverIps)
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/delete'.format(self.region, self.project_id)
        servers = [{'id': server_id} for server_id in serverIds]
        data = {
            'delete_publicip': True,
            'delete_volume': True,
            'servers': servers
        }
        response = session.post(url, headers=self.headers, data=json.dumps(data), timeout=timeout)
        if response.status_code == 200:
            result = {'code': 200, 'message': 'Delete successfully'}
            logger.info('Delete servers: {}'.format(serverIps))
        else:
            result = {'code': 400, 'error': response.json()}
            logger.error('Delete servers: {}'.format(result))
        return result

    def get_arch(self, flavor_name):
        """
        Get architecture by flavor_name
        :param flavor_name: name of flavor
        :return: architecture of the server
        """
        for arch in self.archMapping:
            if flavor_name in self.archMapping.get(arch):
                return arch
        return None

    def get_server_maps(self):
        """
        Get mapping between IP addresses and server_ids
        :return: A list of nested dictionaries {ip: server_id}
        """
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/detail?limit={}&status=ACTIVE&name={}'.format(
            self.region, self.project_id, self.max_list_number, self.name_prefix)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code == 200:
            server_maps = [
                {server.get('addresses').get(list(server.get('addresses').keys())[0])[0].get('addr'): server.get('id')}
                if server.get('addresses') else {None: server.get('id')}
                for server in response.json()['servers']]
            return server_maps
        else:
            return {}

    def get_hostname_maps(self):
        """
        Get mapping between IP addresses and hostnames
        :return: A list of nested dictionaries {IP: hostname}
        """
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/detail?limit={}&status=ACTIVE&name={}'.format(
            self.region, self.project_id, self.max_list_number, self.name_prefix)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code == 200:
            hostname_maps = [{server.get('addresses').get(list(server.get('addresses').keys())[0])[0].get(
                'addr'): server.get('name')}
                             if server.get('addresses') else {None: server.get('id')}
                             for server in response.json()['servers']]
            return hostname_maps
        else:
            return {}

    def get_hostname(self, server_ip):
        """
        Get hostname of the server through IP address
        :param server_ip: IP address
        :return: hostname of the server
        """
        servers = self.get_hostname_maps()
        for server in servers:
            if server.get(server_ip):
                hostname = server.get(server_ip)
                return hostname
        return None

    def get_server_id(self, server_ip):
        """
        Get the server_id through IP address
        :param server_ip: IP address
        :return: server_id
        """
        servers = self.get_server_maps()
        for server in servers:
            if server.get(server_ip):
                server_id = server.get(server_ip)
                return server_id
        return None

    def get_server_ids(self, server_ips):
        """
        Get a list of server_id through IP addresses
        :param server_ips: list of IP address
        :return: list of server_id
        """
        servers = self.get_server_maps()
        server_ids = []
        for ip in server_ips:
            for server in servers:
                if server.get(ip):
                    server_id = server.get(ip)
                    server_ids.append(server_id)
                    break
        return server_ids

    def get_server_ip(self, server_id: str):
        """
        Get IP address through server_id
        :param server_id: server_id
        :return: IP address
        """
        servers = self.get_server_maps()
        for server in servers:
            if server.get(list(server.keys())[0]) == server_id:
                return list(server.keys())[0]
        return None

    def get_server_ips(self, server_ids: list):
        """
        Get a list of IP addresses through server_ids
        :param server_ids: list of server_id
        :return: list of IP address
        """
        servers = self.get_server_maps()
        server_ips = []
        for server_id in server_ids:
            for server in servers:
                server_ip = list(server.keys())[0]
                if server.get(server_ip) == server_id:
                    server_ips.append(server_ip)
                    break
        return server_ips

    def get_max_number_can_create(self):
        """
        Get maximum number of servers can be created
        :return: count of remaining servers can be created or None when error occurs
        """
        url = 'https://ecs.{}.myhuaweicloud.com/v1/{}/cloudservers/detail'.format(self.region, self.project_id)
        response = session.get(url, headers=self.headers, timeout=timeout)
        if response.status_code != 200:
            result = {'code': 400, 'error': response.json()}
            logger.error('Get max number can create: {}'.format(result))
            return 0
        count = response.json().get('count')
        max_servers_number = self.max_servers_number
        return max_servers_number - count

