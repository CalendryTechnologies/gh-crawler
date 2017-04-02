#! /usr/bin/env python

#TODO Current Issues:
# * If a time is not specified for the second date (as in prom setup) the stop datetime is not recorded
# * The date is not carried over from the start time so the stop time defaults to today if there is none provided
# * It may be better to explore the single page about the event which has more details
#  * More steps to get to the item means more could go wrong
#  * More requesting time since each event will be it's own request on top of the ones already requested for lists

from lxml import html
import requests
import json

from datetime import datetime
import dateutil.parser as dateutil #TODO actually use this


def startstop(startstr, stopstr):
    '''
    Extracts start and stop datetimes from strings
    :param startstr: String denoting start datetime
    :param stopstr: String denoting stop datetime (some information may be assumed from startstr)
    '''
    try:
        start = dateutil.parse(startstr, fuzzy=True)
        try:
            stop = dateutil.parse(stopstr, fuzzy=True)
            #TODO make sure each attribute is larger in order from year down (to prevent things like January 1, 2018 < December 31, 2017)

            return startstr, stopstr
        except ValueError:
            print('Unable to parse stop string "%s"' % stopstr)
    except ValueError:
        print('Unable to parse start string "%s"' % startstr)

if __name__ == "__main__":
    pg_num = 1
    done = False #have we finished looping through pages
    datetime_parse_fmt = "%B %-d @ %I:%M %p" #format string for getting datetime object
    datetime_fmt = "%m/%d/%Y %H:%M:%S" #format datetime should be in for standardization
    event_list = [] #list of events to be put together (each event will be dictionary)

    #TODO TODO TODO do not restrict pages in real deal
    while not done: # and pg_num <= 3:
        #Loop through all pages of the calendar

        page = requests.get('https://www.hartsvillesc.gov/calendar/?action=tribe_photo&tribe_paged=%d&tribe_event_display=photo' % pg_num)
        tree = html.fromstring(page.content)

        events = tree.xpath('//div[contains(@class,"type-tribe_events")]')
        notices = tree.xpath('//div[contains(@class,"tribe-events-notices")]/ul/li/text()')

        done = False
        for notice in notices:
            if "no results" in notice.lower():
                done = True

        if len(events) == 0:
            done = True
        else:
            for event in events:
                titles = event.xpath('.//h2[contains(@class,"tribe-events-list-event-title")]/a/text()')
                starts = event.xpath('.//span[contains(@class,"tribe-event-date-start")]/text()')
                stops = event.xpath('.//span[contains(@class,"tribe-event-time")]/text()')
                descriptions = event.xpath('.//div[contains(@class,"tribe-events-content")]/p/text()')
                links = event.xpath('.//a[contains(@class,"tribe-event-url")]/@href')
                #TODO use link to get more information and possibly use lxml function to replace relative urls to help following

                new_event = {}
                if len(titles) <= 0:
                    break #All items must have a title
                else:
                    new_event["title"] = titles[0].strip()

                if len(starts) > 0:
                    startstr = starts[0].strip()
                    try:
                        try_datetime = dateutil.parse(startstr, fuzzy=True)
                        output_datetime = datetime.strftime(try_datetime, '%m/%d/%Y %H:%M:%S')
                        new_event["start"] = output_datetime
                    except: #TODO don't just exept everything
                        print("Unable to parse start string '%s'" % startstr)
                    new_event["startstr"] = startstr

                if len(stops) > 0:
                    stopstr = stops[0].strip()
                    try:
                        try_datetime = dateutil.parse(stopstr, fuzzy=True)
                        output_datetime = datetime.strftime(try_datetime, '%m/%d/%Y %H:%M:%S')
                        new_event["stop"] = output_datetime
                    except: #TODO don't just exept everything
                        print("Unable to parse stop string '%s'" % stopstr)
                    new_event["stopstr"] = stopstr

                if len(descriptions) > 0:
                    new_event["description"] = descriptions[0].strip()

                if len(links) > 0:
                    new_event["link"] = links[0].strip()

                event_list.append(new_event)

        pg_num += 1

    json_text = json.dumps(event_list, indent=4)
    with open("hartsvillesc-test.json", "w+") as fp:
        fp.write(json_text)
