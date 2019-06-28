#!/usr/bin/env python3

import json
from datetime import datetime, timezone
import time
import argparse
import sys
import logging
import os

from dateutil import parser as dt_parser
import boto3


def get_session(aws_profile):
    global saved_sessions
    if aws_profile not in saved_sessions:
        saved_sessions[aws_profile] = boto3.Session(profile_name=aws_profile)

    return saved_sessions[aws_profile]


def add_to_one_graph(args, widget):
    if "annotations" not in widget['properties']:
        widget['properties']["annotations"] = {}

    if "vertical" not in widget['properties']["annotations"]:
        widget['properties']["annotations"]['vertical'] = []

    annotation = [
        {
            "label": "START %s" % args.label,
            "value": args.start
        },
        {
            "value": args.end,
            "label": "END %s" % args.label
        }
    ] if args.end else {
        "label": args.label,
        "value": args.start
    }
    widget['properties']["annotations"]['vertical'].append(annotation)


def update_one_board(board_name, args, backup_filename):
    logger.debug("Getting board: %s", board_name)
    cf = get_session(args.aws_profile).client('cloudwatch')
    db = cf.get_dashboard(
        DashboardName=board_name
    )

    body = json.loads(db['DashboardBody'])
    logger.debug("Dashboard before change: %s", body)

    if not args.dry_run:
        logger.debug("Backing up old dashboard to: %s", backup_filename)
        with open(backup_filename, 'w') as f:
            f.write(json.dumps(body, indent=2))
        print("Old dashboard backed up at: ", backup_filename)

    for widget in body['widgets']:
        if "metric" == widget["type"]:
            add_to_one_graph(args, widget)

    if args.dry_run:
        print("Preview of annotated board:")
        print(json.dumps(body))
        print("DRY RUN: Board not updated.")
    else:
        new_body = json.dumps(body)
        logger.debug("new_body: %s", new_body)
        resp = cf.put_dashboard(
            DashboardName=board_name,
            DashboardBody=new_body
        )
        logger.debug("put_dashboard() response: %s", resp)

    logger.debug("Done with board: %s", board_name)


def add_annotation(args):
    curr_time = int(time.time())
    for board_name in args.boards:
        update_one_board(board_name, args, os.path.realpath("./%s_%d_backup.json" % (board_name, curr_time)))


def acceptable_timestamp(s):
    try:
        d1 = dt_parser.isoparse(s)
        d_utc = datetime.fromtimestamp(d1.timestamp(), timezone.utc)
        logger.debug("%s, %s, %s, %s", s, d1, d_utc, d_utc.strftime("%Y-%m-%dT%H:%M:%SZ"))
        return datetime.fromtimestamp(dt_parser.isoparse(s).timestamp(), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        print("Error parsing '{}': {}".format(s, str(e)), file=sys.stderr)
        print("Expected timestamp format is ISO, as supproted by dateutil.parser.isoparse()", file=sys.stderr)
        raise e


def parse_args():
    epilog = '''

EXAMPLES:
$ {prog} --aws-profile staging \\
         --board-name ApiDashboard \\
         --color '#BBBBBB' \\
         --label 'SM-741 deployment' \\
         --start '2018-11-05T22:44:00+0530' \\
         --end '2018-11-05T20:00:00+0530'
$ {prog} -b ApiDashboard \\
         -l 'Deployment Release 2.03' \\
         -s '2018-11-05 22:44:00'
$ {prog} -b ApiDashboard \\
         -l 'Deployment Release 2.03' \\
         -s '2018-11-05 22:44:00' \\
         --dry-run --verbose
    '''.format(prog=sys.argv[0])
    parser = argparse.ArgumentParser(description='Add vertical annotation to all graphs of one or more dashboards.',
                                     epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)

    required_args = parser.add_argument_group('required arguments')
    parser.add_argument('--aws-profile', '-p',
                        help='Name of aws-profile to use to connect. See https://docs.aws.amazon.com/cli/latest/'
                             'userguide/cli-multiple-profiles.html. (default: default)', default='default')
    required_args.add_argument('--boards', '-b', type=str, nargs='+', help='Space separated list of board names.',
                               required=True)
    required_args.add_argument('--start', '--timestamp', '-s', type=acceptable_timestamp,
                               help='Start time of a range to fill, or the time for a single annotation.',
                               required=True)

    parser.add_argument('--end', '-e', type=acceptable_timestamp, help='End time for fill range.', required=False)
    parser.add_argument('--label', '-l', type=str, help='Annotation label. (default: Deployment)', default='Deployment',
                        required=False)
    parser.add_argument('--color', '-c', type=str, help='Fill color for range. (default: #DD9999)', default='#DD9999',
                        required=False)
    parser.add_argument('--dry-run', '-d', help='Print updated board json, but make no changes.', default=False,
                        required=False, action="store_true")
    parser.add_argument('--verbose', '-v', help='Log debug information.', default=False, required=False,
                        action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("cli args    : %s", sys.argv)
    logger.debug("parsed args : %s", args)

    return args


logPath = os.path.realpath('./add_annotation.log')
logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.CRITICAL,
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(logPath)])
logger = logging.getLogger('add_annotation')
saved_sessions = {}
logger.info("Log file: %s", logPath)

if "__main__" == __name__:
    add_annotation(parse_args())
