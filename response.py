#!/usr/bin/env python

class Response(object):
    """ Response from handlers to Mattermost """
    def __init__(self,text, status=200, response_type="in_channel"):
        self.status = status
        self.response_type = response_type
        self.data = {}
        self.data['response_type'] = response_type
        self.data['text'] = text
