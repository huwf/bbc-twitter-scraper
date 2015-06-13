import erequests
from BBC import BBC
import logging
from Database import Database

db = Database()

#General logging stuff so it doesn't break
logger = logging.getLogger(__name__)	
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)	
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info("Logger created")


url = 'http://www.bbc.co.uk/1/hi/england/hampshire/6245861.stm'
referer = 'http://www.bbc.co.uk/news/health-22855670'
urls = [url]

rs = (erequests.async.get(u) for u in urls)



for u in erequests.map(rs):	
	print '\n\n\n\n%s' % u.url
	#print db.singleValueSelectQuery('SELECT rowid FROM BBCPages WHERE Url = ?', [u.url])
		
	id = BBC.getIdByUrl(u.url)
	print "id: %s" % str(id)
	bbc = BBC(u, id, logger, referer)

