from Database import Database
db = Database()

query = 'SELECT rowid, Url FROM BBCPages WHERE TwitterMentions IS NULL ORDER BY rowid ASC'
query2 = 'SELECT Id1, Url FROM BBCPages bp INNER JOIN BBCLinks bl ON bp.rowid = bl.Id2 LIMIT 1'
listy = []
referer = 'http://www.bbc.co.uk'
for li in db.selectQuery(query):
	id = li[0]
	url =  li[1]
	#print 'URL: %s' % url
	for li in db.selectQuery(query2):
		referer = '%s|%s' % (li[0], li[1])
	listy.append({referer:['%d|%s' % (id,url)]})

with open('todo_list.txt', 'w') as f:
	f.write(str(listy))