#!/usr/bin/env python

import csv
import json
import sys

from getpass import getpass
from jira import JIRA
from optparse import OptionParser
from story_points import initial_story_points_from, story_points_from


parser = OptionParser()
parser.add_option("-s", "--server", help="Target Jira server URL")
parser.add_option("-u", "--username")
parser.add_option("-p", "--password")
parser.add_option("-P", "--project", dest="projects", action="append",
                  help="Jira project to target. Multiple projects supported.")
parser.add_option("-S", "--storymode", action="store_true",
                  help="Extract points for stories rather than epics")
options, _ = parser.parse_args()

if not options.projects:
    print("No projects supplied using the -P parameter", file=sys.stderr)
    sys.exit(1)

with open('jira_config.json', 'r') as config_file:
    config = json.load(config_file)

DONE_STATUSES = config.get("done_statuses")
if not DONE_STATUSES:
    print("Done statuses not configured", file=sys.stderr)
    sys.exit(1)

STORY_ISSUE_TYPES = config.get("story_issue_types")
if not STORY_ISSUE_TYPES:
    print("Story issue types not configured", file=sys.stderr)
    sys.exit(1)

jira = JIRA(
    options={
        'server': options.server or config.get('server') or input("Server: ")
        },
    basic_auth=(
        options.username or config.get('username') or input("Username: "),
        options.password or getpass())
    )


def print_story_points():
    writer = csv.writer(sys.stdout)

    def print_epic_backlog_from(projects):
        epics = jira.search_issues(
                f'project in ({",".join(projects)}) AND issuetype=Epic '
                f'AND status not in ({",".join(DONE_STATUSES)}) '
                'order by status, rank',
                maxResults=None)
        for epic in epics:
            writer.writerow([
                            epic.key,
                            epic.fields.summary,
                            epic.fields.status,
                            initial_story_points_from(epic),
                            unfinished_points_in_stories_from(epic)
                            ])

    def print_story_backlog_from(projects):
            stories = jira.search_issues(
                    f'project in ({",".join(projects)}) '
                    f'AND issuetype in ({",".join(STORY_ISSUE_TYPES)}) '
                    f'AND status not in ({",".join(DONE_STATUSES)}) '
                    'order by status, rank',
                    maxResults=None)
            for story in stories:
                writer.writerow([
                                story.key,
                                story.fields.summary,
                                story.fields.status,
                                story_points_from(story)
                                ])

    if options.storymode:
        print_story_backlog_from(options.projects)
    else:
        print_epic_backlog_from(options.projects)


def unfinished_points_in_stories_from(epic):
    child_stories = jira.search_issues(
                f'"Epic Link"={epic.key} '
                f'AND status not in ({",".join(DONE_STATUSES)}) '
                'order by status, rank')
    return sum(story_points_from(story) for story in child_stories
               if story_points_from(story) is not None)


if __name__ == "__main__":
    print_story_points()
