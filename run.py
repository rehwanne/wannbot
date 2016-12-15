#!/usr/bin/env python2
# -*- coding: iso-8859-1 -*-

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
import re
import sys
import traceback

import response
import config

# dictionary of handlers for enabled slash commands
#handlers['\foo'] = some_function()
handlers = dict()

#########
# Enable Handlers
####
if config.redmine_enable:
    import rredmine
    handlers[config.redmine_command] = rredmine.link_redmine

if config.gif_enable:
    import gif
    handlers[config.gif_command] = gif.getgif


class MattermostRequest(object):
    """
    This is what we get from Mattermost
    """
    def __init__(self,
                 response_url=None,
                 text=None,
                 token=None,
                 channel_id=None,
                 team_id=None,
                 command=None,
                 team_domain=None,
                 user_name=None,
                 channel_name=None):
        self.response_url = response_url
        self.text = text
        self.token = token
        self.channel_id = channel_id
        self.team_id = team_id
        self.command = command
        self.team_domain = team_domain
        self.user_name = user_name
        self.channel_name = channel_name

    def dispatch(self):
        """ call handler for command """
        global handlers
        try:
            c = self.command[0]
        except KeyError:
            print "Request didn't include a command"

        try:
            return handlers[c](self)
        except KeyError as e:
            print "No Handler for command: {}".format(c)
            return ""




class PostHandler(BaseHTTPRequestHandler):
    def get_post_data(self):
        length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(length).decode('utf-8')
        return urlparse.parse_qs(raw_data)

    def do_POST(self):
        """Respond to a POST request."""

        post_data = self.get_post_data()

        # map post values onto Request
        mr = MattermostRequest()
        for key, value in post_data.iteritems():
            setattr(mr, key, value)

        response = mr.dispatch()

        # send response to Mattermost
        self.send_response(response.status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response.data))


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer((config.hostname, config.port), PostHandler)
    print('Starting matterslash server, use <Ctrl-C> to stop')
    server.serve_forever()
