import erequests
from BBC import BBC
import random
import time
import datetime
import calendar
import logging
from Database import Database

db = Database()


def save_todo_list(listy):
	'''
		We'll run this every iteration of the loop, since we are catching exceptions silently
		and "dealing with them later".  Hopefully, saving this in a txt file will mean that we can come back
		to where we were after we crashed.  Maybe...
	'''
	with open('todo_list.txt', 'w') as f:
		f.write(str(listy))


if __name__ == '__main__':
	#Set up logger
	logger = logging.getLogger(__name__)	
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	#Log to console
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	#Log errors to file
	
	fh = logging.FileHandler('error_log.txt')
	fh.setFormatter(formatter)
	fh.setLevel(logging.ERROR)
	logger.addHandler(fh)
	
	#logger.info("Logger created")

	#Schedule stops occasionally, particularly for testing.  Or if it breaks badly
	#To save having to reprocess the URLs, we can just eval todo_list.txt.
	#The list is a list of dicts in the format {id|url:linkedURLs}

	url_list = []
	with open('todo_list.txt') as f:
		url_list = eval(f.read())
	length = 0
	while(url_list):
		#Stop check:
		stop_date = datetime.datetime(2014, 8, 9, 17, 0)
		if calendar.timegm(stop_date.timetuple()) - time.time() < 1:
			logger.info("Ending the application because the time is after the stop date.")
			break
		referer = url_list[0].keys()[0].split('|')[1]
		id = int(url_list[0].keys()[0].split('|')[0])
		#Outside peak hours, we shouldn't need to wait so long...
		if datetime.datetime.now().hour < 7:
			time.sleep(1)
		elif length >= 5:
			randy = random.randint(4,8)	
			logger.info("Processing links from %s.  About to sleep for %ds...." % (referer, randy))
			
			time.sleep(randy)
		else:
			logger.info("Processing links from %s.  Not sleeping because the last list was small/empty" % referer)
			#time.sleep(1)
		header={'Accept-Encoding':'gzip, deflate', 'User-Agent':'Scraper', 'Referer' : referer}
		
		print url_list[0]
		#print url_list[0]["%d|%s" % (id,referer)]		
		#list_not_empty = bool(url_list[0]["%d|%s" % (id,referer)])
		length = len(url_list[0]["%d|%s" % (id,referer)])
		print "List length: %d" % len(url_list[0]["%d|%s" % (id,referer)])
		rs = (erequests.async.get(u.split('|')[1], headers=header) for u in url_list[0]["%d|%s" % (id,referer)])		
		for u in erequests.map(rs):
			try:
				logger.info('Starting to process %s' % u.url)
				id = BBC.getIdByUrl(u.url)
				bbc = BBC(u, id, logger, referer)

				url_list.append({"%d|%s" % (id, bbc.url) : bbc.urls})		
			except Exception, e:
				#Just die and we can deal with it later
				logger.error(str(e))
		logger.info("Finished processing remaining URLs for %s" % referer)
		del url_list[0]		
		save_todo_list(url_list)





#I imagine I'll have to move this up to the top of the file if I want to use it again...		
def first_time_run():
	import sqlite3
	conn = sqlite3.connect(db.dbName)

	conn.execute('CREATE TABLE IF NOT EXISTS BBCPages(Url VARCHAR(128), Stamp VARCHAR(30) NULL, Title VARCHAR(60) NULL, TwitterMentions INT NULL, LiveText INT NULL)')
	conn.execute('CREATE TABLE IF NOT EXISTS BBCLinks(Id1 INT, Id2 INT)')
	conn.execute('CREATE TABLE IF NOT EXISTS BBCText(PageId INT, BBCText TEXT);')
	conn.execute('CREATE TABLE IF NOT EXISTS BadDates(PageId INT);')
	conn.execute('CREATE TABLE IF NOT EXISTS TwitterLinks(PageId INT, TwitterUrl VARCHAR(256))')
	conn.execute('ALTER TABLE BBCPages ADD PossibleHashtags INT NULL')
	conn.execute('ALTER TABLE BBCPages ADD PossibleUsernames INT NULL')
	
	seed_url = []
	url_list = []

	original_url = 'http://www.bbc.co.uk/news/world-europe-28159254'


	insert = db.insertQuery("INSERT INTO BBCPages(Url) VALUES(?)", [original_url])
	conn.close()

	seed_url = []
	#original_url = db.selectQueryAsList('SELECT Url FROM BBCPages WHERE Url = ?', [])[0]		
	id = BBC.getIdByUrl(original_url)
	print "ID: %d" % id

	seed_url.append('%d|%s' % (insert, original_url))


	header={'Accept-Encoding':'gzip, deflate', 'User-Agent': "Scraper", 'Referer' : 'http://www.bbc.co.uk'}
	
	rs = (erequests.async.get(u.split('|')[1], headers=header) for u in seed_url)	

	listy = list(erequests.map(rs))

	seed_url_response = listy[0]
	print seed_url_response
	print BBC.getIdByUrl(original_url)
	bbc = BBC(seed_url_response, id, logger)
	url_list = [{'1|%s' % original_url : bbc.urls}]

	save_todo_list(url_list)

	import sys
	sys.exit()	
