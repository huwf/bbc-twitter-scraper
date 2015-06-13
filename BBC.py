from URLGetter import URLGetter
from BeautifulSoup import BeautifulSoup
import re
import time
import calendar
import robotparser
import os
from Database import Database
import base64
import zlib

db = Database()

class BBC:
	urls = []
	url = ''
	def __init__(self, responseObject, id, logger, referer = 'http://www.bbc.co.uk'):	
		try:	
			self.logger = logger			
			
			self.url = responseObject.url
			self.referer = referer			
			self.id = int(id);
			
			html = responseObject.text
			self.soup = BeautifulSoup(html)
			

			self.urls = self.getRelatedStoryURLs()
			self.html = self.getHTML()
			
			self.text = self.getText()
			self.title = self.getTitle()
			self.date = self.getDate()
			
			self.liveText = self.hasLiveText()

			self.twitterMentions = self.getTwitterMentions(self.text)
			self.getPossibleTwitterMentions()
			self.addInfoToDB()	

			if self.twitterMentions > 0:
				self.storeHTML()
			self.getTwitterLinks()
			
			#self.logger.debug("Constructor took %ds to complete" % int(time.time() - constructor_start))
		except Exception, e:
			self.logger.error("Exception %s happened for %s. Returning...\n" % (str(e), self.url))
			return

	def getTwitterLinks(self):
		'''
		Gets a list of all hyperlinks which point to Twitter and stores them in the database.
		'''
		
		anchors = []
		#print anchors
		counter = 0
		for p in self.html:
			anchors.append(p.findAll('a'))
		for tags in anchors:
			for a in tags:
				if 'href' in a:
					url = a['href']
					if re.match('http[s]*://(www\.)*twitter\.com', url) != None:
						query = 'INSERT INTO TwitterLinks(PageId, TwitterUrl) VALUES(?,?)'
						db.insertQuery(query, [self.id,url])
						counter += 1
		if counter > 0:				
			self.logger.info('TWITTER LINKS!!! %s links to Twitter %d times' % (self.url, counter))


	def robots(self, url, firstTime):
		'''
		If it's the first time in a particular request, then we will try and access the robots.txt file.
		We will then download it to prevent socket errors, because it just fails for no apparent reason.
		Some online discussion suggests it might be due to a 401 or 403 response from robots.txt.
		'''
		#robot_start = time.time()
		if firstTime:
			ug = URLGetter()
			self.logger.info('Getting robots information from BBC website')
			text = ug.request('http://www.bbc.co.uk/robots.txt')			
			with open('robots.txt', 'w') as f:
				#print "Text: %s " % text
				f.write(str(text))
		else:
			self.logger.debug('Using the local robots.txt file')
		robots = robotparser.RobotFileParser()
		robots.set_url('robots.txt')
		robots.read()
		booly = robots.can_fetch('*', url) and robots.can_fetch('Scraper', url) and robots.can_fetch('python-requests/2.1.0 CPython/2.7.5 Windows/7', url)
		#self.logger.debug('Getting robots took %ds, remote file = %s' % (int(time.time() - robot_start), str(firstTime)))
		return booly

	def checkIfInDb(self, url):
		##self.logger.debug('Checking if the URL %s is in the database' % url)
		#db_check_start = time.time()
		query = 'SELECT Url FROM BBCPages WHERE Url = ?'
		#query2 = 'SELECT Url FROM UnprocessedBBCPages WHERE Url = ?'
		##self.logger.debug(db.selectQuery(query, [url]))
		result = bool(db.selectQuery(query, [url]))# and db.selectQuery(query2, [url])
		#self.logger.debug('DB Check took: %d' % int(time.time() - db_check_start))
		return result

	def addInfoToDB(self):
		#query = 'INSERT INTO BBCPages(Url, Stamp, Title, TwitterMentions) VALUES(?,?,?,?)'	
		#update_start = time.time()
		query = 'UPDATE BBCPages SET Stamp = ?, Title=?, TwitterMentions=?, LiveText=? WHERE Url = ?';
		update = db.updateQuery(query, [self.date, self.title, self.twitterMentions, int(self.liveText), self.url])
		self.logger.info('Info updated for %s, %d rows updated' % (self.url, update))
		#self.logger.debug('Info update took %ds for %s' % int((time.time() - update_start)))
		return update


	def doNetworkStuff(self, id2):
		'''
		Add all the URLs that this URL points to into the database.  This makes it RESEARCH!
		'''
		return db.insertQuery('INSERT INTO BBCLinks(ID1, ID2) VALUES(?,?)', [self.id, id2])
	
	def getRelatedStoryURLs(self):
		#related_story_start = time.time()
		self.logger.info('Searching for URLs on %s' % self.url)
		hyperlinks = self.soup.findAll('a', attrs={'class' : ['story', 'tag', 'link', 'image', 'image-link']})

		old_hyperlinks = self.soup.findAll('div', attrs={'class' : 'arr'})
		for oh in old_hyperlinks:
			url = oh.find('a')			
			hyperlinks.append(url)

		listy = []
		queryRobots = calendar.timegm(time.gmtime()) - os.path.getmtime('robots.txt') > 3600
		self.robots(self.url, queryRobots)
		id = 0
		counter = 0
		#loop_start = 0
		for h in hyperlinks:
			counter +=1
			url = h['href']
			#self.logger.debug('getRelatedStoryURLs has URL %s' % url)
			if url.startswith('/'):
				url = 'http://www.bbc.co.uk' + url	

			if self.robots(url, False) and not self.checkIfInDb(url) and not url in listy and not url == self.url and 'bbc.co.uk' in url and not 'mailto:' in url:
				#self.logger.info('%s is not in the database or against the robots.txt' % url)
				id = BBC.addIdToDB(url)
				listy.append('%d|%s' % (int(id), url))
				self.logger.info("About to add %s to the database" % url)				
			else:
				#self.logger.debug('It already exists somewhere!')
				if self.checkIfInDb(url):
					id = BBC.getIdByUrl(url)
			self.doNetworkStuff(id)			

		self.logger.info('Did research.  %s links to %d pages.  Added to the databse' % (self.url, counter))
		#self.logger.debug('Loop took %ds, function took %ds' % (int(time.time() - loop_start), int(time.time() - related_story_start)))
		return listy

	def getHTML(self):		
		'''
		On old pages it breaks, because	they have a table based layout(!), see e.g. http://news.bbc.co.uk/1/hi/england/hampshire/6245861.stm 
		which has an XPath path of /html/body/table[2]/tbody/tr/td[3]/table[2]/tbody/tr[2]/td
		'''
		##self.logger.debug('Using getHTML method')
		content = self.soup.find('div', id='main-content')
		if content:
			content = content.findAll('p')
		else:
			#If it's an old page, fall back onto this...
			content = self.soup.find('body')
			content = content.findAll('table')
		#print content
		return content		

	def getText(self):

		content = self.getHTML()

		text = ''
		for c in content:
			text += c.text
		return text

	def getTitle(self):
		##self.logger.debug("The title is %s" % self.soup.find('title').text)
		return self.soup.find('title').text


	def getDate(self):
		date = self.soup.find('span', attrs={'class' : 'date'})
		if not date:
			date = self.soup.find('div', attrs={'class' : 'ds'})
		if not date:
			date = self.soup.find('span', attrs={'class' : 'ds'})			
		if not date:
			return 'UNKNOWN'
		else:
			return date.text

	def parseDate(self):
		'''
		If the date is in a bad format, catch the exception and put it into the database
		Try and find a way of getting them all later...
		'''
		query = 'INSERT INTO BadDates(PageId) VALUES(?)'
		if self.date == 'UNKNOWN':
			insert = db.insertQuery(query, [self.id])
			return insert
		try:
			time.strptime(self.date, '%d %b %Y')
			return 0
		except:
			insert = db.insertQuery(query, [self.id])
			return insert



	def getTwitterMentions(self, text):
		length = len(re.findall('([Tt]witter|[Tt]weet|[Tt]weeted)', text))
		if length > 0:
			self.logger.info("FOUND TWITTERS! %s has %d TwitterMentions" % (self.url, length))
		return length

	def getPossibleTwitterMentions(self):
		'''
		Finds content which might indicate twitter, e.g. @username or #hashTag
		'''
		text = self.text
		hashtags = len(re.findall('#[A-Za-z0-9]*?[ \.,]', text))
		usernames = len(re.findall('@[A-Za-z0-9]*?[ \.,]', text))
		if hashtags > 0 or usernames > 0:
			self.logger.info('FOUND (POSSIBLE) TWITTERS! %s appears to mention a #HashTag %d times, or a @Username %d times' % (self.url, hashtags, usernames))
			query = 'UPDATE BBCPages SET PossibleHashtags = ?, PossibleUsernames = ? WHERE Url = ?'
			db.updateQuery(query, [hashtags,usernames,self.url])
		

	@staticmethod
	def getIdByUrl(url):
		id = db.singleValueSelectQuery('SELECT rowid FROM BBCPages WHERE Url = ?', [url])
		if not id:
			id = BBC.addIdToDB(url)
		return id

	@staticmethod
	def addIdToDB(url):
		return db.insertQuery('INSERT INTO BBCPages(Url) VALUES(?)', [url])

	def hasLiveText(self):
		return bool(self.soup.find('div', attrs={'class' : 'live-text-best specials-section', 'id' : 'live-event-text-commentary'}))


	def processLiveText(self):
		'''
		Not used, I think
		'''
		#import zlib
		#import base64
		'''
		TODO: Check if date is UNKNOWN or not...
		'''
		liveText = str(self.soup.find('div', attrs={'class' : 'live-text-best specials-section', 'id' : 'live-event-text-commentary'}))
		#Lets compress it a little bit
		while('  ' in liveText):
			liveText = liveText.replace('  ', ' ')
		liveText = re.sub('[\t\n\r\f\v]', '', liveText)	
		liveText = re.sub('<script.*?</script>', '', liveText)	
		liveText = re.sub('<!--.*?(->)', '', liveText)
		liveText = base64.b64encode(zlib.compress(liveText))

		#Find the other live text on the same day
		listy = db.selectQuery('SELECT rowid,LiveTextString FROM LiveText WHERE Stamp = ?', [self.date])
		rowid = 0
		updated = False
		for li in listy:
			rowid = li[0]			
			if li[1] in zlib.decompress(base64.b64decode(liveText)):
				db.updateQuery('UPDATE LiveText SET LiveTextString=? WHERE rowid=?', [liveText, rowid])
				updated = True
				break
		if not updated:
			rowid = db.insertQuery('INSERT INTO LiveText(Text,Date) VALUES(?,?)', [liveText, self.date])
		db.insertQuery('INSERT INTO LiveTextUrl VALUES(?,?)', [self.id, rowid])


	def storeHTML(self):
		'''
		We only want to store the HTML if the page had some twitter mentions on it.
		'''

		pageText = self.text
		#Lets compress it a little bit
		while('  ' in pageText):
			pageText = pageText.replace('  ', ' ')

		pageText = re.sub('[\t\n\r\f\v]', '', pageText)	
		pageText = re.sub('<script.*?</script>', '', pageText)	
		pageText = re.sub('<!--.*?(->)', '', pageText)
		pageText = pageText.encode('utf-8', 'ignore')
		pageText = base64.b64encode(zlib.compress(pageText))		

		query = 'INSERT INTO BBCText(PageId, BBCText) VALUES(?,?);'
		insert = db.insertQuery(query,[self.id, pageText])
		return insert	




