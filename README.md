# Evil Corp Activity Tracker

Executes a JQL query and exports insight about status changes of the query's results to a CSV file.

## Requirements

- Python 3
- Python JIRA (pip install jira) : https://jira.readthedocs.io/en/master/

## Usage

ecat.py (JQL String) --config private.json --output sep2019.csv --prefix https://youilabs.atlassian.net/browse

- JQL string : JQL 
- config : JSON file containing credentials (see below)
- output : csv file to output to, will overwrite
- prefix : URL to prepend to any issue to build a URL to the issue
- page_size : Number of issues to fetch per query

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
- fields and headers are hardcoded