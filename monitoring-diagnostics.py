__author__ = 'TheGreatCO'
from PingMePy.PingMeClient import PingMeClient
import sys
import getopt
import json


class Results:
    def __init__(self, username, server):
        self.server = server
        self.username = username
        self.groups = GroupsList()


class GroupsList(object):
    def __init__(self):
        self.list = dict()

    def __iter__(self):
        return iter(self.list)

    def __getitem__(self, key):
        self.list.get(key)

    def append(self, object):
        self.list.append(object)


def main(argv):
    apiKey = ''
    username = ''
    serverUrl = ''
    try:
        opts, args = getopt.getopt(argv, 'ha:u:s:', ['apiKey=', 'username=', 'serverUrl='])
    except getopt.GetoptError:
        print('monitoring-diagnostics.py -u <username> -a <apiKey> -s <OpsManager Server URL>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('monitoring-diagnostics.py -u <username> -a <apiKey> -s <OpsManager Server URL>')
            sys.exit()
        elif opt in ('-a', '-apiKey'):
            apiKey = arg
        elif opt in ('-u', '-username'):
            username = arg
        elif opt in ('-s', '-serverUrl'):
            serverUrl = arg

    print('Using server ' + serverUrl)

    client = PingMeClient(username, apiKey, serverUrl)
    groupsJson = client.getGroups()
    results = dict()
    results['username'] = username
    results['server'] = serverUrl
    results['groups'] = dict()
    for group in groupsJson['results']:
        print('Found group ' + group['name'])
        groupId = group['id']
        groupName = group['name']

        results['groups'][groupName] = dict()

        results['groups'][groupName]['id'] = groupId
        results['groups'][groupName]['hosts'] = dict()
        hosts = client.get_hosts(groupId)
        for host in hosts['results']:
            hostId = host['id']
            hostName = host['hostname']
            results['groups'][groupName]['hosts'][hostName] = dict()
            results['groups'][groupName]['hosts'][hostName]['id'] = hostId
            results['groups'][groupName]['hosts'][hostName]['metrics'] = []
            for metric in client.getMetrics(groupId, hostId)['results']:
                values = client.getMetric(groupId, hostId, metric['metricName'])
                results['groups'][groupName]['hosts'][hostName]['metrics'].append(values)
    with open('data.txt', 'w') as outfile:
        json.dump(results, outfile)


if __name__ == '__main__':
    main(sys.argv[1:])
