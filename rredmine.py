#!/usr/bin/env python

import re
import sys
import traceback

import redmine

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

    m = re.findall('#([0-9]+)', text)
    if (len(m) < 1):
        return Response("no issue IDs found")
    else:
        for issue in m:
            url = config.redmine_url + "issues/" + issue
            if not redmine:
                answer += url + "\n"
            else:
                answer += "| link | {} | \n".format(url)
                answer += "|:---:|:---:| \n"
                try:
                    i = redmine.issue.get(issue)
                except ResourceNotFoundError as e:
                    answer += "| **ERROR** | Issue not found: #{} |\n".format(issue)
                    traceback.print_exc(file=sys.stdout)
                    answer += "\n"
                    continue
                except:
                    answer += "| **ERROR** | Unable to get data for issue: #{} |\n".format(issue)
                    traceback.print_exc(file=sys.stdout)
                    answer += "\n"
                    continue
                answer += "| subject | {} | \n".format(i.subject)
                answer += "| author | {} | \n".format(i.author.name)
                if not hasattr(i, 'assigned_to'):
                    name = "Nobody"
                else:
                    name = i.assigned_to.name
                answer += "| assigned to | {} | \n".format(name)
            answer += "\n"
    return Response(answer)
