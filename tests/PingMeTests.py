import unittest
import json

from PingMePy import PingMeClient

__author__ = 'TheGreatCO'


class PingMeTests(unittest.TestCase):
    client = PingMeClient("pete@mongodb.com", "c954a569-3905-4e51-9590-714be9fafe62",
                          "http://ec2-52-27-76-79.us-west-2.compute.amazonaws.com:8080")

    def getGroups(self):
        groups = self.client.get_groups().get('results')
        print json.dumps(groups)
        self.assertIsNotNone(groups)

    def testGetMonitoringAgents(self):
        try:
            group = self.client.get_group_by_name("App Servers")
            agents = self.client.get_monitoring_agents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "MONITORING")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetBackupAgents(self):
        try:
            group = self.client.get_group_by_name("App Servers")
            agents = self.client.get_backup_agents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "BACKUP")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetAutomationAgents(self):
        try:
            group = self.client.get_group_by_name("App Servers")
            agents = self.client.get_automation_gents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "AUTOMATION")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetAgents(self):
        try:
            group = self.client.get_group_by_name("App Servers")
            agents = self.client.get_agents(group.get('id'))
            agentCount = self.testGetMonitoringAgents()
            agentCount += self.testGetBackupAgents()
            agentCount += self.testGetAutomationAgents()
            self.assertEqual(len(agents), agentCount)
            self.assertIsNotNone(agents)
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")

    def testGetHosts(self):
        groups = self.client.get_groups().get('results')
        for group in groups:
            hosts = self.client.get_hosts(group.get('id'))
            print json.dumps(hosts)
            self.assertIsNotNone(hosts)

    def testGetHost(self):
        groups = self.client.get_groups().get('results')
        for group in groups:
            for host in self.client.get_hosts(group.get('id')).get('results'):
                host = self.client.get_host(group.get('id'), host.get('id'))
                print json.dumps(host)
                self.assertIsNotNone(host)

    def testStringValidator(self):
        try:
            self.client.get_group(None)
            self.fail("Exception wasn't thrown.")
        except Exception, ex:
            self.assertEqual(ex.message, str.format('{0} must be a string and not empty.', "groupId"))


if __name__ == '__main__':
    unittest.main()
