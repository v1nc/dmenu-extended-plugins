import dmenu_extended
import sys
from requests_html import HTMLSession
import urllib
import pyperclip
import re
#REs for smart copy.
RE_FILE = '(/[^/ ]*)+/[^/ ]+[.][^/\s.]+'
RE_PATH = '(/[^/\s]*)+/[^/\s.]*'
RE_MARSKS =['\".+\"', "\'.+\'",'\`.+\`', RE_FILE, RE_PATH]
class extension(dmenu_extended.dmenu):
	title = 'gmenu: '
	is_submenu = True
	#find paths/filenames and maybe commands in a string.
	def smart_copy(self,text):
		print(text)
		found = []
		for r in RE_MARSKS:
			search = re.search(r, text)
			if search:
				to_append = search.group(0)
				if not r == RE_FILE and not r == RE_PATH:
					#strip marks.
					to_append = search.group(0)[1:-1]
				found_at_search = False
				#search for dublicates.
				for f in found:
					if to_append in f or f in to_append:
						found_at_search = True
				if not found_at_search:
					found.append(to_append)
		#concatenate results if more than one.
		if len(found) > 1:
			out = ""
			first = True
			for f in found:
				if first:
					out+=f
					first = False
				else:
					out+=' | '+f
			return out
		elif len(found) == 1:
			return found[0]
		return text
	def run(self, inputText):
		if inputText == ''or inputText == ' ':
			 inputText = self.menu('', prompt='Enter search')
		#search for the input text.
		session = HTMLSession()
		url = 'https://www.google.com/search?{}'.format(urllib.parse.urlencode({'q':inputText}))
		r = session.get(url)
		full_text = r.html.find('.ILfuVd', first = True)
		head = r.html.find('.Z0LcW', first=True)
		sub = r.html.find(".yxAsKe, .kZ91ed", first=True)
		out = url
		out_array = []
		if full_text:
			for f in full_text.text.split(". "):
				out_array.append(f+".")
		elif head:
			#one sentence answer maybe with sub-answer.
			out = head.text
			if sub:
				out+="({})".format(sub.text)
		else:
			#listed answer, count is implicated.
			list_head = r.html.find('.co8aDb, .gsrt', first=True)
			list_text = r.html.find('.TrT0Xe')
			if(list_head):
				out_array.append(list_head.text)
				count = 1
				for l in list_text:
					first = True
					for k in l.text.split('. '):
						if first:
							out_array.append("({}): {}.".format(count,k))
							first= False
						elif not k =="...":
							out_array.append("      {}.".format(k))
					count+=1
		if len(out_array) == 0:
			#todo wörterbuch: widerstand, die unenlidhe gschichte
			#display title of results and take the user to the selected page.
			out_array.append(out)
			selectedIndex = self.select(out_array, prompt='Copy Text', numeric=True)
		else:
			#let user select result and copy relevant parts to clipboard.
			selectedIndex = self.select(out_array, prompt='Copy Text', numeric=True)
			pyperclip.copy(self.smart_copy(out_array[selectedIndex]))
