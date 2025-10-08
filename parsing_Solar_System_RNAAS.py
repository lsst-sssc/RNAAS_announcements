"""

Required environment variables:
  SOLSYS_RNAAS_SLACK_POST_URL (https://api.slack.com/messaging/webhooks)

"""

import requests, os
import json
from astropy.time import Time
from datetime import datetime, timezone
import feedparser

months={"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12  }

url="https://iopscience.iop.org/journal/rss/2515-5172"


slack_post_url = os.getenv("SOLSYS_RNAAS_SLACK_POST_URL")
slack_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "text": "*Solar System, Exoplanets, and Astrobiology Corridor RNAAS daily summary*",
                "type": "mrkdwn"
            }
        },
    ]
}

# get the current date and time

today = datetime.now(tz=timezone.utc)
ut_today= Time(f"{today.year}-{today.month}-{today.day}", format="iso", scale='utc')


feed = feedparser.parse(url)
 
slack_list = []
dois= set()


for rss_item in feed.entries:
    
    if ( rss_item["aas_corridor"]  == 'The Solar System, Exoplanets, and Astrobiology'):
        title =rss_item['title'] 
        link=rss_item['link']
        authors=rss_item['authors'][0]['name']
        doi=rss_item["prism_doi"]
        publication_date=rss_item["prism_coverdisplaydate"]
        pdf_link=rss_item['iop_pdf'].replace("pdf", "ampdf")
        #ampdf is what's needed on my browser to load the PDF
        print(authors)
        print(rss_item['dc_source'])
    
        
        published_str=rss_item['prism_coverdisplaydate'][-4:]
        
        for i in months.keys():
            if(rss_item['prism_coverdisplaydate'].find(i)>=0):
               published_str=published_str+'-'+str(months[i])+'-'+rss_item['prism_coverdisplaydate'][0:2]
            
        
       
        print(published_str)
        published= Time(published_str, format="iso", scale='utc')

        dt=ut_today.jd-published.jd
        
     
        if dt <=2:

            slack_title=f"<{link}|{title}>"
            slack_pdf_link=f"<{pdf_link}|AAS-hosted PDF>"
            slack_list.append(f"• {slack_title} {authors} {publication_date} {slack_pdf_link}")
           # print(f"• {slack_title} {authors} {publication_date} {slack_pdf_link}")
            #print(dt)


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
