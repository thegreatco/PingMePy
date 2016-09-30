import json
import getopt
import sys
import os

from PingMePy import PingMeClient

__author__ = 'TheGreatCO'


def main(argv):
    api_key = ''
    username = ''
    group_name = ''
    server_url = ''
    usage_string = '~~~USAGE INSTRUCTIONS~~~'
    usage_string += '\r\n'
    usage_string += str.format('{0} {1} {2} {3} {4}\r\n', os.path.basename(__file__), '-u <username', '-a <apiKey>',
                               '-g <groupName>', '-s <OpsManager Server URL>')

    usage_string += "For example\r\n"
    usage_string += str.format('{0} {1} {2} {3} {4}\r\n', os.path.basename(__file__), '-u pete@example.com',
                               '-a 8ee720ba-e1aa-4c12-9e7c-a658d0beebde', '-g "App Servers"',
                               '-s http://myOpsManager.example.com:8080/')
    if len(argv) == 0:
        print(usage_string)
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, 'ha:u:g:s:', ['apiKey=', 'username=', 'groupName=', 'serverUrl='])
    except getopt.GetoptError:
        print(usage_string)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(usage_string)
            sys.exit()
        elif opt in ('-a', '-apiKey'):
            api_key = arg
        elif opt in ('-u', '-username'):
            username = arg
        elif opt in ('-g', '-groupName'):
            group_name = arg
        elif opt in ('-s', '-serverUrl'):
            server_url = arg

    print('Using group ' + group_name)
    print('Using server ' + server_url)
    if server_url == '':
        client = PingMeClient(username, api_key)
    else:
        client = PingMeClient(username, api_key, server_url)

    group = client.get_group_by_name(group_name)
    group_id = group.get('id')
    hosts = client.get_hosts(group_id).get('results')
    for host in hosts:
        host_id = host.get('id')
        host_name = host.get('hostname')
        metrics = client.get_metrics(group_id, host_id)
        for metric in metrics.get('results'):
            metric_name = metric.get('metricName')
            # This is to catch Munin Stats, which are enumerable
            if "MUNIN_IOSTAT_" in metric_name:
                metric_values = client.get_metric(group_id, host_id, metric_name)
                devices = metric_values.get('results')
                for device in devices:
                    obj = client.get_device_metric(group_id, host_id, metric_name, device.get('deviceName'), 'MINUTE',
                                                   'P3D')
                    if obj.get('error') is None:
                        obj.pop('links', None)
                        obj['hostname'] = host_name
                        print(json.dumps(obj))

            # This is to catch database stats, which are enumerable
            elif "DB_LOCK_PERCENT" in metric_name or \
                            "DB_ACCESSES_NOT_IN" in metric_name or \
                            "DB_PAGE_FAULT_EXCEPTIONS" in metric_name:
                metric_values = client.get_metric(group_id, host_id, metric_name)
                devices = metric_values.get('results')
                for device in devices:
                    obj = client.get_device_metric(group_id, host_id, metric_name, device.get('databaseName'), 'MINUTE',
                                                   'P3D')
                    if obj.get('error') is None:
                        obj.pop('links', None)
                        obj['hostname'] = host_name
                        print(json.dumps(obj))
            # This is for all the other "high level" stats
            else:
                obj = client.get_metric(group_id, host_id, metric_name, 'MINUTE', 'P3D')
                if obj.get('error') is None:
                    obj.pop('links', None)
                    obj['hostname'] = host_name
                    print(json.dumps(obj))


if __name__ == '__main__':
    main(sys.argv[1:])
