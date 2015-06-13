import urllib2
import socks
import socket
from StringIO import StringIO
import gzip
import time
import random

class URLGetter:
	'''
	Gets the URLs using the urllib.request library, except automatically adds the extra stuff I want
	HEAD/GET, Spoofed user agent/referer/, tor etc.
	'''

	def request(self,url, method = 'GET', tor = False, referer = False):
		req = urllib2.Request(url)
		if tor:
			socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
			socket.socket = socks.socksocket
				
		#req.add_header('Referer','http://www.google.co.uk')
		if referer:
			req.add_header('Referer', referer)
		req.add_header('Accept-encoding', 'gzip')
		req.add_header('User-Agent','Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)')#IE7, Windows Vista

		try:
			response = urllib2.urlopen(req)
			if response.info().get('Content-Encoding') == 'gzip':
			    buf = StringIO( response.read())
			    f = gzip.GzipFile(fileobj=buf)
			    return f.read()			
			return response.read()
		except urllib2.URLError as e:
			print "Exception!" + str(e.reason)
			if hasattr(e, 'code'):
				self.logger.debug("Code returned: %s\n" % str(e.code))	
			print("About to sleep and then try the request again.")
			time.sleep(random.randint(1,5))
			self.request(url,method,tor,referer)

