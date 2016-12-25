#!/usr/bin/env python2

from tabulate import tabulate

import config
from response import Response

class VotingException(Exception):
    pass

class VotingAlreadyStartedError(VotingException):
    pass

class OptionNotFoundError(VotingException):
    pass

class UserAlreadyVotedError(VotingException):
    pass

class NoActiveVotingError(VotingException):
    pass

class MissingArgumentsError(VotingException):
    pass

class Option(object):
    def __init__(self, text, i):
        if len(text) <= 0:
            raise MissingArgumentsError("Option text can't be empty")
        self.text = text
        self.count = 0
        self.id = i

    def vote(self, voter):
        self.count += 1

class Voting(object):
    STATE_PREPARING = 0
    STATE_RUNNING = 1

    def __init__(self, topic):
        if len(topic) <= 0:
            raise MissingArgumentsError("Topic needed")
        self.topic = topic
        self.state = Voting.STATE_PREPARING
        self.options = list()
        self.voters = list()

    def add_option(self, text):
        if self.state > Voting.STATE_PREPARING:
            raise VotingAlreadyStartedError("Voting already started")
        i = len(self.options) + 1
        self.options.append(Option(text, i))
        return i

    def start(self):
        if self.state > Voting.STATE_PREPARING:
            raise VotingAlreadyStartedError("Voting already started")
        self.state = Voting.STATE_RUNNING

    def restart(self):
        self.options = list()

    def vote(self, option_number, voter):
        try:
            option = self.options[option_number - 1]
        except IndexError:
            raise OptionNotFoundError("Option {} not found".format(option_number))

        if voter in self.voters:
            raise UserAlreadyVotedError("User already voted")
        self.voters.append(voter)
        option.vote(voter)

    def get_results(self):
        results = []
        for o in self.options:
            results.append([o.id, o.text, o.count])
        return results

class VotingManager(object):
    def __init__(self):
        self.votings = dict()

    def get_voting(self, channel):
        try:
            return self.votings[channel]
        except KeyError:
            raise NoActiveVotingError("No active voting")

    def new_voting(self, channel, topic):
        self.votings[channel] = Voting(topic)

    def help(self):
        return """
Start a new voting:
{0} new topic

add options to voting:
{0} add name

vote (users can only vote once):
{0} vote #id

show results:
{0} show
""".format(config.vote_command)

    def handle(self, request):
        if not request.text:
            return Response(self.help())

        text = request.text[0].strip()
        channel = request.channel_id[0].strip()
        args = text.split(' ')

        try:
            if len(args) == 0 or args[0] == 'help':
                return Response(self.help())

            elif args[0] == 'new':
                if len(args) < 2:
                    raise MissingArgumentsError("Topic needed")
                topic = ' '.join(args[1:])
                self.new_voting(channel, topic)
                return Response("Vote \"{}\" created".format(topic))

            elif args[0] == 'show' or args[0] == 'results':
                v = self.get_voting(channel)
                results = v.get_results()
                return Response(tabulate(results, ["id", "Text", "Votes"], tablefmt='pipe'))

            elif args[0] == 'add':
                v = self.get_voting(channel)
                if len(args) < 2:
                    raise MissingArgumentsError("Name needed")
                text = ' '.join(args[1:])
                i = v.add_option(text)
                return Response("Option \"{}\" with id {} added".format(text, i))

            elif args[0] == 'vote':
                v = self.get_voting(channel)
                if len(args) < 2:
                    raise MissingArgumentsError("what do you want to vote?")
                try:
                    i = int(args[1])
                except ValueError:
                    raise MissingArgumentsError("Thats not an option id")

                v.vote(i, request.user_name[0])
                return Response("Voted")

        except VotingException as e:
            return Response("Error: "+ str(e))


        return Response("Error: Unknown command: {}".format(args[0]))


vm = VotingManager()

def handle(request):
    global vm
    return vm.handle(request)
