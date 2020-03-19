# Evil Corp Activity Tracker

Executes a JQL query and exports it to a CSV file.

## Requirements

- Python 3
- Python JIRA (pip install jira) : https://jira.readthedocs.io/en/master/

## Usage

ecat.py (JQL String) --config private.json --output sep2019.csv --prefix https://youilabs.atlassian.net/browse

- JQL string : JQL 
- config : JSON file containing credentials (see below)
- output : csv file to output to, will overwrite
- prefix : URL to prepend to any issue to build a URL to the issue

## Limitations
- Probably tied to our JIRA schema

## Config

{
  "jira_server" : "YOUR_SERVER",
  "jira_user" : "YOUR_USERNAME",
  "jira_apikey" : "see https://id.atlassian.com/manage-profile/security",
  "browse_url_prefix" : "https://company.atlassian.net/browse/"
}

## TODO
- could probably page query if you weren't evil
- fields and headers are hardcoded