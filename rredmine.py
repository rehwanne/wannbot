#!/usr/bin/env python

import re
import sys
import traceback

import redmine
from tabulate import tabulate

from response import Response
import config


if config.redmine_key:
    from redmine import Redmine,ResourceNotFoundError
    redmine = Redmine(config.redmine_url, key=config.redmine_key)
else:
    redmine = None


def link_redmine(mattermost_request):
    text = mattermost_request.text
    answer = ""
    text = ''.join(text).encode('latin1')

    ids = re.findall('#([0-9]+)', text)

    if (len(ids) < 1):
        return Response("no issue IDs found")

    answer = ""
    for issue in ids:
        issue_data = get_data(issue)
        header = issue_data[0]
        rows = issue_data[1:]
        answer += tabulate(rows, header, tablefmt="pipe")
        answer += "\n"

    return Response(answer)

def get_data(issue_id):
    data = []
    url = config.redmine_url + "issues/" + str(issue_id)
    data.append(["link", url])

    if not redmine:
        return data

    try:
        i = redmine.issue.get(issue_id)
    except ResourceNotFoundError as e:
        data.append(["**ERROR**", "issue_id not found ${}".format(issue_id)])
        traceback.print_exc(file=sys.stdout)
        return data
    except:
        data.append(["**ERROR**", "Unable to get data for issue_id ${}".format(issue_id)])
        traceback.print_exc(file=sys.stdout)
        return data

    data.append(["subject", i.subject])
    data.append(["author", i.author.name])

    if not hasattr(i, 'assigned_to'):
        name = "Nobody"
    else:
        name = i.assigned_to.name
    data.append(["assigned to", name])
    data.append(["status", i.status.name])
    return data
