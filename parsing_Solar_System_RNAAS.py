"""

Required environment variables:
  ADS_TOKEN (https://ui.adsabs.harvard.edu/user/settings/token)
  SOLSYS_RNAAS_SLACK_POST_URL (https://api.slack.com/messaging/webhooks)

"""

import requests, os
from urllib.parse import urlencode
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

keywords=['asteroid', "'main-belt comets'", "'centaur group'", 'centaurs', "'near-sun comets'", "'asteroid belt'", "'comet tails'",  'asteroids', 'Solar System', 'comet', 'comets', "'Small Solar System bodies'", 'comae', "'Kuiper belt'", "'Near-Earth objects'", "'Main belt asteroids'", "'asteroid surfaces'"]

oldIds_file = Path("./bibIDS.csv")
ndays=90
token=os.environ['ADS_TOKEN']
outtxt="./newRNAAS.txt"

slack_post_url = os.getenv("SOLSYS_RNAAS_SLACK_POST_URL")
slack_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "text": f"*Solar System RNAAS daily summary*",
                "type": "mrkdwn"
            }
        },
    ]
}


def quote_for_slack(s):
    return s.replace("<", "&lt;").replace(">", "&gt;")


fout=open(outtxt, 'w')

#check if there a stored search
old_bibcodes = set()

if oldIds_file.is_file():
    print('reading in previous file of outputted bibIds')
    old_bibcodes = set(np.genfromtxt(oldIds_file, dtype=str, skip_header=1))

print(old_bibcodes)


# get the current date and time
now = datetime.now()
print(now.month, now.year)

before=now- timedelta(days=ndays)
print(before.month, before.year)

slack_list = []
bibcodes = set()
for keyword in keywords:
    # search by bibstem, return the title
    print('searching '+keyword)
    encoded_query = urlencode({"q": "bibstem:RNAAS pubdate:["+str(before.year)+'-'+str(before.month)+" TO "+str(now.year)+'-'+str(now.month)+"] keyword:"+keyword, "fl": "author, title, bibcode, doi"})
    results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query),                        headers={'Authorization': 'Bearer ' + token})

    query_results=results.json()

    for x in query_results['response']['docs']:
        print('Initial RNAAS match', x['author'][0],', ', x['bibcode'], ', ',x['title'][0], "https://iopscience.iop.org/article/"+x['doi'][0] )

        if x['bibcode'] not in set.union(bibcodes, old_bibcodes):
            print('New RNAAS', x['author'][0],', ', x['bibcode'], ', ',x['title'][0], "https://iopscience.iop.org/article/"+x['doi'][0] )
            fout.write("New RNAAS, "+x['author'][0]+', '+x['bibcode']+ ', '+x['title'][0]+" ,"+ " https://iopscience.iop.org/article/"+x['doi'][0]+"\n" )
            slack_list.append(
                "• {author[0]:}, {bibcode:}, <https://iopscience.iop.org/article/{doi[0]:}|{quoted_title:}>"
                .format(
                    quoted_title=quote_for_slack(x["title"][0]),
                    **x
                )
            )

        bibcodes.add(x['bibcode'])

np.savetxt(oldIds_file, list(bibcodes), delimiter=',',fmt='%s',header='bibcodes_published')   # X is an array
fout.close()

# format slack message and post
if len(slack_list) == 0:
    slack_message['blocks'].append(
        {
            "type": "section",
            "text": {
                "text": "No new articles found.",
                "type": "mrkdwn"
            }
        }
    )
else:
    slack_message['blocks'].extend(
        [
            {
                "type": "section",
                "text": {
                    "text": f"{len(slack_list)} new article{'' if len(slack_list) == 1 else 's'} found.",
                    "type": "mrkdwn"
                },
            },
            {
                "type": "section",
                "text": {
                    "text": "\n".join(slack_list),
                    "type": "mrkdwn"
                },
            },
        ]
    )

if slack_post_url is None:
    print("\nSOLSYS_RNAAS_SLACK_POST_URL is not defined, printing Slack message:\n")
    print(json.dumps(slack_message, indent=2))
else:
    r = requests.post(slack_post_url, data=json.dumps(slack_message))
    if r.status_code == 200:
        print("Posted to Slack.")
    else:
        print("Error posting to Slack.")
