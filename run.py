#!/usr/bin/env python2
# -*- coding: iso-8859-1 -*-

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
import safygiphy
import re
import sys
import traceback

giief = safygiphy.Giphy()

import config

if config.redmine_key:
    from redmine import Redmine,ResourceNotFoundError
    redmine = Redmine(config.redmine_url, key=config.redmine_key)
else:
    redmine = None

_u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t


class MattermostRequest(object):
    """
    This is what we get from Mattermost
    """
    def __init__(self, response_url=None, text=None, token=None, channel_id=None, team_id=None, command=None,
                 team_domain=None, user_name=None, channel_name=None):
        self.response_url = response_url
        self.text = text
        self.token = token
        self.channel_id = channel_id
        self.team_id = team_id
        self.command = command
        self.team_domain = team_domain
        self.user_name = user_name
        self.channel_name = channel_name


class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Respond to a POST request."""
        length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(length).decode('utf-8')
        post_data = urlparse.parse_qs(raw_data)

        mr = MattermostRequest()

        for key, value in post_data.iteritems():
            setattr(mr, key, value)

        responsetext = ''

        if mr.command[0] == u'/gif':
            responsetext = getgif(mr.text)
        elif mr.command[0] == u'/link_redmine':
            responsetext = link_redmine(mr.text)

        if responsetext:
            data = {}
            data['response_type'] = 'in_channel'
            data['text'] = responsetext
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data))
        return

def getgif(text):
    search = ''.join(text).encode('latin1')
    jif = giief.random(tag=search)
    if jif['data']:
        return u'' +jif['data']['image_original_url'] + " " +search
    else:
        return "gibts nicht"

def link_redmine(text):
    answer = ""

    text = ''.join(text).encode('latin1')

    m = re.findall('#([0-9]+)', text)
    if (len(m) < 1):
        return "no issue IDs found"
    else:
        for issue in m:
            answer += config.redmine_url + "issues/" + issue + "\n"
            if redmine:
                try:
                    i = redmine.issue.get(issue)
                except ResourceNotFoundError as e:
                    answer += "Can't find issue #" + issue + "\n"
                    traceback.print_exc(file=sys.stdout)
                    continue
                except:
                    answer += "Error retrieving issue #" + issue + "\n"
                    traceback.print_exc(file=sys.stdout)
                    continue
                    continue
                answer += "subject: " + i.subject + "\n"
                answer += "author: " + i.author.name + "\n"
                if not hasattr(i, 'assigned_to'):
                    name = "Nobody"
                else:
                    name = i.assigned_to.name
                answer += "assigned to: " + name + "\n"
            answer += "\n"
    return answer


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer((config.hostname, config.port), PostHandler)
    print('Starting matterslash server, use <Ctrl-C> to stop')
    server.serve_forever()
