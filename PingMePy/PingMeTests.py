from PingMePy.PingMe import PingMeClient
import unittest
import json

__author__ = 'TheGreatCO'



class PingMeClientTests(unittest.TestCase):
    client = PingMeClient("pete@mongodb.com", "c954a569-3905-4e51-9590-714be9fafe62",
                          "http://ec2-52-27-76-79.us-west-2.compute.amazonaws.com:8080")

    def getGroups(self):
        groups = self.client.getGroups().get('results')
        print json.dumps(groups)
        self.assertIsNotNone(groups)

    def testGetMonitoringAgents(self):
        try:
            group = self.client.getGroupByName("App Servers")
            agents = self.client.getMonitoringAgents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "MONITORING")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetBackupAgents(self):
        try:
            group = self.client.getGroupByName("App Servers")
            agents = self.client.getBackupAgents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "BACKUP")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetAutomationAgents(self):
        try:
            group = self.client.getGroupByName("App Servers")
            agents = self.client.getAutomationAgents(group.get('id'))
            self.assertIsNotNone(agents)
            for agent in agents.get('results'):
                self.assertEqual(agent.get('typeName'), "AUTOMATION")
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")
        return len(agents.get('results'))

    def testGetAgents(self):
        try:
            group = self.client.getGroupByName("App Servers")
            agents = self.client.getAgents(group.get('id'))
            agentCount = self.testGetMonitoringAgents()
            agentCount += self.testGetBackupAgents()
            agentCount += self.testGetAutomationAgents()
            self.assertEqual(len(agents), agentCount)
            self.assertIsNotNone(agents)
        except IOError:
            self.fail("Connection to OpsManager Instance Failed")

    def testGetHosts(self):
        groups = self.client.getGroups().get('results')
        for group in groups:
            hosts = self.client.getHosts(group.get('id'))
            print json.dumps(hosts)
            self.assertIsNotNone(hosts)

    def testGetHost(self):
        groups = self.client.getGroups().get('results')
        for group in groups:
            for host in self.client.getHosts(group.get('id')).get('results'):
                host = self.client.getHost(group.get('id'), host.get('id'))
                print json.dumps(host)
                self.assertIsNotNone(host)

    def testStringValidator(self):
        try:
            self.client.getGroup(None)
            self.fail("Exception wasn't thrown.")
        except Exception, ex:
            self.assertEqual(ex.message, str.format('{0} must be a string and not empty.', "groupId"))


if __name__ == '__main__':
    unittest.main()
