# aws-cw-utils
AWS Cloudwatch Utilities

# add_annotations

Add a vertical annotation to all graphs in one or more dashboards.

## TL;DR
```
# Add single vertical line to all graphs of board1 and board2 at given time
$ add_annotation.py -b board1 board2 -s '2019-01-01T11:22:00+05:30'

# Do a dry run, print the new board JSON source instead of updating it.
$ add_annotation.py -b board1 board2 -s '2019-01-01T11:22:00+05:30'

# Add a vertical range/bar from start to end time, filled with RED, to all graphs of board1 and board2
$ add_annotation.py --boards board1 board2 -l "maintanance-window" --color "#FF0000" \
                    --start '2019-01-01T11:00:00+05:30' --end '2019-01-01T12:00:00+05:30'

# Use an AWS profile other than default
$ add_annotation.py --aws-profile staging-env -b board1 board2 -s '2019-01-01T11:22:00+05:30'
```

## Usage
```
usage: add_annotation.py [-h] [--aws-profile AWS_PROFILE] --boards BOARDS
                         [BOARDS ...] --start START [--end END]
                         [--label LABEL] [--color COLOR] [--dry-run]
                         [--verbose]

Add vertical annotation to all graphs of one or more dashboards.

optional arguments:
  -h, --help            show this help message and exit
  --aws-profile AWS_PROFILE, -p AWS_PROFILE
                        Name of aws-profile to use to connect. See https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html. (default: default)
  --end END, -e END     End time for fill range.
  --label LABEL, -l LABEL
                        Annotation label. (default: Deployment)
  --color COLOR, -c COLOR
                        Fill color for range. (default: #DD9999)
  --dry-run, -d         Print updated board json, but make no changes.
  --verbose, -v         Log debug information.

required arguments:
  --boards BOARDS [BOARDS ...], -b BOARDS [BOARDS ...]
                        Space separated list of board names.
  --start START, --timestamp START, -s START
                        Start time of a range to fill, or the time for a single annotation.

EXAMPLES:
$ ./add_annotation.py --aws-profile staging \
         --board-name ApiDashboard \
         --color '#BBBBBB' \
         --label 'SM-741 deployment' \
         --start '2018-11-05T22:44:00+0530' \
         --end '2018-11-05T20:00:00+0530'
$ ./add_annotation.py -b ApiDashboard \
         -l 'Deployment Release 2.03' \
         -s '2018-11-05 22:44:00'
$ ./add_annotation.py -b ApiDashboard \
         -l 'Deployment Release 2.03' \
         -s '2018-11-05 22:44:00' \
         --dry-run --verbose
```
