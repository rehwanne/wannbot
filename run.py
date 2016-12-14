#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
import safygiphy
giief = safygiphy.Giphy()

HOSTNAME = 'localhost'
PORT = 5000 

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
        post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))

        for key, value in post_data.iteritems():
            if key == 'response_url':
                MattermostRequest.response_url = value
            elif key == 'text':
                MattermostRequest.text = value
            elif key == 'token':
                MattermostRequest.token = value
            elif key == 'channel_id':
                MattermostRequest.channel_id = value
            elif key == 'team_id':
                MattermostRequest.team_id = value
            elif key == 'command':
                MattermostRequest.command = value
            elif key == 'team_domain':
                MattermostRequest.team_domain = value
            elif key == 'user_name':
                MattermostRequest.user_name = value
            elif key == 'channel_name':
                MattermostRequest.channel_name = value

        responsetext = ''

        if MattermostRequest.command[0] == u'/gif':
            responsetext = getgif(MattermostRequest.text)

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
        print(jif)
        return u'' +jif['data']['image_original_url'] + " " +search
    else:
        return "gibts nicht"


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer((HOSTNAME, PORT), PostHandler)
    print('Starting matterslash server, use <Ctrl-C> to stop')
    server.serve_forever()
