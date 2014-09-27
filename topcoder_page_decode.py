import sys
from lxml import html
import requests
import os
import re

PROBLEM_DETAIL_URL='tc_problem_detail_page'
PROBLEM_STATEMENT_URL = 'tc_problem_statement_page'


class TopCoderProblemDetails:
    def __init__(self):
        self.problem_name = None
        self.used_in = None
        self.used_as = None
        self.categories = None

        #process data
        self.division = None
        self.level = None
        pass

    def process_data(self):
        self.get_more_from_used_as()

    def get_more_from_used_as(self):
        to_process = self.used_as.split()
        _dict = dict()
        _dict[to_process[0]] = to_process[1]
        _dict[to_process[2]] = to_process[3]

        if 'Division' in _dict:
            self.division = _dict['Division']
        else:
            self.division = 'None'

        if 'Level' in _dict:
            self.level = _dict['Level']
        else:
            self.level = 'None'

        return

    def print_content(self):
        print 'problem_name = ', self.problem_name
        print 'used_in = ', self.used_in
        print 'used_ad = ', self.used_as
        print 'categories = ', self.categories

        print 'data from processing...'
        print 'Division = ', str(self.division)
        print 'Level = ', str(self.level)




def check_is_url(url):
    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url):
        return True
    else:
        return False


def identify_what_url_type(url):
    #TODO: add stuff here to figure the url type
    return PROBLEM_DETAIL_URL


def get_content_from_url(url):
    # tree = html.parse('problem_summary.html').getroot()
    tree = html.parse(url).getroot()

    tc_prob = TopCoderProblemDetails()
    tc_prob.problem_name = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[1]/td[2]/a/text()')[0].strip(' \t\n\r')
    tc_prob.used_in = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[2]/td[2]/a/text()')[0].strip(' \t\n\r')
    tc_prob.used_as = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[3]/td[2]/text()')[0].strip(' \t\n\r')
    tc_prob.categories = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[4]/td[2]/text()')[0].strip(' \t\n\r')

    tc_prob.process_data()
    tc_prob.print_content()




def main():
    print 'Enter TC page url = '
    # url = sys.stdin.readline().rstrip()
    url = 'http://community.topcoder.com/tc?module=ProblemDetail&rd=16077&pm=13219'

    if check_is_url(url):
        url_type = identify_what_url_type(url)

        if url_type == PROBLEM_DETAIL_URL:
            get_content_from_url(url)
    else:
        print 'ERROR: not a valid url'

if __name__ == '__main__':
    main()