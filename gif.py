#!/usr/bin/env python

import safygiphy

from response import Response

giief = safygiphy.Giphy()

def getgif(mattermost_request):
    text = mattermost_request.text
    search = ''.join(text).encode('latin1')
    jif = giief.random(tag=search)
    if jif['data']:
        t = u'' +jif['data']['image_original_url'] + " " +search
    else:
        t = "gibts nicht"
    return Response(t)
