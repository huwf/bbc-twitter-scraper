from Database import Database
import time

dbName = '2014-07-02.db'

db = Database('2014-07-02.db')

query = 'SELECT * FROM BBCText'
listy = db.selectQuery(query)

for li in listy:
	print li#[1],li[2]
print "\n"


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

query = 'SELECT * FROM BBCPages WHERE TwitterMentions > 0 AND Stamp LIKE \'%2002%\''
listy = db.selectQuery(query)

for li in listy:
	print li

for i in range(2013, 2015):
	for m in months:		
		if i == 2014 and m == 'August':
			break
		query = 'SELECT * FROM ((SELECT COUNT(*) FROM BBCPages WHERE TwitterMentions > 0 \
			AND Stamp LIKE \'%' + str(i) + '%\' AND Stamp LIKE \'%' + str(m) + '%\') AS Mentions,\
		(SELECT COUNT(*) FROM BBCPages WHERE  Stamp LIKE \'%' + str(i) + '%\' AND Stamp LIKE \'%' + str(m) + '%\') AS Total) '
		listy = db.selectQuery(query)

		for li in listy:
			print m, i, li[0], li[1], 100 * float(li[0]) / float(li[1])


mentions = db.singleValueSelectQuery('SELECT (SELECT count(*) FROM BBCPages WHERE TwitterMentions  > 0);')
processed_total = db.singleValueSelectQuery('SELECT COUNT(*) FROM BBCPages WHERE TwitterMentions IS NOT NULL')
unprocessed_total = db.singleValueSelectQuery('SELECT COUNT(*) FROM BBCPages WHERE TwitterMentions IS NULL')

twitter_percentage = float(mentions) / float(processed_total) * 100
print "%d pages in the database (%d processed, %d unprocessed)\n%d mention Twitter (%f)." \
	% (processed_total + unprocessed_total, processed_total, unprocessed_total, mentions, twitter_percentage)

'''
Use this for making a nice graph...
links = db.selectQuery('SELECT Id1,Id2 FROM BBCLinks')

with open('links.csv', 'a') as f:
	for li in links:
		f.write('%s,%s\n' % (li[0], li[1]))
'''





#Old stuff.  Don't care about it at the moment, might look at it later...
# listy = db.selectQuery('SELECT * FROM BBCPages ORDER BY TwitterMentions DESC')

# for li in listy:
#     pass
#     #print("URL: %s\t%s\t%s\t%s" % (li[0], li[1], li[2], li[4]))

# query = 'SELECT Url, TwitterMentions FROM BBCPages ORDER BY TwitterMentions DESC'
# url = 'http://news.bbc.co.uk/1/hi/health/8583551.stm'
# listy = db.selectQuery(query)

# for li in listy:
# 	pass
#     #print li[0], li[1]

# query0 = "SELECT trim(substr(Stamp, length(Stamp) - 4)), Stamp FROM BBCPages LIMIT 1"
# query = 'SELECT count(*) FROM BBCPages'#, (SELECT count(*) FROM BBCPages WHERE TwitterMentions IS NOT NULL) AS ScrapedPages,  (SELECT count(*) FROM BBCPages WHERE TwitterMentions > 0) AS MentionsTwitter'# WHERE TwitterMentions IS NOT NULL'
# query2 = 'SELECT count(*) FROM BBCPages WHERE TwitterMentions IS NOT NULL'
# query2a = 'SELECT count(*) FROM BBCPages WHERE TwitterMentions IS NULL'
# query3 = 'SELECT count(*) FROM BBCPages WHERE TwitterMentions > 0'

# first_line = db.selectQuery(query0)
# total_pages = db.singleValueSelectQuery(query)
# processed_pages = db.singleValueSelectQuery(query2)
# unprocessed_pages = db.singleValueSelectQuery(query2a)
# twitter_pages = db.singleValueSelectQuery(query3)

# for li in first_line:
# 	stamp = li['Stamp']
# 	print(time.strptime(stamp, '%d %B %Y')[0])
# 	print li

# print 'Total Pages in DB: %d\nTotal Pages Processed: %d\nUnprocessed Pages: %d\nTotal Pages With Twitter: %d\nTwitter Page Percentage: %d \
# ' % (total_pages, processed_pages, unprocessed_pages, twitter_pages, 100 * twitter_pages / processed_pages)

# query4 = 'SELECT COUNT(*) FROM BBCLinks'
# print 'Total Links in DB: %d\n' % db.singleValueSelectQuery(query4)



# query5 = 'SELECT rowid FROM BBCPages WHERE Url = \'%s\'' % url
# rowid = db.singleValueSelectQuery(query5)
# print "This page has rowid %s " % rowid

# query6 = 'SELECT Url FROM BBCPages bp INNER JOIN BBCLinks bl ON bp.rowid = bl.Id2 WHERE bl.Id1 = %s AND TwitterMentions IS NULL' % rowid
# print "The following pages should have already been processed for %s, but haven't for some reason" % url
# for li in db.selectQueryAsList(query6):
# 	print li


# #query7 = 'SELECT COUNT(*) FROM (SELECT Url, COUNT(Url) AS Amount FROM BBCPages GROUP BY Url)a WHERE a.Amount > 1'#' ORDER BY Amount DESC'
# query7 = 'SELECT COUNT(Url) FROM BBCPages WHERE Url = ?'
# #for li in db.selectQuery(query7):
# #	print li[0]

# print "Checking for duplicates on %s: %d entry total" % (url, db.singleValueSelectQuery(query7, [url]))

# big_query = 'SELECT Year, COUNT(Year) AS Amount \
# FROM (SELECT trim(substr(Stamp, length(Stamp) - 3)) AS Year FROM BBCPages) GROUP BY Year ORDER BY Amount DESC'

# print "Big Query:"
# for li in db.selectQuery(big_query):
# 	print li

# #Starting at 11:47 on 3/1/14
# #Total Pages in DB: 52959
# #Total Pages Processed: 49149
# #Unprocessed Pages: 3810
# #Total Pages With Twitter: 7053
# #Twitter Page Percentage: 14 
# #Total Links in DB: 1763378