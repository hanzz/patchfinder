from patchfinder.plugin import Plugin
from patchfinder.patch import Patch
from collections import OrderedDict
import urllib
from lxml import etree
import pickle
import os
import sys

class GentooPlugin(Plugin):
	def __init__(self):
		self.name = 'Gentoo'
		if os.path.exists('gentoo.db'):
			pkl_file = open('gentoo.db', 'rb')
		else:
			pkl_file = open('/usr/share/patchfinder/gentoo.db', 'rb')
		self.packages = pickle.load(pkl_file)
		pkl_file.close()

	def patches(self, component):
		ret = {}
		categories = []
		if component.find("/") != -1:
			categories = [component.split('/')[0]]
			component = component.split('/')[1]
		else:
			if not self.packages.has_key(component):
				return {}
			categories = self.packages[component]
		category = ""
		version = ""
		for cat in categories:

			print >> sys.stderr, "Downloading Gentoo version info for", component, "in category", cat
			url = "http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/%s/%s" % (cat, component)
			f = urllib.urlopen(url)
			data = f.read()
			f.close()

			hrefs = etree.HTML(data).xpath("//*[contains(@name,'.ebuild')]")
			if len(hrefs) == 0:
				continue
			for href in hrefs:
				version += href.attrib['name'] + " "
			category = cat
			break


		print >> sys.stderr, "Downloading Gentoo patches list"
		url = "http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/%s/%s/files/" % (category, component)
		f = urllib.urlopen(url)
		data = f.read()
		f.close()
		#print >> sys.stderr, data

		ret[version] = OrderedDict()

		hrefs = etree.HTML(data).xpath("//*[contains(@name,'.patch')]")
		for href in hrefs:
			name = href.attrib['name']
			url = "http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/%s/%s/files/%s" % (category, component, href.attrib['name'])
			ret[version][name] = Patch(name, url)
		return ret

