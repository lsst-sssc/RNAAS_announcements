
# import the requests package and set your token in a variable for later use
import requests, os
from urllib.parse import urlencode, quote_plus
import json
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

keywords=['asteroid', "'main-belt comets'", "'centaur group'", 'centaurs', "'near-sun comets'", "'asteorid belt'", "'comet tails'",  'asteroids', 'Solar System', 'comet', 'comets', "'Small Solar System bodies'", 'comae', "'Kuiper belt'", "'Near-Earth objects'", "'Main belt asteroids'", "'asteroid surfaces'"]

oldIds_file = Path("./bibIDS.csv")
ndays=90
token=os.environ['ADS_TOKEN']
outtxt="./newRNAAS.txt"

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
		bibcodes.append(x['bibcode'])


	looked_at_today=np.asarray(bibcodes, dtype=str)

bibcodes=np.asarray(bibcodes, dtype=str)

np.savetxt(oldIds_file, bibcodes, delimiter=',',fmt='%s',header='bibcodes_published')   # X is an array
fout.close()
