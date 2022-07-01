#!/usr/bin/env python

import json
import sys

from getpass import getpass
from jira import JIRA
from optparse import OptionParser
from story_points import initial_story_points_from, story_points_from

DONE_STATUSES = 'Done'

parser = OptionParser()
parser.add_option("-s", "--server", help="Target Jira server URL")
parser.add_option("-u", "--username")
parser.add_option("-p", "--password")
parser.add_option("-P", "--project", dest="projects", action="append",
                  help="Jira project to target. Multiple projects supported.")
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


def print_backlog_from(projects):
    epics = jira.search_issues(
            f'project in ({",".join(projects)}) AND issuetype=Epic')
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
    if not options.projects:
        print("No projects supplied", file=sys.stderr)
        sys.exit(1)

    print_backlog_from(options.projects)
