from requests.auth import HTTPDigestAuth
import sys
import getopt
import json
import os
import cookielib
import urllib2
import shutil
import requests

__author__ = 'TheGreatCO'


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


class PingMeClient:
    def __init__(self, username, api_key, base_url):
        self.username = username
        self.api_key = api_key
        self.url = base_url + 'api/public/v1.0/'

    def get_groups(self):
        url = self.url + 'groups'
        result = requests.get(url, auth=HTTPDigestAuth(self.username, self.api_key))
        return json.loads(result.text)


def get_diagnostic_archives(username, password, api_key, base_url, out_dir):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # Handle login. This should populate our cookie jar.
    login_data = json.dumps({"username": username, "password": password})
    req = urllib2.Request(base_url + 'user/v1/auth',
                          data=login_data,
                          headers={'Content-Type': 'application/json'})
    response = opener.open(req)
    response.read()

    mms_client = PingMeClient(username, api_key, base_url)
    groups = mms_client.get_groups()

    for group in groups['results']:
        print('Fetching diagnostic archives for ' + group['name'])

        req = urllib2.Request(base_url + 'admin/diagnostics/' + group.get('id') + '-diagnostics.tar.gz')
        response = opener.open(req)
        out_stream = open(out_dir + '/' + group.get('id') + '-diagnostics.tar.gz', 'w')
        out_stream.write(response.read())
        out_stream.close()

        req = urllib2.Request(
            base_url + 'admin/backup/diagnostics/' + group.get('id') + '.tar.gz?minutes=4320&limit=10000')
        response = opener.open(req)
        out_stream = open(out_dir + '/' + group.get('id') + '.tar.gz', 'w')
        out_stream.write(response.read())
        out_stream.close()


def main(argv):
    usage_string = '-u <username> ' \
                   '-p <password> ' \
                   '-a <api_key> ' \
                   '-s <opsManagerUrl>' \
                   '-b <basePath> ' \
                   '-c <appBasePath> ' \
                   '-d <daemonBasePath> ' \
                   '-e <backupAgentLogPath> ' \
                   '-f <monitoringAgentLogPath> ' \
                   '-g <automationAgentLogPath> '

    username = ''
    password = ''
    api_key = ''
    server_url = ''
    # Create a default base path
    base_path = '/opt/mongodb/'
    app_path = ''
    daemon_path = ''
    # Create default agent log paths
    backup_agent_log_path = '/var/log/mongodb-mms/'
    backup_agent_config_path = '/etc/mongodb-mms/'
    monitoring_agent_log_path = '/var/log/mongodb-mms/'
    monitoring_agent_config_path = '/etc/mongodb-mms/'
    automation_agent_log_path = '/var/log/mongodb-mms/'
    automation_agent_config_path = '/etc/mongodb-mms/'

    try:
        opts, args = getopt.getopt(argv, 'u:p:a:s:b:c:d:e:f:g:h',
                                   ['username=',
                                    'password=',
                                    'api_key=',
                                    'opsManagerServerUrl=',
                                    'basePath=',
                                    'appBasePath=',
                                    'daemonBasePath=',
                                    'backupAgentLogPath=',
                                    'monitoringAgentLogPath=',
                                    'automationAgentLogPath=',
                                    'help'])
    except getopt.GetoptError:
        print(os.path.basename(__file__) + usage_string)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(os.path.basename(__file__) + usage_string)
            sys.exit()
        elif opt in ('-u', '-username'):
            username = arg
        elif opt in ('-p', '-password'):
            password = arg
        elif opt in ('-a', '-api_key'):
            api_key = arg
        elif opt in ('-s', '-opsManagerServerUrl'):
            server_url = arg
        elif opt in ('-b', '-base_path'):
            base_path = arg
            if not base_path.endswith('/'):
                base_path += '/'
        elif opt in ('-c', '-appBasePath'):
            app_path = arg
            if not app_path.endswith('/'):
                app_path += '/'
        elif opt in ('-d', '-daemonBasePath'):
            daemon_path = arg
            if not daemon_path.endswith('/'):
                daemon_path += '/'
        elif opt in ('e', '-backupAgentLogPath'):
            backup_agent_log_path = arg
            if not backup_agent_log_path.endswith('/'):
                backup_agent_log_path += '/'
        elif opt in ('f', '-monitoringAgentLogPath'):
            monitoring_agent_log_path = arg
            if not monitoring_agent_log_path.endswith('/'):
                monitoring_agent_log_path += '/'
        elif opt in ('g', '-automationAgentLogPath'):
            automation_agent_log_path = arg
            if not automation_agent_log_path.endswith('/'):
                automation_agent_log_path += '/'

    if app_path == '':
        app_path = base_path + 'mms/'
    if daemon_path == '':
        daemon_path = base_path + 'mms-backup-daemon/'

    # Create the relevant App Paths
    app_logs_path = app_path + 'logs/'
    app_config_path = app_path + 'conf/'

    # Create the relevant Daemon Paths
    daemon_logs_path = daemon_path + 'logs/'
    daemon_config_path = daemon_path + 'conf/'

    # print('Base Path \t\t' + base_path)
    # print('App Base Path \t\t' + app_path)
    # print('App Logs Path \t\t' + app_logs_path)
    # print('App Config Path \t' + app_config_path)
    # print('Daemon Base Path \t' + daemon_path)
    # print('Daemon Logs Path \t' + daemon_logs_path)
    # print('Daemon Config Path \t' + daemon_config_path)
    # print('Backup Agent Log Path \t' + backup_agent_log_path)
    # print('Monitoring Agent Log Path \t' + monitoring_agent_log_path)
    # print('Automation Agent Log Path \t' + automation_agent_log_path)

    try:
        # If this doesn't fail, a component of MMS is running on this server.
        # process_ids = get_pid('mms-app')

        # Go one step further and verify the right path was provided in args
        if os.path.exists(base_path):
            nothing_found = True
            out_dir = os.path.dirname(os.path.abspath(__file__)) + '/opsmanager-diagnostic-data'
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)
            os.mkdir(out_dir)

            if os.path.exists(app_path) and os.path.exists(app_logs_path) and os.path.exists(app_config_path):
                # We are probably running on an app server
                print('Found App Server Directory, generating package')
                out_app_dir = out_dir + '/app'
                create_dir_if_not_exist(out_app_dir)

                shutil.copytree(app_logs_path, out_app_dir + '/logs')
                shutil.copytree(app_config_path, out_app_dir + '/conf')
                nothing_found = False
            if os.path.exists(daemon_path) and os.path.exists(daemon_logs_path) and os.path.exists(daemon_config_path):
                # We are probably running on an daemon server
                print('Found Daemon Directory, generating package')
                out_daemon_dir = out_dir + '/daemon'
                create_dir_if_not_exist(out_daemon_dir)

                shutil.copytree(daemon_logs_path, out_daemon_dir + '/logs')
                shutil.copytree(daemon_config_path, out_daemon_dir + '/config')
                nothing_found = False

            if os.path.exists(backup_agent_log_path) and os.path.exists(backup_agent_config_path):
                # We are probably running on a backup agent
                print('Found Backup Agent information, generating package')
                out_backup_agent_dir = out_dir + '/backupAgent'
                create_dir_if_not_exist(out_backup_agent_dir)

                shutil.copytree(backup_agent_log_path, out_backup_agent_dir + '/logs')
                shutil.copytree(backup_agent_config_path, out_backup_agent_dir + '/config')
                nothing_found = False

            if os.path.exists(monitoring_agent_log_path) and os.path.exists(monitoring_agent_config_path):
                # We are probably running on a monitoring agent
                print('Found Monitoring Agent information, generating package')
                out_monitoring_agent_dir = out_dir + '/backupAgent'
                create_dir_if_not_exist(out_monitoring_agent_dir)

                shutil.copytree(monitoring_agent_log_path, out_monitoring_agent_dir + '/logs')
                shutil.copytree(monitoring_agent_config_path, out_monitoring_agent_dir + '/config')
                nothing_found = False

            if os.path.exists(automation_agent_log_path) and os.path.exists(automation_agent_config_path):
                # We are probably running on a server with automated processes
                print('Found Automation Agent information, generating package')
                out_automation_agent_dir = out_dir + '/backupAgent'
                create_dir_if_not_exist(out_automation_agent_dir)

                shutil.copytree(automation_agent_log_path, out_automation_agent_dir + '/logs')
                shutil.copytree(automation_agent_config_path, out_automation_agent_dir + '/config')
                nothing_found = False

            if not username == '' and not password == '' and not api_key == '' and not server_url == '':
                print('Getting diagnostic archives')
                out_diagnostics_dir = out_dir + '/diagnosticArchives'
                create_dir_if_not_exist(out_diagnostics_dir)

                get_diagnostic_archives(username, password, api_key, server_url, out_diagnostics_dir)
                nothing_found = False

            if nothing_found:
                print('OpsManager not found on this Server, '
                      'did you specify the correct base_path? If not sure, leave it blank.')
                sys.exit(2)

            print('Generating archive...')

            if os.path.exists(out_dir + '.tar.gz'):
                os.remove(out_dir + '.tar.gz')

            shutil.make_archive('opsmanager-diagnostic-data', 'zip', '.', 'opsmanager-diagnostic-data')
            shutil.rmtree(out_dir)
        else:
            print('OpsManager not found on this Server, '
                  'did you specify the correct base_path? If not sure, leave it blank.')
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


if __name__ == '__main__':
    main(sys.argv[1:])
