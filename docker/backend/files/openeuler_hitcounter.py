#!/usr/bin/python3

"""
run this script with logstashdump:
"""

import re
import os
import logging
import argparse
from datetime import datetime
from requests.utils import unquote

# setup logging
logger = logging.getLogger(__name__)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s")
ch.setFormatter(fmt=fmter)
logger.addHandler(ch)

logline_regex = re.compile(
    r'(?P<ip_address>.*)\s+(?P<hostname>.*)\s+-\s+\[(?P<timestamp>.*)\]\s+"GET (?P<url>.*)\s+(?P<protocol>.*)"\s+(?P<code>\d+)'
    r'\s+(?P<bytes_sent>\d+)\s+"(?P<referer>.*)"\s+"(?P<content_encoding>.*)"\s+"(?P<agent>.*)"\s+'
    r'"(?P<xforward>.*)"', re.IGNORECASE)

base_regex = "/results/(?P<owner>[^/]*)/(?P<project>[^/]*)/(?P<chroot>[^/]*)/"
repomd_url_regex = re.compile(base_regex + "repodata/repomd.xml", re.IGNORECASE)
rpm_url_regex = re.compile(
    base_regex + r"(?P<build_dir>[^/]*)/(?P<rpm>[^/]*\.rpm)", re.IGNORECASE)

spider_regex = re.compile(
    '.*(ahrefs|bot/[0-9]|bingbot|borg|google|googlebot|yahoo|slurp|msnbot'
    '|openbot|archiver|netresearch|lycos|scooter|altavista|teoma|gigabot'
    '|blitzbot|oegp|charlotte|furlbot|http://client|polybot|htdig|ichiro'
    '|larbin|pompos|scrubby|searchsight|seekbot|semanticdiscovery|silk|snappy'
    '|spider|voila|vortex|voyager|zao|zeal|fast-webcrawler|converacrawler'
    '|msrbot|baiduspider|mogimogi|speedy|dataparksearch'
    '|findlinks|crawler|yandex|blexbot|semrushbot).*',
    re.IGNORECASE)

CHROOT_REPO_METADATA_STAT = 'chroot_repo_metadata_dl_stat'
CHROOT_RPMS_STAT = 'chroot_rpms_dl_stat'
PROJECT_RPMS_STAT = 'project_rpms_dl_stat'
KEY_SEPARATOR = '|'
REGEX_GROUP_OWNER = 'owner'
REGEX_GROUP_PROJECT = 'project'
REGEX_GROUP_CHROOT = 'chroot'

def url_to_key_strings(url):
    """
    Take a full URL and return a list of unique strings representing it,
    that copr-frontend will understand.
    """
    url_match = repomd_url_regex.match(url)
    if url_match:
        chroot_key = (
            CHROOT_REPO_METADATA_STAT,
            url_match.group(REGEX_GROUP_OWNER),
            url_match.group(REGEX_GROUP_PROJECT),
            url_match.group(REGEX_GROUP_CHROOT)
        )
        chroot_key_str = KEY_SEPARATOR.join(chroot_key)
        return [chroot_key_str]

    url_match = rpm_url_regex.match(url)
    if url_match:
        chroot_key = (
            CHROOT_RPMS_STAT,
            url_match.group(REGEX_GROUP_OWNER),
            url_match.group(REGEX_GROUP_PROJECT),
            url_match.group(REGEX_GROUP_CHROOT)
        )
        chroot_key_str = KEY_SEPARATOR.join(chroot_key)
        project_key = (
            PROJECT_RPMS_STAT,
            url_match.group(REGEX_GROUP_OWNER),
            url_match.group(REGEX_GROUP_PROJECT)
        )
        project_key_str = KEY_SEPARATOR.join(project_key)
        return [chroot_key_str, project_key_str]
    return []


def parse_log_file(path):
    """
    Take a log file and return its contents as a list of dicts.
    """
    with open(path, 'r') as logfile:
        content = logfile.readlines()

    accesses = []
    for line in content:
        m = logline_regex.match(line[1:-1].encode('utf-8').decode('unicode_escape'))
        if not m:
            continue

        access = m.groupdict()
        access["cs-uri-stem"] = access.pop("url")
        access["sc-status"] = access.pop("code")
        access["cs(User-Agent)"] = access.pop("agent")
        timestamp = datetime.strptime(access.pop("timestamp"),
                                      "%d/%b/%Y:%H:%M:%S %z")
        access["time"] = timestamp.strftime("%H:%M:%S")
        access["date"] = timestamp.strftime("%Y-%m-%d")
        accesses.append(access)
    return accesses


def get_arg_parser():
    """
    Generate argument parser for this script
    """
    name = os.path.basename(__file__)
    description = 'Read lighttpd access.log and count repo accesses.'
    parser = argparse.ArgumentParser(name, description=description)
    parser.add_argument(
        'logfile',
        action='store',
        help='Path to the input logfile')
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=("Print verbose information about what is going on"))
    return parser

def parse_dict(accesses):
    """
    Increment frontend statistics based on these `accesses`
    """
    result = get_hit_data(accesses)
    if not result:
        logger.debug("No recognizable hits among these accesses, skipping.")
        return

    logger.debug("Hits: %s", result["hits"])

def get_hit_data(accesses):
    """
    Prepare body for the frontend request in the same format that
    copr_log_hitcounter.py does.
    """
    hits = {}
    timestamps = []
    for access in accesses:
        url = access["cs-uri-stem"]

        if access["sc-status"] == "404":
            logger.debug("Skipping: %s (404 Not Found)", url)
            continue

        if access["cs(User-Agent)"].startswith("Mock"):
            logger.debug("Skipping: %s (user-agent: Mock)", url)
            continue

        bot = spider_regex.match(access["cs(User-Agent)"])
        if bot:
            logger.debug("Skipping: %s (user-agent '%s' is a known bot)",
                      url, bot.group(1))
            continue

        # Convert encoded characters from their %40 values back to @.
        url = unquote(url)

        # I don't know how or why but occasionally there is an URL that is
        # encoded twice (%2540oamg -> %40oamg - > @oamg), and yet its status
        # code is 200. AFAIK these appear only for EPEL-7 chroots and their
        # User-Agent is something like urlgrabber/3.10%20yum/3.4.3
        # I wasn't able to reproduce such accesses, and we decided to not count
        # them
        if url != unquote(url):
            logger.warning("Skipping: %s (double encoded URL, user-agent: '%s', "
                        "status: %s)", access["cs-uri-stem"],
                        access["cs(User-Agent)"], access["sc-status"])
            continue

        # We don't want to count every accessed URL, only those pointing to
        # RPM files and repo file
        key_strings = url_to_key_strings(url)
        if not key_strings:
            logger.debug("Skipping: %s", url)
            continue

        found = False
        for x in key_strings:
            if x.startswith("chroot_rpms_dl_stat|") and x.endswith("|srpm-builds"):
                found = True
                break
        if found:
            logger.debug("Skipping %s (SRPM build)", url)
            continue

        logger.info("Processing: %s", url)

        # When counting RPM access, we want to iterate both project hits and
        # chroot hits. That way we can get multiple `key_strings` for one URL
        for key_str in key_strings:
            hits.setdefault(key_str, 0)
            hits[key_str] += 1

        # Remember this access timestamp
        datetime_format = "%Y-%m-%d %H:%M:%S"
        datetime_string = "{0} {1}".format(access["date"], access["time"])
        datetime_object = datetime.strptime(datetime_string, datetime_format)
        timestamps.append(int(datetime_object.timestamp()))

    return {
        "ts_from": min(timestamps),
        "ts_to": max(timestamps),
        "hits": hits,
    } if hits else {}

def main():
    "Main function"
    parser = get_arg_parser()
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # If the access.log gets too big, sending it all at once to frontend will
    # timeout. Let's send it in chunks.
    # The issue is, there is no transaction mechanism, so theoretically some
    # chunks may succeed, some fail and never be counted. But we try to send
    # each request repeatedly and losing some access hits from time to time
    # isn't a mission critical issue and I would just roll with it.
    accesses = parse_log_file(args.logfile)
    parse_dict(accesses)



if __name__ == "__main__":
    main()
