import sys
from lxml import html
import requests
import os

# print 'Enter url'
# url = sys.stdin.readline().rstrip()
# #url='http://community.topcoder.com/stat?c=problem_statement&pm=1259&rd=4493'
# page = requests.get(url)
# tree = html.fromstring(page.text)

# fh = open('problem_summary.html','Ur')
tree = html.parse('problem_summary.html').getroot()
# print tree.xpath('//a/@href')
print tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[1]/td[2]/a/text()')
print tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[2]/td[2]/a/text()')
print tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[2]/td[2]/a/text()')
print tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[4]/td[2]/text()')


