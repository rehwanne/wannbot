#!/usr/bin/env python
import re

from tabulate import tabulate
import github

from response import Response
import config

commands = {}

def handle(mattermost_request):
    text = mattermost_request.text[0]
    text = text.strip()
    try:
        (command, arg) = text.split(' ', 1)
    except ValueError:
        command = text
        arg = ""

    try:
        global commands
        func = commands[command]
    except KeyError:
        return Response("Unknown command: " + command)
    return Response(func(arg))

def issue(arg):
    arg = arg.strip()
    if len(arg) == 0:
        return "error: missing arguments"

    args = arg.split(' ')
    if len(args) == 1:
        try:
            (project, issue) = re.search('([^/]+/[^/]+)/issues/(\d+)', arg).groups()
        except AttributeError:
            return "error: no url found"
    elif len(args) == 2:
        project = args[0]
        issue = args[1]
    else:
        return "error: too many arguments"

    issue = int(issue)
    hub = github.Github()
    repo = hub.get_repo(project)
    try:
        issue = repo.get_issue(issue)
    except github.UnknownObjectException:
        return "Issue not found"

    header = ["Link", issue.html_url]
    rows = []
    rows.append(['Title', issue.title])
    rows.append(['State', issue.state])

    assignee = issue.assignee
    if not assignee:
        name = "No one assigned"
    else:
        name = "{} ({})".format(assignee.login, assignee.name)
    rows.append(['Assignee', name])

    if issue.labels:
        labels = ""
        for label in issue.labels:
            labels += label.name + " "
        rows.append(["Labels", labels])

    return tabulate(rows, header, tablefmt="pipe")


commands['issue'] = issue
