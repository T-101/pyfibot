# -*- encoding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import pytvmaze
from dateutil.parser import *
from dateutil.relativedelta import *
import pytz
from datetime import datetime

def command_maze(bot, user, channel, args):
    try:
        show = pytvmaze.get_show(show_name=args, embed='episodes')
    except pytvmaze.exceptions.ShowNotFound:
        print("Show '%s' not found" % args)

    next_episode = None
    next_delta = None

    now = datetime.now(pytz.timezone("Europe/Helsinki"))

    # go through the episodes in reverse order
    for episode in reversed(show.episodes):
        delta = relativedelta(parse(episode.airstamp), now)

        # episode is in the past, stop searching
        if delta.months <= 0 and \
           delta.days <= 0 and \
           delta.minutes <= 0:
               break
        else:
            # episode is (still) in the future
            next_episode = episode
            next_delta = delta

    # No new episodes found
    if not next_episode:
        # ended show, find latest episode
        if show.status == "Ended":
            next_episode = show.episodes.pop()
            latest_delta = relativedelta(now, parse(next_episode.airstamp))
        else:
            # Still running, ep airdate not yet known
            bot.say(channel, "No new episodes found for %s" % show.name)
            return


    show_id = "%s %s '%s'" % (show.name, "%dx%02d" % (next_episode.season_number, next_episode.episode_number), next_episode.title)

    if show.status == "Ended":
        msg = "Latest episode of %s aired on %s (%s ago) on %s" % (show_id, next_episode.airdate, _ago(latest_delta), show.network['name'])
    else:
        msg = "Next episode of %s airs %s (%s) on %s" % (show_id, next_episode.airdate, _ago(next_delta), show.network['name'])

    bot.say(channel, msg.encode("UTF-8"))

def _ago(delta, exact=False):
    delta_msg = []
    if delta.years != 0:
        delta_msg.append("%d years" % delta.years)
    if delta.months != 0:
        delta_msg.append("%d months" % delta.months)
    if delta.days != 0:
        delta_msg.append("%d days" % delta.days)

    if delta.years == 0 and delta.months == 0 and delta.days == 0:
        exact = True

    if exact:
        if delta.hours != 0:
            delta_msg.append("%d hours" % delta.hours)
        if delta.minutes != 0:
            delta_msg.append("%d minutes" % delta.minutes)

    return " ".join(delta_msg)
