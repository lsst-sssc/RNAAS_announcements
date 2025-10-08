# RNAAS_announcements
Python script to check RNAAS for new relevant research notes

The aim of the script is to use the ADS API to announce new relevant AAS Research Notes that hasve been recently published. 

**The python scripts assume that you have a SOLSYS_RNAAS_SLACK_POST_URL environment variable with your slack app webhook token (https://api.slack.com/messaging/webhooks).**

**The ADS version requires ADS_TOKEN environment variable set with your ADS API token (https://ui.adsabs.harvard.edu/user/settings/token).** 

Output posted to slack channel (console if slack URL is not provided)
