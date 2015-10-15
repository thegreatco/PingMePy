__author__ = 'TheGreatCO'
import requests
from requests.auth import HTTPDigestAuth
from urlparse import urljoin
import json


class PingMeClient:
    url = None
    username = None
    apiKey = None

    def __init__(self, username, apiKey, baseUrl='https://cloud.mongodb.com/'):
        """Initiate a new instance of the PingMePy class. It defaults to http://cloud.mongodb.com,
        however a local OpsManager instance can be specified."""
        self.username = username
        self.apiKey = apiKey
        self.url = urljoin(baseUrl, 'api/public/v1.0/')

    def getAgents(self, groupId):
        """Get the list of all agents in the specified groupId"""

        self.__testParameterForString(groupId, 'groupId')
        agents = self.getMonitoringAgents(groupId).get('results')
        agents += self.getBackupAgents(groupId).get('results')
        agents += self.getAutomationAgents(groupId).get('results')
        return agents

    def getMonitoringAgents(self, groupId):
        """Get the list of monitoring agents in the specified groupId"""

        self.__testParameterForString(groupId, 'groupId')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(groupId, 'MONITORING'))
        result = self.__get(url)

        return json.loads(result.text)

    def getBackupAgents(self, groupId):
        """Get the list of backup agents in the specified groupId"""

        self.__testParameterForString(groupId, 'groupId')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(groupId, 'BACKUP'))
        result = self.__get(url)

        return json.loads(result.text)

    def getAutomationAgents(self, groupId):
        """Get the list of automation agents in the specified groupId"""

        self.__testParameterForString(groupId, 'groupId')

        url = urljoin(self.url, 'groups/{0}/agents/{1}'.format(groupId, 'AUTOMATION'))
        result = self.__get(url)

        return json.loads(result.text)

    def getGroups(self):
        url = urljoin(self.url, 'groups')
        result = self.__get(url)

        return json.loads(result.text)

    def getGroup(self, groupId):
        """

        :param groupId:
        :return:
        """

        self.__testParameterForString(groupId, 'groupId')

        url = urljoin(self.url, 'groups/' + groupId)
        result = self.__get(url)

        return json.loads(result.text)

    def getGroupByName(self, groupName):
        """
        Get a single group by its name [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/groups/#get-a-group
        :param groupName: The name of the group in Cloud / OpsManager
        :return: The group object
        """
        self.__testParameterForString(groupName, 'groupName')

        url = urljoin(self.url, 'groups/byName/' + groupName)
        result = self.__get(url)

        return json.loads(result.text)

    def getHosts(self, groupId):
        """
        Get the list of hosts in the specified group. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-all-hosts-in-a-group
        :param groupId: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :return: The list of hosts in the group.
        """

        self.__testParameterForString(groupId, 'groupId')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts')
        result = self.__get(url)

        return json.loads(result.text)

    def getHost(self, groupId, hostId):
        """
        Get a host by hostId [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-id
        :param groupId: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :param hostId: The Id of the host. If only hostname:port is known, use getHostByName
        :return: The Host object
        """

        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostId, 'hostId')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts/' + hostId)
        result = self.__get(url)

        return json.loads(result.text)

    def getHostByName(self, groupId, hostName):
        """
        Get a host by hostname:port [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#get-a-host-by-name-and-port
        :param groupId: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :param hostName: The hostname:port combination of the host to retrieve
        :return: The Host object
        """

        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostName, 'hostName')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts/byName/' + hostName)
        result = self.__get(url)

        return json.loads(result.text)

    def createHost(self, groupId, host):
        """
        Create a new host in the group. This is done using a host object. [1]
        [1]: https://docs.opsmanager.mongodb.com/current/reference/api/hosts/#create-a-host
        :param groupId: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :param host: The host object that needs to be created. See Cloud Manager docs link above.
        :return: The status of the call. Should be success or failure.
        """

        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForDictionary(host, 'host')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/' + groupId + '/hosts')
        result = self.__post(url, host)

        return json.loads(result.text)

    def updateHost(self, groupId, host):
        """
        :param groupId: The Id of the group, if not known, use the groupName and call getGroupByName to get the Id
        :param host: The host object that needs to be updated. This needs to include the hostId.
        :return: The status of the call. Should be success or failure.
        """
        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForDictionary(host, 'host')

        # I should probably have some validation of the dict here...

        url = urljoin(self.url, 'groups/' + groupId + '/hosts')
        result = self.__update(url, host)

        return json.loads(result.text)

    def deleteHost(self, groupId, hostId):
        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostId, 'hostId')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts/' + hostId)
        result = self.__delete(url)

        return json.loads(result.text)

    def getLastPing(self, groupId, hostId):
        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostId, 'hostId')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts/' + hostId + '/lastPing')
        result = self.__get(url)

        return json.loads(result.text)

    def getMetrics(self, groupId, hostId):
        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostId, 'hostId')

        url = urljoin(self.url, 'groups/' + groupId + '/hosts/' + hostId + '/metrics')
        result = self.__get(url)

        return json.loads(result.text)

    def getMetric(self, groupId, hostId, metricId, deviceName=None, granularity="1M", period="P2D"):
        self.__testParameterForString(groupId, 'groupId')
        self.__testParameterForString(hostId, 'hostId')
        self.__testParameterForString(metricId, 'metricId')
        if deviceName is not None:
            url = urljoin(self.url,
                          'groups/{0}/hosts/{1}/metrics/{2}/{3}?granularity={4}&period={5}'.format(groupId, hostId,
                                                                                                   metricId, deviceName,
                                                                                                   granularity, period))
        else:
            url = urljoin(self.url,
                          'groups/{0}/hosts/{1}/metrics/{2}?granularity={3}&period={4}'.format(groupId, hostId,
                                                                                               metricId, granularity,
                                                                                               period))
        result = self.__get(url)

        return json.loads(result.text)

    def __get(self, url):
        return requests.get(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __update(self, url, data):
        return requests.patch(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    def __delete(self, url):
        return requests.delete(url, auth=HTTPDigestAuth(self.username, self.apiKey))

    def __post(self, url, data):
        return requests.post(url, auth=HTTPDigestAuth(self.username, self.apiKey), data=data)

    @staticmethod
    def __testParameterForString(param, paramName):
        if (not isinstance(param, unicode) and not isinstance(param, str)) or param is None or param == '' \
                or param.isspace():
            raise Exception(str.format('{0} must be a string and not empty.', paramName))

    @staticmethod
    def __testParameterForDictionary(param, paramName):
        if not isinstance(param, dict) or param is None or len(param) == 0:
            raise Exception(str.format('{0} must be a dictionary and not empty.'), paramName)
