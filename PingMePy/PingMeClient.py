# pylint: disable=R0904,C0302,R0913

from datetime import datetime
import warnings
import functools
from urlparse import urljoin
import logging

import requests
from requests.auth import HTTPDigestAuth

__author__ = 'TheGreatCO'

def deprecated(func, new_func_name):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(new_func_name, *args, **kwargs):
        """
        This will actually display the warning for the decorator.
        """
        warnings.warn_explicit(
            "Call to deprecated function {}. Use {} instead.".format(func.__name__, new_func_name),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1)
        return func(*args, **kwargs)
    return new_func(new_func_name)

class PingMeClient(object):
    """
    A client for interacting with the MongoDB Cloud or Ops Manager API.
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
    # Last modified 2017-07-14
    def get_hosts(self, group_id, items_per_page=100, page_num=1):
        """
        Get all MongoDB processes in a group. The resulting list is sorted alphabetically
        by hostname:port. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts-get-all-in-group/
        :param group_id: ID of the group that owns this MongoDB process.
        :param items_per_page: The number of items to include in a page. Default is 100.
        :param page_num: The page number of the results to retrieve.
        :return: The list of hosts in the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_int(items_per_page, 'items_per_page')
        self.__test_parameter_for_int(page_num, 'page_num')

        url = urljoin(self.url, 'groups/{0}/hosts?itemsPerPage={1}&pageNum{2}'
                      .format(group_id, items_per_page, page_num))

        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def get_hosts_in_cluster(self, group_id, cluster_id, items_per_page=100, page_num=1):
        """
        Get all MongoDB processes in a group. Use the clusterId query parameter to only get the
        processes that belong to the specified cluster. The resulting list is sorted alphabetically
        by hostname:port. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts-get-all-in-group/
        :param group_id: ID of the group that owns this MongoDB process.
        :param cluster_id: The ID of the cluster to which the MongoDB processes belongs.
                           Specify this query parameter to limit the response to only
                           processes belonging to the specified cluster.
        :param items_per_page: The number of items to include in a page. Default is 100.
        :param page_num: The page number of the results to retrieve.
        :return: The list of hosts in the group.
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_int(items_per_page, 'items_per_page')
        self.__test_parameter_for_int(page_num, 'page_num')

        url = urljoin(self.url, 'groups/{0}/hosts?itemsPerPage={1}&pageNum{2}&clusterId={3}'.format(group_id, items_per_page, page_num, cluster_id))

        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def get_host(self, group_id, host_id):
        """
        Get the MongoDB process with the specified host ID.[1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :return: The Host object. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/host-get-by-id/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/host-get-by-id/#response-elements
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts{1}'.format(group_id, host_id))
        result = self.__get(url)

        return result

    @deprecated("get_host_by_hostname_and_port")
    # Last modified 2017-07-14
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
    
    # Last modified 2017-07-14
    def get_host_by_hostname_and_port(self, group_id, host_name, port):
        """
        Get a host by host_name and port [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/host-get-by-hostname-port/
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_name: Primary hostname. A MongoDB process typically has several aliases, 
                         so the primary is the best available name as decided by Cloud/Ops Manager.
        :return: The Host object
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_name, 'host_name')
        self.__test_parameter_for_int(port, 'port')

        url = urljoin(self.url, 'groups/{0}/hosts/byName/{1}:{2}'.format(group_id, host_name, port))
        result = self.__get(url)

        return result
    
    # Last modified 2017-07-14
    def create_host(self, group_id, host):
        """
        Start monitoring a new MongoDB process. The Monitoring Agent will start monitoring the
        MongoDB process on the hostname and port you specify. Ops Manager knows only the
        information that you provided. Thus, the document returned in the response document
        will include blank values while Ops Manager discovers the missing values. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host: The host object that needs to be created. [2]
        :return: The newly created host. [3]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/create-host/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/create-host/#request-body-parameters
        [3]: https://docs.opsmanager.mongodb.com/current/reference/api/create-host/#response-elements
        """

        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_dictionary(host, 'host')
        self.__test_parameter_for_string(host['hostname'], 'host.hostname')
        self.__test_parameter_for_int(host['port'], 'host.port')

        if host.get('authMechanismName', None) == "MONGODB_CR":
            self.__test_parameter_for_string(host['username'], 'host.username')
            self.__test_parameter_for_string(host['password'], 'host.password')

        if host.get('authMechanismName', None) == "MONGODB_X509":
            self.__test_parameter_is_value(host['username'], 'host.username', None)
            self.__test_parameter_is_value(host['password'], 'host.password', None)
            self.__test_parameter_is_value(host['sslEnabled'], 'host.sslEnabled', True)

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/{0}/hosts'.format(group_id))
        result = self.__post(url, host)

        return result

    # Last modified 2017-07-14
    def update_host(self, group_id, host_id, host):
        """
        Update the configuration of a monitored MongoDB process. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :param host: The host object that needs to be updated. [2]
        :return: The status of the call. [3]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/update-host/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/update-host/#request-body-parameters
        [3]: https://docs.opsmanager.mongodb.com/current/reference/api/update-host/#response-elements
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

        url = urljoin(self.url, 'groups/{0}/hosts/{1}'.format(group_id, host_id))
        result = self.__update(url, host)

        return result

    # Last modified 2017-07-14
    def delete_host(self, group_id, host_id):
        """
        Stop monitoring a MongoDB process. The Monitoring Agent will start monitoring the
        MongoDB process on the hostname and port you specify. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :return: The status of the call. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/delete-host/
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/delete-host/#response-elements
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}'.format(group_id, host_id))
        result = self.__delete(url)

        return result

    # Last modified 2017-07-14
    def get_last_ping(self, group_id, host_id):
        """
        Get the ping object for the last ping received for this host.
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :return: The status of the call.
        :return: The ping object.
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/lastPing'.format(group_id, host_id))
        result = self.__get(url)

        return result

    # endregion

    # region Disks
    # Last modified 2017-07-14
    def get_disk_partitions(self, group_id, host_id):
        """
        Retrieves the disks and disk partitions on which MongoDB runs. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/disks/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/disks'.format(group_id, host_id))
        result = self.__delete(url)

        return result

    # Last modified 2017-07-14
    def get_disk_partition(self, group_id, host_id, partition_name):
        """
        Retrieves the specified disk or disk partition. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :param partition_name: The name of the partition.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/disks/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(partition_name, 'partition_name')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/disks/{2}'.format(group_id, host_id,
                                                                        partition_name))
        result = self.__delete(url)

        return result

    # endregion

    # region Databases
    # Last modified 2017-07-14
    def get_databases(self, group_id, host_id):
        """
        Retrieves the databases running on a MongoDB process. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/databases/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/databases'.format(group_id, host_id))
        result = self.__delete(url)

        return result

    # Last modified 2017-07-14
    def get_single_database(self, group_id, host_id, database_name):
        """
        Retrieves a single database running on a MongoDB process. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :param database_name: The name of the database.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/databases/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(database_name, 'database_name')

        url = urljoin(self.url, 'groups/{0}/hosts/{1}/databases/{2}'.format(group_id, host_id,
                                                                            database_name))
        result = self.__delete(url)

        return result
    # endregion

    # region Clusters
    # Last modified 2017-07-14
    def get_clusters(self, group_id):
        """
        Get all clusters in a group. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :return: The list of clusters. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#get-all-clusters
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#id4
        """
        self.__test_parameter_for_string(group_id, 'group_id')

        url = urljoin(self.url, 'groups/{0}/clusters'.format(group_id))
        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def get_clusters_in_cluster(self, group_id, parent_cluster_id):
        """
        Get all clusters in a group with the specified parent cluster. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param parent_cluster_id: ID of the parent cluster that owns the clusters.
        :return: The list of clusters. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#get-all-clusters
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#id4
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(parent_cluster_id, 'parent_cluster_id')

        url = urljoin(self.url, 'groups/{0}/clusters?parentClusterId={1}'.format(group_id,
                                                                                 parent_cluster_id))
        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def get_cluster(self, group_id, cluster_id):
        """
        Get a single cluster by ID. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param cluster_id: ID of the cluster.
        :return: The cluster. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#get-a-cluster
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#response
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def update_cluster(self, group_id, cluster_id, cluster_name):
        """
        Update a cluster by ID. The only property that you may modify is the clusterName,
        since Cloud / Ops Manager discovers all other cluster properties. This operation
        is only available on clusters of type SHARDED and SHARDED_REPLICA_SET.
        :param group_id: ID of the group that owns this MongoDB process.
        :param cluster_id: ID of the cluster.
        :param cluster_name: The name to set for the cluster.
        :return: The cluster. [2]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#update-a-cluster
        [2]: https://docs.opsmanager.mongodb.com/current/reference/api/clusters/#id7
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_id')
        self.__test_parameter_for_string(cluster_id, 'cluster_name')

        url = urljoin(self.url, 'groups/{0}/clusters/{1}'.format(group_id, cluster_id))
        data = {"clusterName":cluster_name}
        result = self.__update(url, data)

        return result
    # endregion

    # region Measurements
    # Last modified 2017-07-14
    def get_host_measurements_by_period(self, group_id, host_id, granularity, period,
                                        measurements=None):
        """
        Retrieves measurements collected by the Monitoring and Automation Agents for your MongoDB
        processes, databases, and hardware disks. Monitoring Agents collect process and database
        measurements using MongoDB diagnostic commands, including serverStatus and dbStats.
        Automation Agents collect measurements for servers that run managed mongod and mongos
        processes. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :param granularity: An ISO-8601-formatted time period that specifies the interval between
                            measurement data points. For example, PT30S specifies 30-second
                            granularity. The supported values for this parameter are the same as
                            are available in the Granularity drop-down list when you view metrics
                            in the Ops Manager interface.
        :param period: How far back in the past to retrieve measurements, as specified by an
                       ISO-8601 period string. For example, setting PT24H specifies 24 hours.
                       An ISO-8601-formatted time period that specifies how far back in the
                       past to query. For example, to request the last 36 hours,
                       specify: period=P1DT12H.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/measurements/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(granularity, 'granularity')
        self.__test_parameter_for_string(period, 'period')

        url = urljoin(self.url,
                      'groups/{0}/hosts/{1}/measurements?granularity={2}&period={3}'
                      .format(group_id, host_id, granularity, period))

        if measurements is not None:
            m_parameter_string = "&".join(measurements)
            url = "{0}&{1}".format(url, m_parameter_string)

        result = self.__get(url)

        return result

    # Last modified 2017-07-14
    def get_host_measurements_by_range(self, group_id, host_id, granularity, start,
                                       end, measurements=None):
        """
        Retrieves measurements collected by the Monitoring and Automation Agents for your MongoDB
        processes, databases, and hardware disks. Monitoring Agents collect process and database
        measurements using MongoDB diagnostic commands, including serverStatus and dbStats.
        Automation Agents collect measurements for servers that run managed mongod and mongos
        processes. [1]
        :param group_id: ID of the group that owns this MongoDB process.
        :param host_id: ID of the host for the MongoDB process.
        :param granularity: An ISO-8601-formatted time period that specifies the interval between
                            measurement data points. For example, PT30S specifies 30-second
                            granularity. The supported values for this parameter are the same as
                            are available in the Granularity drop-down list when you view metrics
                            in the Ops Manager interface.
        :param start: The time at which to start retrieving measurements, as specified by an
                      ISO-8601 timestamp string. If you specify start you must also specify end.
        :param end: The time at which to stop retrieving measurements, as specified by an
                    ISO-8601 timestamp string. If you specify end you must also specify start.
        :param m: Specifies which measurements to return. If m is not specified, all measurements
                  are returned.

                  To specify multiple values for m, you must repeat the m parameter. For example:

                  ../measurements?m=CONNECTIONS&m=OPCOUNTER_CMD&m=OPCOUNTER_QUERY

                  You must specify measurements that are valid for the host. Cloud / Ops Manager
                  returns an error if any specified measurements are invalid For available
                  measurements, see Measurement Types.
        :return: The status of the call.
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/measurements/
        """
        self.__test_parameter_for_string(group_id, 'group_id')
        self.__test_parameter_for_string(host_id, 'host_id')
        self.__test_parameter_for_string(granularity, 'granularity')
        self.__test_parameter_for_string(start, 'start')
        self.__test_parameter_for_string(end, 'end')

        url = urljoin(self.url,
                      'groups/{0}/hosts/{1}/measurements?granularity={2}&start={3}&end={4}'
                      .format(group_id, host_id, granularity, start, end))

        if measurements is not None:
            m_parameter_string = "&".join(measurements)
            url = "{0}&{1}".format(url, m_parameter_string)

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
        checkpoint_id = snapshot.get('checkpointId', None)
        snapshot_id = snapshot.get('snapshotId', None)
        timestamp = snapshot.get('timestamp', None)
        if snapshot_id is None and timestamp is None and checkpoint_id is None:
            raise Exception('snapshot.snapshotId and snapshot.timestamp and snapshot.checkpointId'\
                            'cannot be None. See https://docs.opsmanager.mongodb.com/current/reference/api/restore-jobs/#examples-create-restore-jobs'\
                            ' for more information')
        if timestamp is not None:
            self.__test_parameter_contains_val(timestamp, 'date', 'date')
            self.__test_parameter_contains_val(timestamp, 'increment', 'increment')
        if snapshot.get('delivery', None) is not None:
            delivery = snapshot.get('delivery')
            if delivery.get('methodName', None) == 'SCP':
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

        snapshot_id = snapshot.get('snapshotId', None)
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
        return requests.patch(url, auth=HTTPDigestAuth(self.username, self.api_key), json=data).json()

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
        return requests.post(url, auth=HTTPDigestAuth(self.username, self.api_key), json=data).json()

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
