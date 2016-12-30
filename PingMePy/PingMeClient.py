# pylint: disable=R0904,C0302,R0913

from datetime import datetime
import warnings
import functools
from urlparse import urljoin
import logging

import requests
from requests.auth import HTTPDigestAuth

__author__ = 'TheGreatCO'

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        """
        This will actually display the warning for the decorator.
        """
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1)
        return func(*args, **kwargs)
    return new_func

class PingMeClient(object):
    """
    Stuff
    """
    url = None
    username = None
    api_key = None
    user = None

    def __init__(self, username, api_key, base_url='https://cloud.mongodb.com/'):
        """
        Initiate a new instance of the PingMePy class. It defaults to http://cloud.mongodb.com,
        however a local OpsManager instance can be specified.
        :param username: The username used to log into Cloud Manager / Ops Manager
        :param api_key: The API Key associated with the username
        :param base_url: The base URL of the Ops Manager installation. Leave blank for Cloud Manager
        :return: An instance of the PingMeClient class
        """
        if username is None:
            raise Exception("username cannot be None.")
        if api_key is None:
            raise Exception("api_key cannot be None.")
        if base_url is None:
            raise Exception("base_url cannot be None.")
        self.username = username
        self.api_key = api_key
        self.url = urljoin(base_url, 'api/public/v1.0/')
        self.user = self.get_user_by_name(self.username)


    # region Hosts
    def get_hosts(self, group_id):
        """
        Get the list of hosts in the specified group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-all-hosts-in-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The list of hosts in the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/hosts'.format(group_id))
        result = self.__get(url)

        return result

    def get_host(self, group_id, host_id):
        """
        Get a host by host_id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The Id of the host. If only host_name:port is known, use getHostByName
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts{1}'.format(group_id, host_id))
        result = self.__get(url)

        return result

    def get_host_by_name(self, group_id, host_name):
        """
        Get a host by host_name:port [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-name-and-port
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_name: The host_name:port combination of the host to retrieve
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_name, 'host_name')
        self.__test_parameter_contains_val(host_name, "host_name", ":")

        url = urljoin(self.url, 'groups/{0}/hosts/byName/{1}'.format(group_id, host_name))
        result = self.__get(url)

        return result

    def create_host(self, group_id, host):
        """
        Create a new host in the group. This is done using a host object. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#create-a-host
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host: The host object that needs to be created. See Cloud Manager docs link above.
        :return: The status of the call. Should be success or failure.
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')
        self.__test_parameter_for_string(host['hostname'], 'host.hostname')
        self.__test_parameter_for_int(host['port'], 'host.port')
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

        return result

    def update_host(self, group_id, host):
        """
        Update the specified host in the group [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#update-a-host
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host: The host object that needs to be updated. This needs to include the host_id.
        :return: The status of the call.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')
        self.__test_parameter_for_string(host['hostname'], 'host.hostname')
        self.__test_parameter_for_int(host['port'], 'host.port')
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

        return result

    def delete_host(self, group_id, host_id):
        """
        Delete the specified host_id from the group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}'.format(group_id, host_id))
        result = self.__delete(url)

        return result

    def get_last_ping(self, group_id, host_id):
        """
        Get the ping object for the last ping received for this host.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :return: The ping object.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/lastPing'.format(group_id, host_id))
        result = self.__get(url)

        return result

    # endregion

    # region Agents
    def get_agents(self, group_id):
        """
        Get the list of all agents in the specified group_id. Note that this is just a wrapper
        around the other type specific get_agent calls.
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
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
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The list of Monitoring Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'MONITORING'))
        result = self.__get(url)

        return result

    def get_backup_agents(self, group_id):
        """
        Get the list of backup agents in the specified group_id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The list of Backup Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'BACKUP'))
        result = self.__get(url)

        return result

    def get_automation_gents(self, group_id):
        """
        Get the list of automation agents in the specified group_id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The list of Automation Agents for the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(group_id, 'AUTOMATION'))
        result = self.__get(url)

        return result

    # endregion

    # region Metrics
    @deprecated
    def get_metrics(self, group_id, host_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics'.format(group_id, host_id))
        result = self.__get(url)

        return result

    @deprecated
    def get_metric(self, group_id, host_id, metric_id, granularity="1M", period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :param metric_id:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}?granularity={3}&period={4}'
                      .format(group_id, host_id, metric_id, granularity, period))
        result = self.__get(url)

        return result

    @deprecated
    def get_device_metric(self, group_id, host_id, metric_id, device_name, granularity="1M",
                          period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :param metric_id:
        :param device_name:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}/{3}?granularity={4}&period={5}'
                      .format(group_id, host_id, metric_id, device_name, granularity, period))
        result = self.__get(url)

        return result

    @deprecated
    def get_database_metric(self, group_id, host_id, metric_id, database_name, granularity="1M",
                            period="P2D"):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the host in Cloud Manager / Ops Manager, if not known,
                        use the hostName and call get_host_by_name to get the Id
        :param metric_id:
        :param database_name:
        :param granularity:
        :param period:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(metric_id, 'metric_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/metrics/{2}/{3}?granularity={4}&period={5}'
                      .format(group_id, host_id, metric_id, database_name, granularity, period))
        result = self.__get(url)

        return result

    # endregion

    # region Clusters
    def get_clusters(self, group_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/clusters'.format(group_id))
        result = self.__get(url)

        return result

    def get_cluster(self, group_id, cluster_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__get(url)

        return result

    def update_cluster(self, group_id, cluster_id, cluster_name):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the id.
        :param cluster_name: The name to set for the cluster.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_name')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__update(url, '{ "clusterName": "{0}" }'.format(cluster_name))

        return result

    # endregion

    # region Groups
    def get_groups(self):
        """
        Get the list of groups that the current username / API Key have access to.
        :return: The list of groups.
        """
        url = urljoin(self.url, 'groups')
        result = self.__get(url)

        return result

    def get_group(self, group_id):
        """
        Get a single group by its id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The group object
        """

        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__get(url)

        return result


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

        return result

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

        return result

    def delete_group(self, group_id):
        """
        Delete a group [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#delete-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The result of command, typically "OK" [2]
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#id4
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}'.format(group_id))
        result = self.__delete(url)

        return result

    def get_group_users(self, group_id):
        """
        Get the users that are members of the group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-all-users-in-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: The list of users in the group [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-users-in-a-group
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__get(url)

        return result

    def add_user_to_group(self, group_id, users):
        """
        Add the specified users to the group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#add-users-to-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param users: The list of users with roles. This must be an array even for a single user.
        :return: The result of the operation [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#id3
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(users, 'users')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/users'.format(group_id))
        result = self.__update(url, users)

        return result

    def remove_user_from_group(self, group_id, user_id):
        """
        Remove the specified user from the group
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#remove-a-user-from-a-group
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param user_id: The id of the user (not the username)
        :return: The result of the operation [2]
         [2]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#delete-a-user-from-a-group
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(user_id, 'user_id')

        url = urljoin(self.url, 'groups/{0}/users/{1}'.format(group_id, user_id))
        result = self.__delete(url)

        return result

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

        return result

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

        return result

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

        return result

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

        return result

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

        return result

    # endregion

    # region Alerts
    def get_alerts(self, group_id, status=None):
        """
        Get all of the alerts regardless of status, for the group_id [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-all-alerts
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param status: The status of alerts to get. Omit or set to None to get all alerts
                       regardless of status.
        :return: The list of alerts
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        if status is None:
            url = urljoin(self.url, 'groups/{0}/alerts'.format(group_id))
        else:
            url = urljoin(self.url, 'groups/{0}/alerts?status={1}'.format(group_id, status))

        result = self.__get(url)

        return result

    def get_alert(self, group_id, alert_id):
        """
        Get a specific alert [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-an-alert
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :return: The alert object
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}'.format(group_id, alert_id))

        result = self.__get(url)

        return result

    def acknowledge_alert(self, group_id, alert_id, acknowledge_until):
        """
        Acknowledge an alert until the specified time
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :param acknowledge_until: The time until which the alert will be acknowledged. Must
                                  be ISO8601 timestamp or Date object
        :return: The alert object.
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}'.format(group_id, alert_id))

        if isinstance(acknowledge_until, datetime):
            result = self.__update(url, '{ "acknowledgeUntil": "{0}"'
                                   .format(acknowledge_until.isoformat()))
        elif isinstance(acknowledge_until, str) or isinstance(acknowledge_until, unicode):
            result = self.__update(url, '{ "acknowledgeUntil": "{0}"'.format(acknowledge_until))
        else:
            raise Exception("acknowledge_until is the wrong type. Must be str, unicode, " \
                            "or datetime")

        return result

    # endregion

    # region Alert Configurations
    def get_alert_configs(self, group_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__get(url)

        return result

    def get_alert_config(self, group_id, alert_id):
        """
        Get the configuration that triggered the alert. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/alerts/#get-alert-configurations-that-triggered-an-alert
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_id: The id of the alert.
        :return: The alert configuration object
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/alerts/{1}/alertConfigs'.format(group_id, alert_id))

        result = self.__get(url)

        return result

    def get_all_open_alerts_triggered_by_alert_config(self, group_id, alert_config_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_config_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}/alerts'.format(group_id,
                                                                            alert_config_id))
        result = self.__get(url)

        return result

    def create_alert_config(self, group_id, alert_config):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_config:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(alert_config, 'alert_config')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__post(url, alert_config)

        return result

    def update_alert_config(self, group_id, alert_config):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_config:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(alert_config, 'alert_config')

        url = urljoin(self.url, 'groups/{0}/alertConfigs'.format(group_id))
        result = self.__update(url, alert_config)

        return result

    def toggle_alert_state(self, group_id, alert_config_id, alert_state="disabled"):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
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

        return result

    def delete_alert_config(self, group_id, alert_config_id):
        """

        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param alert_config_id:
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(alert_config_id, 'alert_config_id')

        url = urljoin(self.url, 'groups/{0}/alertConfigs/{1}'.format(group_id, alert_config_id))
        result = self.__delete(url)

        return result

    # endregion

    # region Maintenance Windows
    def get_maintenance_windows(self, group_id):
        """
        Get all maintenance windows with end dates in the future.
        https://docs.opsmanager.mongodb.com/current/reference/api/maintenance-windows/#get-all-maintenance-windows
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/maintenanceWindows'.format(group_id))
        result = self.__get(url)

        return result


    def get_maintenance_window(self, group_id, maintenance_window_id):
        """
        Get a Single Maintenance Window by its ID.
        https://docs.opsmanager.mongodb.com/current/reference/api/maintenance-windows/#get-a-single-maintenance-window-by-its-id
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/maintenanceWindows/{1}'.format(group_id, maintenance_window_id))
        result = self.__get(url)

        return result


    def create_maintenance_window(self, group_id, maintenance_window):
        """
        Create a new Maintenance Window for the group.
        https://docs.opsmanager.mongodb.com/current/reference/api/maintenance-windows/#create-a-maintenance-window
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """

        self.__test_parameter_contains_val(maintenance_window, 'startDate', 'startDate')
        self.__test_parameter_contains_val(maintenance_window, 'endDate', 'endDate')
        self.__test_parameter_contains_val(maintenance_window, 'description', 'description')
        self.__test_parameter_contains_val(maintenance_window, 'alertTypeNames', 'alertTypeNames')

        url = urljoin(self.url, 'groups{0}/maintenanceWindows'.format(group_id))
        result = self.__post(url, maintenance_window)

        return result

    def update_maintenance_window(self, group_id, maintenance_window):
        """
        Update a new Maintenance Window for the group.
        https://docs.opsmanager.mongodb.com/current/reference/api/maintenance-windows/#update-a-maintenance-window
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param maintenance_window: The maintenance window object.
        :return:
        """
        self.__test_parameter_contains_val(maintenance_window, 'id', 'id')
        self.__test_parameter_contains_val(maintenance_window, 'startDate', 'startDate')
        self.__test_parameter_contains_val(maintenance_window, 'endDate', 'endDate')
        self.__test_parameter_contains_val(maintenance_window, 'description', 'description')
        self.__test_parameter_contains_val(maintenance_window, 'alertTypeNames', 'alertTypeNames')

        url = urljoin(self.url, 'groups{0}/maintenanceWindows/{1}'
                      .format(group_id, maintenance_window['id']))
        result = self.__update(url, maintenance_window)

        return result

    def delete_maintenance_window(self, group_id, maintenance_window_id):
        """
        Delete a new Maintenance Window for the group
        https://docs.opsmanager.mongodb.com/current/reference/api/maintenance-windows/#delete-a-maintenance-window
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """

        url = urljoin(self.url, 'groups{0}/maintenanceWindows/{1}'
                      .format(group_id, maintenance_window_id))
        result = self.__delete(url)

        return result

    # endregion

    # region Backup Configurations
    def get_backup_configurations(self, group_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/backupConfigs'.format(group_id))
        result = self.__get(url)

        return result


    def get_backup_configuration(self, group_id, cluster_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')

        url = urljoin(self.url, 'groups/{0}/backupConfigs/{1}'.format(group_id, cluster_id))
        result = self.__get(url)

        return result


    def update_backup_configuration(self, group_id, backup_config):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_contains_val(backup_config, 'cluster_id', 'cluster_id')
        self.__test_parameter_contains_val(backup_config, 'statusName', 'statusName')

        url = urljoin(self.url, 'groups/{0}/backupConfigs/{1}'
                      .format(group_id, backup_config['cluster_id']))
        result = self.__update(url, backup_config)

        return result


    def update_backup_configuration_for_cluster(self, group_id, cluster_id, backup_config):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_contains_val(backup_config, 'statusName', 'statusName')

        url = urljoin(self.url, 'groups/{0}/backupConfigs/{1}'.format(group_id, cluster_id))
        result = self.__update(url, backup_config)

        return result
    # endregion

    # region Snapshot Schedule
    def get_snapshot_schedule(self, group_id, cluster_id):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')

        url = urljoin(self.url, 'groups/{0}/backupConfigs/{1}/snapshotSchedule'
                      .format(group_id, cluster_id))
        result = self.__get(url)

        return result


    def update_snapshot_schedule(self, group_id, cluster_id, snapshot_schedule):
        """
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param snapshot_schedule: The schedule to use for snapshot creation.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_dictionary(snapshot_schedule, 'snapshot_schedule')

        url = urljoin(self.url, 'groups/{0}/backupConfigs/{1}/snapshotSchedule'
                      .format(group_id, cluster_id))
        result = self.__update(url, snapshot_schedule)

        return result
    # endregion

    # region Snapshots
    def get_all_snapshots_for_cluster(self, group_id, cluster_id):
        """
        Get all snapshots for a given cluster_id. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/snapshots/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/snapshots'.format(group_id, cluster_id))
        result = self.__get(url)

        return result

    def get_snapshot_for_cluster(self, group_id, cluster_id, snapshot_id):
        """
        Get a specific snapshot for a given cluster_id. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/snapshots/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param snapshot_id: The id of the snapshot in Cloud Manager / Ops Manager, if not known,
                           call get_all_snapshots_for_cluster to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(snapshot_id, 'snapshot_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/snapshots/{2}'
                      .format(group_id, cluster_id, snapshot_id))
        result = self.__get(url)

        return result

    def delete_snapshot_for_cluster(self, group_id, cluster_id, snapshot_id):
        """
        Delete a specific snapshot for a given cluster_id. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/snapshots/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param snapshot_id: The id of the snapshot in Cloud Manager / Ops Manager, if not known,
                           call get_all_snapshots_for_cluster to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(snapshot_id, 'snapshot_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/snapshots/{2}'
                      .format(group_id, cluster_id, snapshot_id))
        result = self.__delete(url)

        return result
    # endregion

    # region Checkpoints
    def get_all_checkpoints_for_cluster(self, group_id, cluster_id):
        """
        Get a list of cluster checkpoints for the specified cluster_id. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/checkpoints/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/checkpoints'.format(group_id, cluster_id))
        result = self.__get(url)

        return result

    def get_checkpoint_for_cluster(self, group_id, cluster_id, checkpoint_id):
        """
        Get one cluster checkpoint for the specified cluster_id. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/checkpoints/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(checkpoint_id, 'checkpoint_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/checkpoints/{2}'
                      .format(group_id, cluster_id, checkpoint_id))
        result = self.__get(url)

        return result
    # endregion

    # region Restore Jobs
    def get_all_restore_jobs_for_cluster(self, group_id, cluster_id, batch_id=None):
        """
        Get All Restore Jobs for a Cluster. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param batch_id: [OPTIONAL] The id of the batch for the restore job in Cloud Manager /
                         Ops Manager, this is only returned as part of a sharded cluster restore.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/restoreJobs'.format(group_id, cluster_id))
        if batch_id is not None:
            url = url + "?batchId={0}".format(batch_id)
        result = self.__get(url)

        return result

    def get_restore_job_for_cluster(self, group_id, cluster_id, job_id):
        """
        Get a Single Restore Job for a Cluster. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param job_id: The id of the restore job for the cluster in Cloud Manager / Ops Manager,
                       if not known, call get_all_restore_jobs_for_cluster to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(job_id, 'job_id')
        url = urljoin(self.url, 'groups/{0}/clusters/{1}/restoreJobs/{2}'.format(group_id, cluster_id, job_id))
        result = self.__get(url)

        return result

    def get_all_restore_jobs_for_sccc(self, group_id, host_id):
        """
        Get All Restore Jobs for a Legacy Mirrored Config Server. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the SCCC Host in Cloud Manager / Ops Manager, if not known,
                           call get_clusters or get_hosts to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/restoreJobs'.format(group_id, host_id))
        result = self.__get(url)

        return result

    def get_restore_job_for_sccc(self, group_id, host_id, job_id):
        """
        Get a Single Restore Job for a Legacy Mirrored Config Server. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param host_id: The id of the SCCC Host in Cloud Manager / Ops Manager, if not known,
                           call get_clusters or get_hosts to get the Id.
        :param job_id: The id of the restore job for the cluster in Cloud Manager / Ops Manager,
                       if not known, call get_all_restore_jobs_for_cluster to get the Id
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(job_id, 'job_id')
        url = urljoin(self.url, 'groups/{0}/hosts/{1}/restoreJobs/{2}'
                      .format(group_id, host_id, job_id))
        result = self.__get(url)

        return result

    def create_restore_job_for_cluster(self, group_id, cluster_id, snapshot):
        """
        Create a Restore Job for a Cluster [1]. See examples for required post data. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/#examples-create-restore-jobs
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param snapshot_id: The id of the snapshot in Cloud Manager / Ops Manager, if not known,
                            call get_all_snapshots_for_cluster to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_dictionary(snapshot, 'snapshot')
        # self.__test_parameter_contains_val(snapshot, 'snapshotId', 'snapshotId')
        checkpoint_id = snapshot.get('checkpointId', default=None)
        snapshot_id = snapshot.get('snapshotId', default=None)
        timestamp = snapshot.get('timestamp', default=None)
        if snapshot_id is None and timestamp is None and checkpoint_id is None:
            raise Exception('snapshot.snapshotId and snapshot.timestamp and snapshot.checkpointId'\
                            'cannot be None. See https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/#examples-create-restore-jobs'\
                            ' for more information')
        if timestamp is not None:
            self.__test_parameter_contains_val(timestamp, 'date', 'date')
            self.__test_parameter_contains_val(timestamp, 'increment', 'increment')
        if snapshot.get('delivery', default=None) is not None:
            delivery = snapshot.get('delivery')
            if delivery.get('methodName', default=None) == 'SCP':
                self.__test_parameter_for_string(delivery.get('hostname'),
                                                 'snapshot.delivery.hostname')
                self.__test_parameter_for_int(delivery.get('port'), 'snapshot.delivery.port')
                self.__test_parameter_for_string(delivery.get('targetDirectory'),
                                                 'snapshot.delivery.targetDirectory')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}/restoreJobs'.format(group_id, cluster_id))
        result = self.__post(url, snapshot)

        return result

    def create_restore_job_for_sccc(self, group_id, host_id, snapshot):
        """
        Create a Restore Job for a legacy SCCC [1]. See examples for required post data. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/#examples-create-restore-jobs
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param cluster_id: The id of the cluster in Cloud Manager / Ops Manager, if not known,
                           call get_clusters to get the Id.
        :param snapshot_id: The id of the snapshot in Cloud Manager / Ops Manager, if not known,
                            call get_all_snapshots_for_cluster to get the Id.
        :return:
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_dictionary(snapshot, 'snapshot')

        snapshot_id = snapshot.get('snapshotId', default=None)
        if snapshot_id is None:
            raise Exception('snapshot.snapshotId cannot be None. '\
                            'See https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/#examples-create-restore-jobs'\
                            ' for more information')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/restoreJobs'.format(group_id, host_id))
        result = self.__post(url, snapshot)

        return result

    # endregion

    # region Whitelist
    def get_whitelist(self):
        """
        Get the list of whitelisted IPs for the user.
        :return: The list of whitelisted IPs for the user
        """
        url = urljoin(self.url, 'users/{0}/whitelist'.format(self.user['id']))
        result = self.__get(url)

        return result
    # endregion

    # region Automation Configuration
    def get_automation_configuration(self, group_id):
        """
        Get the Automation Configuration. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/automation-config/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: https://docs.opsmanager.mongodb.com/current/reference/api/automation-config/#automation-configuration-entity
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/automationConfig'.format(group_id))
        result = self.__get(url)

        return result

    def update_automation_configuration(self, group_id, config):
        """
        Update the Automation Configuration. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/automation-config/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :param config: The automation configuration for the group. It is recommended to
                       use get_automation_configuration first and modify the existing config
                       instead of building a configuration from scratch if possible.
        :return: https://docs.opsmanager.mongodb.com/current/reference/api/automation-config/#automation-configuration-entity
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/automationStatus'.format(group_id))
        result = self.__post(url, config)

        return result
    # endregion

    # region Automation Status
    def get_automation_status(self, group_id):
        """
        Get Automation Status. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/automation-status/
        :param group_id: The id of the group in Cloud Manager / Ops Manager, if not known,
                         use the groupName and call get_group_by_name to get the Id
        :return: https://docs.opsmanager.mongodb.com/current/reference/api/automation-status/#entity-fields
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        url = urljoin(self.url, 'groups/{0}/automationStatus'.format(group_id))
        result = self.__get(url)

        return result
    # endregion

    # region HTTP Methods
    def __get(self, url):
        """
        Make GET call to the specified URL
        :param url: The URL to which the call is made
        :return: The result of the GET
        """
        logging.debug('GET Call to {0}'.format(url))
        return requests.get(url, auth=HTTPDigestAuth(self.username, self.api_key)).json()

    def __update(self, url, data):
        """
        Make a PATCH call to the specified URL with the provided data payload
        :param url: The URL to which the call is made
        :param data: The payload to send to the URL
        :return: The result of the PATCH
        """
        logging.debug('PATCH Call to {0} with {1}'.format(url, data))
        return requests.patch(url, auth=HTTPDigestAuth(self.username, self.api_key), data=data).json()

    def __delete(self, url):
        """
        Make a DELETE call to the specified URL
        :param url: The URL to which the call is made
        :return: The result of the DELETE
        """
        logging.debug('DELETE Call to {0}'.format(url))
        return requests.delete(url, auth=HTTPDigestAuth(self.username, self.api_key)).json()

    def __post(self, url, data):
        """
        Make a POST call to the specified URL with the provided data payload
        :param url: The URL to which the call is made
        :param data: The payload to send to the URL
        :return: The result of the POST
        """
        logging.debug('POST Call to {0} with {1}'.format(url, data))
        return requests.post(url, auth=HTTPDigestAuth(self.username, self.api_key), data=data).json()

    # endregion

    @staticmethod
    def __test_parameter_for_string(param, param_name):
        if (not isinstance(param, unicode) and not isinstance(param, str)) or param is None\
            or param == '' or param.isspace():
            raise Exception(str.format('{0} must be a string and not empty.', param_name))

    @staticmethod
    def __test_parameter_for_int(param, param_name):
        if not isinstance(param, (int, long)):
            raise Exception(str.format('{0} must be an integer and not empty.', param_name))

    @staticmethod
    def __test_parameter_for_dictionary(param, param_name):
        if not isinstance(param, dict) or param is None or len(param) == 0:
            raise Exception(str.format('{0} must be a dictionary and not empty.'), param_name)

    @staticmethod
    def __test_parameter_contains_val(param, param_name, contains_val):
        if contains_val not in param:
            raise Exception(str.format('{0} must be in proper format. Missing {1}'),
                            param_name, contains_val)
    @staticmethod
    def __test_parameter_is_value(param, param_name, expected_val):
        if param is not True:
            raise Exception(str.format('{0} is {1}, expected value is {2}.',
                                       param_name, param, expected_val))
