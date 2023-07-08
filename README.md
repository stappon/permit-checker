# recreation.gov backcountry permit checker

Checks for available backcountry permits and email when new ones are found.

The main script runs forever and polls every 60 seconds. It's intended to be run as a background service on a machine that's always online. The `permit_checker` module contains all the actual functionality and could be re-used in other contexts.

This does not work for all permits. recreation.gov uses different endpoints for different permits, and so far I've only added support for the ones I've personally needed. Currently this supports all permits that use the `permit_itinerary` endpoint, plus Inyo National Forest and Mt Whitney (which use a special `permits_inyo` endpoint).

Requires Python 3.8+ due to usage of protocols.

## Usage
* Create and activate virtual environment
* Install requirements.txt
* Define environment variables for email notifications
    * `PERMIT_EMAIL_SENDER` and `PERMIT_EMAIL_PASSWORD`: The email account and password used to send notifications. I've been using a free-tier Mailgun account, plus a filter in my gmail to mark it as non-spam.
    * `PERMIT_EMAIL_RECIPIENT`: The email address to which notifications are sent.
* Run `main.py` with desired permit parameters:
    * `--id`: Permit IDs can be found by loading the permit page in your browser and looking for the ID in the URL.
    * `--divisions`: A "division" is a more-specific location or type under the umbrella of a given permit ID. For instance, Mt Whitney has day use and overnight divisions, and each backcountry campsite within Bryce National Park is its own division under the same permit ID. There is not a consistent way to see division IDs in the recreation.gov UI. You will need to load your browser dev tools, query for the permit you want, and examine the availability request/response.
    * `--earliest`: The earliest start date you'll accept (YYYY-mm-dd)
    * `--latest`: The latest start date you'll accept (YYYY-mm-dd). If omitted, will default to same value as `--earliest`.
    * `--secs`: How often, in seconds, to poll for new results. Default is 60, or 5 when in test mode.
    * `--test`: Optional flag. Intended for examining debug logs without sending any emails.

### Examples I'm currently running
Mt Whitney day use:
`python main.py --id 4675320 --divisions 4675320127 4675320129 4675320130 4675320131 --earliest 2023-08-05 --latest 2023-08-07 --people 2 --test`

Rocky Mountains East Inlet along Pfiffner Traverse:
`python main.py --id 445860 --divisions 406 --earliest 2023-09-20 --latest 2023-10-30 --people 2`                   `

## Tests
`$python -m pytest` from repo root

## mypy
`python -m mypy .` from repo
