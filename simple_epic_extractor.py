from jira import JIRA
import json

DONE_STATUSES = 'Done'

with open('jira_config.json', 'r') as config_file:
    config = json.load(config_file)

jira = JIRA(
    options={'server': config['server']},
    basic_auth=(config['email'], config['apitoken']))


def main():
    epics = jira.search_issues("project=TEAM AND issuetype=Epic")

    for epic in epics:
        unfinished_points_in_stories = unfinished_points_in_stories_from(epic)
        print(epic.key,
              epic.fields.status,
              epic.fields.customfield_10026,
              unfinished_points_in_stories)


def unfinished_points_in_stories_from(epic):
    child_stories = jira.search_issues(
                f'"Epic Link"={epic.key} '
                f'AND status not in ({DONE_STATUSES}) order by status, rank')
    return sum(story.fields.customfield_10026 for story in child_stories
               if story.fields.customfield_10026 is not None)


main()
