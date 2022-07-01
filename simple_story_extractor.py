from jira import JIRA
import json

with open('jira_config.json', 'r') as config_file:
    config = json.load(config_file)

jira = JIRA(
    options={'server': config['server']},
    basic_auth=(config['email'], config['apitoken']))

epics = jira.search_issues("project=TEAM AND issuetype=Story")

for epic in epics:
    print(epic.key, epic.fields.status, epic.fields.customfield_10026)
