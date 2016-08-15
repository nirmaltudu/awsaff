#!/usr/local/bin/python

"""
Script to retrieve product info using Amazon Affiliate API.
"""
from optparse import OptionParser
from amazonproduct import API
import json
import time
import lxml.etree as etree
from collections import defaultdict

HTML_TMPL = \
"""
<div class="product-box">
	<a target="_blank" href="{DetailPageURL}">
		<img src="{MediumImage}" width="120" height="160">
	</a>
	<div class="product-title">
		<h3>{Title}</h3>
	</div>
	<p class="product-price">{Price}<br>
	   <a target="_blank" style="color: #337ab7; text-decoration:none;" href="{MoreOffer}"> More offers </a>
   </p>
	<div>
		<span class="a-button a-button-primary">
			<a target="_blank" href="{DetailPageURL}" style="text-decoration:none">
				<span class="a-button-inner">
					<img src="http://webservices.amazon.com/scratchpad/assets/images/Amazon-Favicon-64x64.png" class="a-icon a-icon-shop-now">
					<input class="a-button-input" type="submit" value="Add to cart">
					<span class="a-button-text">Shop Now</span>
				</span>
			</a>
		</span>
	</div>
</div>
"""


def get_options():
	parser = OptionParser()
	parser.add_option("-C", "--config_file", dest="filename",
					  help="Config file name", metavar="FILE")
	parser.add_option("-S", "--strategy", dest="strategy",
					  help="Specify strategy to follow")

	return parser.parse_args()

def main():
	(opt, args) = get_options()
	cat = Category()
	api = AWSAPI(AUTH())
	strat = Strategy(opt.strategy, api.API)
	strat.apply()
	strat.dumpHTML()


class Category(object):
	def __init__(self, cfg_file=None):
		self._cfg_file = cfg_file or "./categories.json"
		json_str = ''
		with open(self._cfg_file, 'r') as rf:
			json_str = ''.join(rf.readlines())
		self._category = json.loads(json_str)

	@property
	def Names(self):
		return [i[0] for i in self._category['CATEGORIES'].values()]

	@property
	def SearchIndex(self):
		return [i[1] for i in self._category['CATEGORIES'].values()]

	@property
	def BrowseNode(self):
		return [i[2] for i in self._category['CATEGORIES'].values()]

	@property
	def SearchIndexToNode(self):
		return dict([(i[1], i[2]) for i in self._category['CATEGORIES'].values()])

	@property
	def SearchIndexToSortKey(self):
		return dict([(i[1], i[3]) for i in self._category['CATEGORIES'].values()])

	@property
	def SearchIndexToName(self):
		return dict([(i[1], i[0]) for i in self._category['CATEGORIES'].values()])

class Result(dict):
	_XPATHS = {
		'DetailPageURL' : ['DetailPageURL'],
		'MediumImage' : ['MediumImage', 'URL'],
		'Title' : ['ItemAttributes', 'Title'],
		'MoreOffer' : ['Offers', 'MoreOffersUrl'],
		'Price' : ['Offers','Offer','OfferListing','Price','FormattedPrice']
	}
	def __init__(self, ele):
		for (k, v) in self._XPATHS.iteritems():
			t_ele = ele
			for i in v:
				try:
				    t_ele = getattr(t_ele, i)
				except AttributeError:
					t_ele = "-"
			setattr(self, k, t_ele)

	def toHTML(self):
		global HTML_TMPL
		try:
			return HTML_TMPL.format(DetailPageURL=self.DetailPageURL,
								    MediumImage=self.MediumImage,
								    Title=self.Title,
								    MoreOffer=self.MoreOffer,
								    Price=self.Price)
		except Exception:
			return ''
			
class Strategy(object):
	_cfg_file = './strategy.json'
	def __init__(self, name, api):
		json_str = ''
		with open(self._cfg_file, 'r') as rf:
			json_str = ''.join(rf.readlines())
			# print json_str
		cfg = json.loads(json_str)
		self._strat = cfg['STRATEGY'][name]
		self._results = defaultdict(list)
		self._qparams = dict()
		self._api = api

	@property
	def query_params(self):
		if self._qparams:
			return self._qparams
		cat = Category()
		for (cabbrev, cid) in cat.SearchIndexToNode.iteritems():
			params = dict()
			for attr in self._strat.keys():
				val = self._strat[attr]
				val = val.format(CATEGORY_ABBREV=cabbrev, CATEGORY_ID=cid,
								 CATEGORY_SORT=cat.SearchIndexToSortKey[cabbrev])
				params[attr] = val
			self._qparams[cat.SearchIndexToName[cabbrev]] = params
		return self._qparams

	def apply(self, sleep=2):
		for (cat, param) in self.query_params.iteritems():
			print '\t'.join(param.values())
			try:
				res = self._api.call(**param)
			except Exception:
				continue
			# print res
			for ele in res.Items.Item:
				e = Result(ele)
				self._results[cat].append(e)
			time.sleep(sleep)
		return True

	@property
	def results(self):
		return self._results

	def dumpHTML(self):
		html_text = ''
		links = ''
		for (cat, results) in self.results.iteritems():
			links += '<li><a href="#%s">%s</a></li>' % (cat, cat)
			html_text += '\n<div class="container" id="%s">' % cat
			html_text += '<div class="page-header"><h1>%s</h1></div>' % cat
			for result in results:
				html_text += result.toHTML() + '\n'
			html_text += "</div>\n"
		# print html_text
		with open('./html/index.tmpl', 'r') as rf:
			html_tmpl = ''.join(rf.readlines())
			html = html_tmpl.format(PRODUCT_DETAILS=html_text, INTERNAL_LINKS=links)
			# print html
			with open("./html/index.html", "w") as wf:
				wf.write(html)
		return True

class AWSAPI(object):
	def __init__(self, auth):
		self._api = API(access_key_id=auth.access_key,
				   secret_access_key=auth.secret_key,
				   locale='us',
				   associate_tag=auth.associate_tag)
	@property
	def API(self):
		return self._api
	

class AUTH(object):
	@property
	def access_key(self):
		return 'AKIAIMKZJ7DJT4P6NIUA'
	@property
	def secret_key(self):
		return '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'
	@property
	def associate_tag(self):
		return 'nirmaltudu-20'	


if __name__ == "__main__":
	main()