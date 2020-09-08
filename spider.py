import urllib.error
import ssl
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import json
import sqlitedb
import os

import settings

WEB_SITE = os.getenv("website")
DATABSE = os.getenv("db")

with open('config.json', 'r') as f:
    config = json.load(f)

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if DATABSE is not None:
    db = sqlitedb.DB(config['datastorage'][DATABSE])
else:
    db = sqlitedb.DB(config['datastorage'][sys.argv[2]])

webs = list()

row = db.select(
    'SELECT id,url FROM Pages WHERE html is NULL ORDER BY RANDOM() LIMIT 1', 1)

if row is not None:
    print("Restarting existing crawl.  Remove recipe.sqlite to start a fresh crawl.")
    tlbwebs = db.select('SELECT url FROM Webs', "all")
    webs = [row[0] for row in tlbwebs]

else:
    print("Starting new crawl...........")
    if WEB_SITE is not None:
        starturl = config['wrapsrc'][WEB_SITE]['website']
    else:
        starturl = config['wrapsrc'][sys.argv[1]]['website']
        
    web = starturl
    if (starturl.endswith('.htm') or starturl.endswith('.html')):
        pos = starturl.rfind('/')
        web = starturl[:pos]

    stament = []
    if (len(web) > 1):
        webs.append(web)
        stament.append(
            'INSERT OR IGNORE INTO Webs (url) VALUES ("{}")'.format(web))
        stament.append(
            'INSERT OR IGNORE INTO Pages (url, html) VALUES ("{}", NULL)'.format(starturl))
        db.executes(stament)
        db.commit()

# Get the current webs

print(webs)

many = 0
while True:
    # if ( many < 1 ) :
    ##    sval = input('How many pages:')
    # if ( len(sval) < 1 ) :
    # break
    ##    many = int(sval)
    ##many = many - 1

    try:

        row = db.select(
            'SELECT id,url FROM Pages WHERE html is NULL ORDER BY RANDOM() LIMIT 1', "one")
        # print row
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        many = 0
        break

    print(fromid, url, end=' ')

    try:
        document = urlopen(url, context=ctx)
        html = document.read()

        if 'text/html' != document.info().get_content_type():
            print("Ignore non text/html page")

            db.executes('DELETE FROM Pages WHERE url="{}"'.format(url))
            db.commit()
            # cur.execute('DELETE FROM Pages WHERE url=?', (url, ))
            # conn.commit()
            continue

        print('('+str(len(html))+')', end=' ')
        soup = BeautifulSoup(html, "html.parser")

    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break

    except:
        print("Unable to retrieve or parse page")
        continue

    statement = []
    statement.append(
        'INSERT OR IGNORE INTO Pages (url, html) VALUES ("{}", NULL)'.format(url))
    statement.append(
        'UPDATE Pages SET html={} WHERE url="{}"'.format(html.decode("utf-8"), url))

    db.executes(stament)
    db.commit()

    # Retrieve all of the anchor tags
    tags = soup('a')
    count = 0
    for tag in tags:
        href = tag.get('href', None)
        if (href is None):
            continue
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        if (len(up.scheme) < 1):
            href = urljoin(url, href)
        ipos = href.find('#')
        if (ipos > 1):
            href = href[:ipos]
        if (href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif')):
            continue
        if (href.endswith('/')):
            href = href[:-1]
        # print href
        if (len(href) < 1):
            continue

            # Check if the URL is in any of the webs
        found = False
        for web in webs:
            if (href.startswith(web)):
                found = True
                break
        if not found:
            continue

        db.execute(
            'INSERT OR IGNORE INTO Pages (url, html) VALUES ("{}", NULL)'.format(href))
        count = count + 1
        db.commit()

        try:
            row = db.select('SELECT id FROM Pages WHERE url="{}" LIMIT 1'.format(href), 'one')
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue
    print(count)
db.close()
