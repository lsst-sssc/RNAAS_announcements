# RNAAS_announcements
Python script to check RNAAS for new relevant research notes

The aim of the script is to use the ADS API to announce new relevant AAS Research Notes that hasve been recently published. 

**The python script assumes that you have set ADS_TOKEN and SOLSYS_RNAAS_SLACK_POST_UR environment variable with your ADS API token ((https://ui.adsabs.harvard.edu/user/settings/token) and the slack app webhook token (https://api.slack.com/messaging/webhooks).**

Output will be printed in newRNAAS.txt and also to the slack channel (console if slack URL is not provided)
