from datetime import datetime
import warnings
import functools
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
    user = None

    def __init__(self, username, apikey, base_url='https://cloud.mongodb.com/'):
        """
        Initiate a new instance of the PingMePy class. It defaults to http://cloud.mongodb.com,
        however a local OpsManager instance can be specified.
        :param username: The username used to log into Cloud Manager / Ops Manager
        :param apikey: The API Key associated with the username
        :param base_url: The base URL of the Ops Manager installation. Leave blank for Cloud Manager
        :return: An instance of the PingMeClient class
        """
        self.username = username
        self.apiKey = apikey
        self.url = urljoin(base_url, 'api/public/v1.0/')
        self.user = self.get_user_by_name(self.username)


    # region Hosts
    def get_hosts(self, group_id):
        """
        Get the list of hosts in the specified group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-all-hosts-in-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
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
                         get_group_by_name to get the Id
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
                         get_group_by_name to get the Id
        :param host_name: The host_name:port combination of the host to retrieve
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_name, 'host_name')
        self.__test_parameter_contains_string(host_name, "host_name", ":")

        url = urljoin(self.url, 'groups/{0}/hosts/byName/{1}'.format(group_id, host_name))
        result = self.__get(url)

        return json.loads(result.text)

    def create_host(self, group_id, host):
        """
        Create a new host in the group. This is done using a host object. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#create-a-host
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host: The host object that needs to be created. See Cloud Manager docs link above.
        :return: The status of the call. Should be success or failure.
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')
        self.__test_parameter_for_string(host['hostname'], 'host.hostname')
        self.__test_parameter_for_string(host['port'], 'host.port')
        if host['authMechanismName'] == "MONGODB_CR":
            self.__test_parameter_for_string(host['username'], 'host.username')
            self.__test_parameter_for_string(host['password'], 'host.password')
        if host['authMechanismName'] == "MONGODB_X509":
            self.__test_parameter_is_value(host['username'], 'host.username', None)
            self.__test_parameter_is_value(host['password'], 'host.password', None)
            self.__test_parameter_is_value(host['sslEnabled'], 'host.sslEnabled', True)

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__post(url, host)

        return json.loads(result.text)

    def update_host(self, group_id, host):
        """
        Update the specified host in the group [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#update-a-host
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host: The host object that needs to be updated. This needs to include the host_id.
        :return: The status of the call.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')
        self.__test_parameter_for_string(host['hostname'], 'host.hostname')
        self.__test_parameter_for_string(host['port'], 'host.port')
        if host['authMechanismName'] == "MONGODB_CR":
            self.__test_parameter_for_string(host['username'], 'host.username')
            self.__test_parameter_for_string(host['password'], 'host.password')
        if host['authMechanismName'] == "MONGODB_X509":
            self.__test_parameter_is_value(host['username'], 'host.username', None)
            self.__test_parameter_is_value(host['password'], 'host.password', None)
            self.__test_parameter_is_value(host['sslEnabled'], 'host.sslEnabled', True)

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/hosts'.format(group_id))
        result = self.__update(url, host)

        return json.loads(result.text)

    def delete_host(self, group_id, host_id):
        """
        Delete the specified host_id from the group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}'.format(group_id, host_id))
        result = self.__delete(url)

        return json.loads(result.text)

    def get_last_ping(self, group_id, host_id):
        """
        Get the ping object for the last ping received for this host.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
        :return: The ping object.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/lastPing'.format(group_id, host_id))
        result = self.__get(url)

        return json.loads(result.text)

    # endregion

    # region Agents
    def get_agents(self, group_id):
        """
        Get the list of all agents in the specified group_id. Note that this is just a wrapper around the other
        type specific get_agent calls.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
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
                         get_group_by_name to get the Id
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
                         get_group_by_name to get the Id
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
                         get_group_by_name to get the Id
        :return: The list of Automation Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'AUTOMATION'))
        result = self.__get(url)

        return json.loads(result.text)

    # endregion

    # region Metrics
    @deprecated
    def get_metrics(self, group_id, host_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics'.format(group_id, host_id))
        result = self.__get(url)

        return json.loads(result.text)
    
    @deprecated
    def get_metric(self, group_id, host_id, metric_id, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
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

    @deprecated
    def get_device_metric(self, group_id, host_id, metric_id, device_name, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
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

    @deprecated
    def get_database_metric(self, group_id, host_id, metric_id, database_name, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known, use the hostName and call
                        get_host_by_name to get the Id
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

    # endregion

    # region Clusters
    def get_clusters(self, group_id):
        """
        
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id 
        :return: 
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/clusters'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_cluster(self, group_id, cluster_id):
        """
        
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id 
        :param cluster_id: 
        :return: 
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__get(url)

        return json.loads(result.text)

    def update_cluster(self, group_id, cluster_id, cluster_name):
        """
        
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id 
        :param cluster_id: 
        :param cluster_name: 
        :return: 
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_name')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__update(url, '{ "clusterName": "{0}" }'.format(cluster_name))

        return json.loads(result.text)

    # endregion

    # region Groups
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
                         get_group_by_name to get the Id
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
        """
        Create a group [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#create-a-group
        :param group_name: The name of the group to use. This must be unique.
        :return: The group object. [2]
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#id2
        """
        self.__test_parameter_for_string(group_name, 'group_name')

        url = urljoin(self.url, 'groups/')
        result = self.__post(url, ' { "name" : "{0}" }'.format(group_name))

        return json.loads(result.text)

    def delete_group(self, group_id):
        """
        Delete a group [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#delete-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :return: The result of command, typically "OK" [2]
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#id4
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__delete(url)

        return json.loads(result.text)

    def get_group_users(self, group_id):
        """
        Get the users that are members of the group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-all-users-in-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :return: The list of users in the group [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-users-in-a-group
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def add_user_to_group(self, group_id, users):
        """
        Add the specified users to the group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#add-users-to-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param users: The list of users with roles. This must be an array even for a single user.
        :return: The result of the operation [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#id3
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(users, 'users')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__update(url, users)

        return json.loads(result.text)

    def remove_user_from_group(self, group_id, user_id):
        """
        Remove the specified user from the group
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#remove-a-user-from-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param user_id: The id of the user (not the username)
        :return: The result of the operation [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#delete-a-user-from-a-group
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(user_id, 'user_id')

        url = urljoin(self.url, 'groups/{0}/users/{1}'.format(group_id, user_id))
        result = self.__delete(url)

        return json.loads(result.text)

    # endregion

    # region Users
    def get_user_by_id(self, user_id):
        """
        Get a user object for the specified user_id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#get-a-user-by-id
        :param user_id: The id of the user.
        :return:
        """
        self.__test_parameter_for_string(user_id, 'user_id')

        url = urljoin(self.url, 'users/{0}'.format(user_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_user_by_name(self, user_name):
        """
        Get a user object for the specified user_name [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#get-a-user-by-id
        :param user_name: The username of the user
        :return:
        """
        self.__test_parameter_for_string(user_name, 'user_name')

        url = urljoin(self.url, 'users/byName/{0}'.format(user_name))
        result = self.__get(url)

        return json.loads(result.text)

    def create_user(self, user):
        """
        Create a user [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#id5
        :param user: The user object
        :return: The user object
        """
        self.__test_parameter_for_dictionary(user, 'user')

        url = urljoin(self.url, 'users')
        result = self.__post(url, user)

        return json.loads(result.text)

    def create_first_user(self, user):
        """
        Create the very first user in an OpsManager installation.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#id4
        :param user:
        :return:
        """
        self.__test_parameter_for_dictionary(user, 'user')

        url = urljoin(self.url, 'unauth/users')
        result = self.__post(url, user)

        return json.loads(result.text)

    def update_user(self, user):
        """
        Create a user [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#id5
        :param user: The user object
        :return: The updated user object [2]
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/users/#id6
        """
        self.__test_parameter_for_dictionary(user, 'user')

        url = urljoin(self.url, 'users')
        result = self.__update(url, user)

        return json.loads(result.text)

    # endregion

    # region Alerts
    def get_alerts(self, group_id, status=None):
        """
        Get all of the alerts regardless of status, for the group_id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-all-alerts
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param status: The status of alerts to get. Omit or set to None to get all alerts regardless of status.
        :return: The list of alerts
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        if status is None:
            url = urljoin(self.url, 'groups/{0}/alerts'.format(group_id))
        else:
            url = urljoin(self.url, 'groups/{0}/alerts?status={1}'.format(group_id, status))

        result = self.__get(url)

        return json.loads(result.text)

    def get_alert(self, group_id, alert_id):
        """
        Get a specific alert [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-an-alert
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :return: The alert object
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}'.format(group_id, alert_id))

        result = self.__get(url)

        return json.loads(result.text)

    def get_alert_config(self, group_id, alert_id):
        """
        Get the configuration that triggered the alert. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-alert-configurations-that-triggered-an-alert
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :return: The alert configuration object
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}/alertConfigs'.format(group_id, alert_id))

        result = self.__get(url)

        return json.loads(result.text)

    def acknowledge_alert(self, group_id, alert_id, acknowledge_until):
        """
        Acknowledge an alert until the specified time
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :param acknowledge_until: The time until which the alert will be acknowledged. Must be ISO8601 timestamp or Date
                                 object
        :return: The alert object.
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}'.format(group_id, alert_id))

        if isinstance(acknowledge_until, datetime):
            result = self.__update(url, '{ "acknowledgeUntil": "{0}"'.format(acknowledge_until.isoformat()))
        elif isinstance(acknowledge_until, str) or isinstance(acknowledge_until, unicode):
            result = self.__update(url, '{ "acknowledgeUntil": "{0}"'.format(acknowledge_until))
        else:
            raise Exception("acknowledge_until is the wrong type. Must be str, unicode, or datetime")

        return json.loads(result.text)

    # endregion

    # region Alert Configurations
    def get_alert_configs(self, group_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_alert_config(self, group_id, alert_config_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}'.format(group_id, alert_config_id))
        result = self.__get(url)

        return json.loads(result.text)

    def get_all_open_alerts_triggered_by_alert_config(self, group_id, alert_config_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}/alerts'.format(group_id, alert_config_id))
        result = self.__get(url)

        return json.loads(result.text)

    def create_alert_config(self, group_id, alert_config):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(alert_config, 'alert_config')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__post(url, alert_config)

        return json.loads(result.text)

    def update_alert_config(self, group_id, alert_config):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(alert_config, 'alert_config')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__update(url, alert_config)

        return json.loads(result.text)

    def toggle_alert_state(self, group_id, alert_config_id, alert_state="disabled"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config_id:
        :param alert_state:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')
        self.__test_parameter_for_string(alert_state, 'alert_state')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}'.format(group_id, alert_config_id))

        if alert_state == "disabled":
            result = self.__update(url, '{ "enabled": false }')
        elif alert_state == "enabled":
            result = self.__update(url, '{ "enabled": true }')
        else:
            raise Exception("alert_state parameter value was illegal. Must be enabled or disabled")

        return json.loads(result.text)

    def delete_alert_config(self, group_id, alert_config_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :param alert_config_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}'.format(group_id, alert_config_id))
        result = self.__delete(url)

        return json.loads(result.text)

    # endregion

    # region Maintenance Windows
    def get_maintenance_windows(self, group_id):
        """
        Get all maintenance windows with end dates in the future.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/maintenanceWindows'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)

    
    def get_maintenance_window(self, group_id, maintenance_window_id)""
        """
        Get a Single Maintenance Window by its ID.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known, use the groupName and call
                         get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/maintenanceWindows'.format(group_id))
        result = self.__get(url)

        return json.loads(result.text)
    # endregion

    # region Backup Configurations
    # endregion

    # region Snapshot Schedule
    # endregion

    # region Snapshots
    # endregion

    # region Checkpoints
    # endregion

    # region Restore Jobs
    # endregion

    # region Whitelist
    def get_whitelist(self):
        url = urljoin(self.url, 'users/{0}/whitelist'.format(self.user['id']))
        result = self.__get(url)

        return json.loads(result.text)
    # endregion

    # region Automation Configuration
    # endregion

    # region Automation Status
    # endregion

    # region HTTP Methods
    def __get(self, url):
        """
        Make GET call to the specified URL
        :param url: The URL to which the call is made
        :return: The result of the GET
        """
        logging.debug('GET Call to {0}'.format(url))
        return requests.get(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __update(self, url, data):
        """
        Make a PATCH call to the specified URL with the provided data payload
        :param url: The URL to which the call is made
        :param data: The payload to send to the URL
        :return: The result of the PATCH
        """
        logging.debug('PATCH Call to {0} with {1}'.format(url, data))
        return requests.patch(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    def __delete(self, url):
        """
        Make a DELETE call to the specified URL
        :param url: The URL to which the call is made
        :return: The result of the DELETE
        """
        logging.debug('DELETE Call to {0}'.format(url))
        return requests.delete(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __post(self, url, data):
        """
        Make a POST call to the specified URL with the provided data payload
        :param url: The URL to which the call is made
        :param data: The payload to send to the URL
        :return: The result of the POST
        """
        logging.debug('POST Call to {0} with {1}'.format(url, data))
        return requests.post(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    # endregion

    @staticmethod
    def __test_parameter_for_string(param, param_name):
        if (not isinstance(param, unicode) and not isinstance(param, str)) or param is None or param == '' \
                or param.isspace():
            raise Exception(str.format('{0} must be a string and not empty.', param_name))

    @staticmethod
    def __test_parameter_for_dictionary(param, param_name):
        if not isinstance(param, dict) or param is None or len(param) == 0:
            raise Exception(str.format('{0} must be a dictionary and not empty.'), param_name)

    @staticmethod
    def __test_parameter_contains_string(param, param_name, contains_val):
        if contains_val not in param:
            raise Exception(str.format('{0} must be in proper format. Missing {1}'), param_name, contains_val)
    @staticmethod
    def __test_parameter_is_value(param, param_name, expected_val)
        if not param == True:
            raise Exception(str.format('{0} is {1}, expected value is {2}.', param_name, param, expected_val))

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.warn_explicit(
                "Call to deprecated function {}.".format(func.__name__),
                category=DeprecationWarning,
                filename=func.func_code.co_filename,
                lineno=func.func_code.co_firstlineno + 1
            )
        return func(*args, **kwargs)
    return new_func