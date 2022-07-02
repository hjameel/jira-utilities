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

with open('jira_config.json', 'r') as config_file:
    config = json.load(config_file)

DONE_STATUSES = config.get("done_statuses")
if not DONE_STATUSES:
    print("Done statuses not configured", file=sys.stderr)
    sys.exit(1)

jira = JIRA(
    options={
        'server': options.server or config.get('server') or input("Server: ")
        },
    basic_auth=(
        options.username or config.get('username') or input("Username: "),
        options.password or getpass())
    )


def print_epic_backlog_from(projects, writer):
    epics = jira.search_issues(
            f'project in ({",".join(projects)}) AND issuetype=Epic '
            f'AND status not in ({",".join(DONE_STATUSES)}) '
            'order by status, rank')
    for epic in epics:
        writer.writerow([
                        epic.key,
                        epic.fields.summary,
                        epic.fields.status,
                        initial_story_points_from(epic),
                        unfinished_points_in_stories_from(epic)
                        ])


def unfinished_points_in_stories_from(epic):
    child_stories = jira.search_issues(
                f'"Epic Link"={epic.key} '
                f'AND status not in ({",".join(DONE_STATUSES)}) '
                'order by status, rank')
    return sum(story_points_from(story) for story in child_stories
               if story_points_from(story) is not None)


def print_story_backlog_from(projects, writer):
        stories = jira.search_issues(
                "project=TEAM AND issuetype=Story "
                f'AND status not in ({",".join(DONE_STATUSES)}) '
                'order by status, rank')
        for story in stories:
            writer.writerow([
                            story.key,
                            story.fields.summary,
                            story.fields.status,
                            initial_story_points_from(story)
                            ])


if __name__ == "__main__":
    if not options.projects:
        print("No projects supplied using the -P parameter", file=sys.stderr)
        sys.exit(1)
    writer = csv.writer(sys.stdout)

    if options.storymode:
        print_story_backlog_from(options.projects, writer)

    print_epic_backlog_from(options.projects, writer)
