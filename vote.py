#!/usr/bin/env python2

class VotingAlreadyStartedError(Exception):
    pass

class OptionNotFoundError(Exception):
    pass

class UserAlreadyVotedError(Exception):
    pass

class NoActiveVotingError(Exception):
    pass

class Option(object):
    def __init__(self, text, i):
        if len(text) <= 0:
            raise ValueError("Option text can't be empty")
        self.text = text
        self.count = 0
        self.voters = list()
        self.id = i

    def vote(self, voter):
        self.count += 1
        if voter in self.voters:
            raise UserAlreadyVotedError()
        self.voters.append(voter)

class Voting(object):
    STATE_PREPARING = 0
    STATE_RUNNING = 1

    def __init__(self, topic):
        if len(topic) <= 0:
            raise ValueError("Topic can't be empty")
        self.topic = topic
        self.state = Voting.STATE_PREPARING
        self.options = list()

    def add_option(self, text):
        if self.state > Voting.STATE_PREPARING:
            raise VotingAlreadyStartedError()
        self.options.append(Option(text, len(self.options)))

    def start(self):
        if self.state > Voting.STATE_PREPARING:
            raise VotingAlreadyStartedError()
        self.state = Voting.STATE_RUNNING

    def restart(self):
        self.options = list()

    def vote(self, option_number, voter):
        try:
            option = self.options[option_number]
        except IndexError:
            raise OptionNotFoundError("Option " + option_number + "not found")
        option.vote(voter)

    def __str__(self):
        r = "**{}**\n".format(self.topic)

        if len(self.options) == 0:
            width = 0
        else:
            width = len(max(self.options, key=lambda x:len(x.text)).text)

        width = max(width, len("Option"))
        j = (width - len("Option")) / 2
        print width

        w = width
        r += "|id  |" + "Option".ljust(w) + "|Votes|\n"
        w = width - 2
        print w
        r += "|:--:|:" + "-"*w + ":|:" + "-"*3 + ":|\n"

        for o in self.options:
            w = width
            r += "|" + str(o.id).ljust(4) + "|" + o.text.ljust(w)+ "|" + str(o.count).ljust(5) + "|\n"

        return r

class VotingManager(object):
    def __init__(self):
        self.votings = dict()

    def get_voting(self, channel):
        try:
            return self.votings[channel]
        except KeyError:
            raise NoActiveVotingError()

    def new_voting(self, channel, topic):
        self.votings[channel] = Voting(topic)
