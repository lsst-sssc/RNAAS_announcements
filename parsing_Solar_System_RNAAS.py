
# import the requests package and set your token in a variable for later use
import requests, os
from urllib.parse import urlencode, quote_plus
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

keywords=['asteroid', "'main-belt comets'", "'centaur group'", 'centaurs', "'near-sun comets'", "'asteroid belt'", "'comet tails'",  'asteroids', 'Solar System', 'comet', 'comets', "'Small Solar System bodies'", 'comae', "'Kuiper belt'", "'Near-Earth objects'", "'Main belt asteroids'", "'asteroid surfaces'"]

oldIds_file = Path("./bibIDS.csv")
ndays=90
token=os.environ['ADS_TOKEN']
outtxt="./newRNAAS.txt"

# message designed with Slack's block kit builder
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

"""
        {
            "type": "section",
            "text": {
                "text": "{n_images} image{plural_images} and {n_targets} target{plural_targets} processed in the past 24 hours.",
                "type": "mrkdwn"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "C/2022 E3   r=13.1 ± 0.03\n22P   g 11.14 ± 0.12"
            }
        }
    ]
}
"""

no_articles_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "text": f"*Solar System RNAAS daily summary*",
                "type": "mrkdwn"
            }
        },
        {
            "type": "section",
            "text": {
                "text": f"No articles found in the past {ndays} days.",
                "type": "mrkdwn"
            }
        },
    ]
}

fout=open(outtxt, 'w')

#check if there a stored search
old_bibIDs=[]

if oldIds_file.is_file():
    print('reading in previous file of outputted bibIds')
    old_bibIDs=np.genfromtxt(oldIds_file, dtype=str, skip_header=1)
else:
    old_bibIDs=np.zeros(1,str)

print(old_bibIDs)
bibcodes=[]
looked_at_today=np.zeros(1,str)


# get the current date and time
now = datetime.now()
print(now.month, now.year)

before=now- timedelta(days=ndays)
print(before.month, before.year)

slack_list = []
for keyword in keywords:
    # search by bibstem, return the title
    print('searching '+keyword)
    encoded_query = urlencode({"q": "bibstem:RNAAS pubdate:["+str(before.year)+'-'+str(before.month)+" TO "+str(now.year)+'-'+str(now.month)+"] keyword:"+keyword, "fl": "author, title, bibcode, doi"})
    results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}".format(encoded_query),                        headers={'Authorization': 'Bearer ' + token})

    query_results=results.json()


    for x in query_results['response']['docs']:
        w= (x['bibcode'] == old_bibIDs)

        wh= (x['bibcode'] == looked_at_today)

        print('Initial RNAAS match', x['author'][0],', ', x['bibcode'], ', ',x['title'][0], "https://iopscience.iop.org/article/"+x['doi'][0] )

        if (len(old_bibIDs[w]) == 0) and (len(looked_at_today[wh]) ==0) :
            print('New RNAAS', x['author'][0],', ', x['bibcode'], ', ',x['title'][0], "https://iopscience.iop.org/article/"+x['doi'][0] )
            fout.write("New RNAAS, "+x['author'][0]+', '+x['bibcode']+ ', '+x['title'][0]+" ,"+ " https://iopscience.iop.org/article/"+x['doi'][0]+"\n" )
            slack_list.append("{author[0]:}, {bibcode[0]:}, <https://iopscience.iop.org/article/{doi[0]:}|{title[0]:}>".format(**x))
        bibcodes.append(x['bibcode'])


    looked_at_today=np.asarray(bibcodes, dtype=str)

bibcodes=np.asarray(bibcodes, dtype=str)

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
    slack_message['blocks'].append(
        {
            "type": "section",
            "text": {
                "text": f"{len(slack_list)} new article{'' if len(slack_list) == 1 else 's'} found:",
                "type": "mrkdwn"
            },
        },
        {
            "type": "section",
            "text": {
                "text": "\n".join(slack_list),
                "type": "mrkdwn"
            },
        }
    )

np.savetxt(oldIds_file, bibcodes, delimiter=',',fmt='%s',header='bibcodes_published')   # X is an array
fout.close()

# post to slack
