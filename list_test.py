import base64
import zlib
import re
from BeautifulSoup import BeautifulSoup
import time
txt = ''


with open('olympiclivetext.html') as f:
	html = f.read()
	soup = BeautifulSoup(html)










# with open('todo_list.txt') as f:
# 	start = time.time()
# 	listy = eval(f.read())
# 	print time.time() - start
# 	start = time.time()
# 	print listy[2234]
# 	print time.time() - start


def get_anchor_classes(filename):
	classes = []
	with open(filename) as f:
		html = f.read()
		soup = BeautifulSoup(html)
		listy = soup.findAll('a', attrs={'class': ['tag', 'link', 'story']})
		
		for li in listy:
			print li.attrs
			if len(li.attrs) > 1 and 'class' not in  li.attrs:
				class_name = li.attrs[1][1]
				if class_name not in classes:
					classes.append(class_name)
		return classes	

#print "%s\n%s\n%s\n" % (str(get_anchor_classes('bbc.html')), str(get_anchor_classes('bbcNewsStory.html')), str(get_anchor_classes('bbcSportStory.html')))
#print get_anchor_classes('bbcSportStory.html')
#<a class=""> we want are: story; special-report; link; tag, image, image-link


'''
	soup = BeautifulSoup(html)
	html = str(soup.find('div', id='main-content'))

	print "%d\tOriginal size" % len(html)
	print "%d\tGzip/Base64 original"	% len(base64.b64encode(zlib.compress(html)))

	html2 = re.sub('[\t\n\r\f\v]', '', html)
	print '%d\tGzip/Base64 - without whitespace, but including spaces' % len(base64.b64encode(zlib.compress(html2)))
	print '%d\tWithout whitespace, without double spaces' % len(html2)
	html2 = html.replace('  ', ' ')
	html2 = re.sub('[\t\n\r\f\v]', '', html2)
	print '%d\tGzip/Base64 - Without whitespace, without double spaces' % len(base64.b64encode(zlib.compress(html2)))
	print len(html2)
	html2 = html
	while('  ' in html2):
		html2 = html2.replace('  ', ' ')
	html2 = re.sub('[\t\n\r\f\v]', '', html2)	
	print "%d\tWithout whitespace and double spaces(looped)" % len(html2)
	print '%d\tGzip/Base64 - Without whitespace, without double spaces (looped)' % len(base64.b64encode(zlib.compress(html2)))	
	html2 = html
	while('  ' in html2):
		html2 = html2.replace('  ', ' ')
	html2 = html2.replace('&nbsp;', '')
	html2 = re.sub('[\t\n\r\f\v]', '', html2)	
	html2 = re.sub('<script.*?</script>', '', html2)	
	html2 = re.sub('<!--.*?(->)', '', html2)

	print "%d\tWithout whitespace and double spaces(looped), & <script> tags" % len(html2)

	print '%d\tGzip/Base64 - Without whitespace, without double spaces (looped)' % len(base64.b64encode(zlib.compress(html2)))	
	
	compressed = base64.b64encode(zlib.compress(html2))
	#print("HTML2 with some additional text")
	print html2
	print zlib.decompress(base64.b64decode(compressed))


with open('bbc.txt', 'w') as f:
	f.write(txt)
	


#Using only <div id='main-content'>
#31541	Original size
#9336	Gzip/Base64 original
#9256	Gzip/Base64 - without whitespace, but including spaces
#30940	Without whitespace, without double spaces
#9224	Gzip/Base64 - Without whitespace, without double spaces
#30389
#29913	Without whitespace and double spaces(looped)
#9188	Gzip/Base64 - Without whitespace, without double spaces (looped)
#25816	Without whitespace and double spaces(looped), & <script> tags
#8100	Gzip/Base64 - Without whitespace, without double spaces (looped)


#bbc.html (full document) starts at 96.0Kb (98,304B) on disk
'''