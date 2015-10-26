import requests
from requests.auth import HTTPDigestAuth
from urlparse import urljoin
import json
import logging

__author__ = 'TheGreatCO'


class PingMeClient:
    url = None
    username = None
    apiKey = None

    def __init__(self, username, api_key, base_url='https://cloud.mongodb.com/'):
        """
        Initiate a new instance of the PingMePy class. It defaults to http://cloud.mongodb.com,
        however a local OpsManager instance can be specified.
        :param username: The username used to log into Cloud Manager / Ops Manager
        :param api_key: The API Key associated with the username
        :param base_url: The base URL of the Ops Manager installation. Leave blank for Cloud Manager
        :return: An instance of the PingMeClient class
        """
        self.username = username
        self.apiKey = api_key
        self.url = urljoin(base_url, 'api/public/v1.0/')

    def get_hosts(self, group_id):
        """
        Get the list of hosts in the specified group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-all-hosts-in-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :return: The list of hosts in the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/hosts'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_host(self, group_id, host_id):
        """
        Get a host by host_id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id: The Id of the host. If only host_name:port is known, use getHostByName
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts{1}'.format(group_id, host_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_host_by_name(self, group_id, host_name):
        """
        Get a host by host_name:port [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-name-and-port
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_name: The host_name:port combination of the host to retrieve
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_name, 'host_name')

        url = urljoin(self.url, 'groups/{0}/hosts/byName/{1}'.format(group_id, host_name))
        result = self.__get(url)

        return json.loads(result.text)

    def create_host(self, group_id, host):
        """
        Create a new host in the group. This is done using a host object. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#create-a-host
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host: The host object that needs to be created. See Cloud Manager docs link above.
        :return: The status of the call. Should be success or failure.
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__post(url, host)

        return json.loads(result.text)

    def update_host(self, group_id, host):
        """
        :param group_id: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :param host: The host object that needs to be updated. This needs to include the host_id.
        :return: The status of the call. Should be success or failure.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/hosts'.format(group_id))
        result = self.__update(url, host)

        return json.loads(result.text)

    def delete_host(self, group_id, host_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}'.format(group_id, host_id))
        result = self.__delete(url)

        return json.loads(result.text)

    def get_last_ping(self, group_id, host_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/lastPing'.format(group_id, host_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_agents(self, group_id):
        """
        Get the list of all agents in the specified group_id. Note that this is just a wrapper around the other
        type specific get_agent calls.
        :param group_id:
        :return:
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        agents = self.get_monitoring_agents(group_id).get('results')
        agents += self.get_backup_agents(group_id).get('results')
        agents += self.get_automation_gents(group_id).get('results')
        return agents

    def get_monitoring_agents(self, group_id):
        """
        Get the list of monitoring agents in the specified group_id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :return: The list of Monitoring Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'MONITORING'))
        result = self.__get(url)

        return json.loads(result.text)

    def get_backup_agents(self, group_id):
        """
        Get the list of backup agents in the specified group_id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :return: The list of Backup Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'BACKUP'))
        result = self.__get(url)

        return json.loads(result.text)

    def get_automation_gents(self, group_id):
        """
        Get the list of automation agents in the specified group_id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :return: The list of Automation Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'AUTOMATION'))
        result = self.__get(url)

        return json.loads(result.text)

    def get_metrics(self, group_id, host_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics'.format(group_id, host_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_metric(self, group_id, host_id, metric_id, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :param metric_id:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}?granularity={3}&period={4}'.format(group_id, host_id,
                                                                                                     metric_id,
                                                                                                     granularity,
                                                                                                     period))
        result = self.__get(url)

        return json.loads(result.text)

    def get_device_metric(self, group_id, host_id, metric_id, device_name, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :param metric_id:
        :param device_name:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}/{3}?granularity={4}&period={5}'.format(group_id,
                                                                                                         host_id,
                                                                                                         metric_id,
                                                                                                         device_name,
                                                                                                         granularity,
                                                                                                         period))
        result = self.__get(url)

        return json.loads(result.text)

    def get_database_metric(self, group_id, host_id, metric_id, database_name, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :param host_id:
        :param metric_id:
        :param database_name:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}/{3}?granularity={4}&period={5}'.format(group_id,
                                                                                                         host_id,
                                                                                                         metric_id,
                                                                                                         database_name,
                                                                                                         granularity,
                                                                                                         period))
        result = self.__get(url)

        return json.loads(result.text)

    def get_clusters(self, group_id):
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/clusters'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_cluster(self, group_id, cluster_id):
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__get(url)

        return json.loads(result.text)

    def update_cluster(self, group_id, cluster_id, cluster_name):
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_name')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__update(url, '{ "clusterName": "{0}" }'.format(cluster_name))

        return json.loads(result.text)

    def get_groups(self):
        """
        Get the list of groups that the current username / API Key have access to.
        :return: The list of groups.
        """
        url = urljoin(self.url, 'groups')
        result = self.__get(url)

        return json.loads(result.text)

    def get_group(self, group_id):
        """
        Get a single group by its id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         getGroupByName to get the Id
        :return: The group object
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_group_by_name(self, group_name):
        """
        Get a single group by its name [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-a-group
        :param group_name: The name of the group in Cloud / OpsManager
        :return: The group object
        """
        self.__test_parameter_for_string(group_name, 'groupName')

        url = urljoin(self.url, 'groups/byName/{0}'.format(group_name))
        result = self.__get(url)

        return json.loads(result.text)

    def create_group(self, group_name):
        self.__test_parameter_for_string(group_name, 'group_name')

        url = urljoin(self.url, 'groups/')
        result = self.__post(url, ' { "name" : "{0}" }'.format(group_name))

        return json.loads(result.text)

    def delete_group(self, group_id):
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__delete(url)

        return json.loads(result.text)

    def get_group_users(self, group_id):
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def add_user_to_group(self, group_id, users):
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(users, 'users')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__update(url, users)

        return json.loads(result.text)

    def remove_user_from_group(self, group_id, user_id):
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(user_id, 'user_id')

        url = urljoin(self.url, 'groups/{0}/users/{1}'.format(group_id, user_id))
        result = self.__delete(url)

        return json.loads(result.text)

    def __get(self, url):
        logging.debug('GET Call to {0}'.format(url))
        return requests.get(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __update(self, url, data):
        logging.debug('PATCH Call to {0} with {1}'.format(url, data))
        return requests.patch(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    def __delete(self, url):
        logging.debug('DELETE Call to {0}'.format(url))
        return requests.delete(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __post(self, url, data):
        logging.debug('POST Call to {0} with {1}'.format(url, data))
        return requests.post(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    @staticmethod
    def __test_parameter_for_string(param, param_name):
        if (not isinstance(param, unicode) and not isinstance(param, str)) or param is None or param == '' \
                or param.isspace():
            raise Exception(str.format('{0} must be a string and not empty.', param_name))

    @staticmethod
    def __test_parameter_for_dictionary(param, param_name):
        if not isinstance(param, dict) or param is None or len(param) == 0:
            raise Exception(str.format('{0} must be a dictionary and not empty.'), param_name)
