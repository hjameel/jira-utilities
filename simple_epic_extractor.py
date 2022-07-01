#!/usr/bin/env python

import json

from getpass import getpass
from jira import JIRA
from optparse import OptionParser
from story_points import initial_story_points_from, story_points_from

DONE_STATUSES = 'Done'

parser = OptionParser()
parser.add_option("-s", "--server", dest="server")
parser.add_option("-u", "--username", dest="username")
parser.add_option("-p", "--password", dest="password")
options, _ = parser.parse_args()

with open('jira_config.json', 'r') as config_file:
    config = json.load(config_file)


jira = JIRA(
    options={
        'server': options.server or config.get('server') or input("Server: ")
        },
    basic_auth=(
        options.username or config.get('username') or input("Username: "),
        options.password or getpass())
    )


def main():
    epics = jira.search_issues("project=TEAM AND issuetype=Epic")
    for epic in epics:
        print(epic.key,
              epic.fields.status,
              initial_story_points_from(epic),
              unfinished_points_in_stories_from(epic))


def unfinished_points_in_stories_from(epic):
    child_stories = jira.search_issues(
                f'"Epic Link"={epic.key} '
                f'AND status not in ({DONE_STATUSES}) order by status, rank')
    return sum(story_points_from(story) for story in child_stories
               if story_points_from(story) is not None)


if __name__ == "__main__":
    main()
