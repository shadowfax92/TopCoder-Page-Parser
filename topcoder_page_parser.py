#!/usr/bin/env python
import sys
from lxml import html
import requests
import os
import re
import time
import datetime
import csv

DATA_STORE_FILE_PATH = 'topcoder_data.csv'


class TopCoderProblemDetails:
    def __init__(self):
        self.problem_name = None
        self.used_in = None
        self.used_as = None
        self.categories = None
        self.url = None

        #process data
        self.division = None
        self.level = None
        self.date = None
        self.time = None

        # dictionary key names for easy communication between classes
        self.col_problem_name = 'PROBLEM_NAME'
        self.col_used_in = 'USED_IN'
        self.col_used_as = 'USED_AS'
        self.col_categories = 'CATEGORIES'
        self.col_division = 'DIVISION'
        self.col_level = 'LEVEL'
        self.col_date = 'DATE'
        self.col_time = 'TIME'
        self.col_url = 'URL'

        self.column_order = [self.col_problem_name,
                             self.col_used_in,
                             self.col_division,
                             self.col_level,
                             self.col_date,
                             self.col_time,
                             self.col_used_as,
                             self.col_categories,
                             self.col_url]

        self.result_dict = dict()
        pass

    def process_data(self):
        self.get_more_from_used_as()
        self.store_date_and_time()
        self.create_dictionary()

    def validate_data_received(self):
        if self.problem_name is None:
            print 'ERROR: Invalid URL. Exiting!'
            sys.exit(1)

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

    def store_date_and_time(self):
        curr_time = datetime.datetime.now()
        self.date = curr_time.strftime('%d-%m-%Y')
        self.time = curr_time.strftime('%H:%M:%S')

    def create_dictionary(self):
        self.result_dict[self.col_problem_name] = self.problem_name
        self.result_dict[self.col_used_in] = self.used_in
        self.result_dict[self.col_used_as] = self.used_as
        self.result_dict[self.col_categories] = self.categories
        self.result_dict[self.col_division] = self.division
        self.result_dict[self.col_level] = self.level
        self.result_dict[self.col_date] = self.date
        self.result_dict[self.col_time] = self.time
        self.result_dict[self.col_url] = self.url

    def print_content(self):
        print 'problem_name = ', self.problem_name
        print 'used_in = ', self.used_in
        print 'used_ad = ', self.used_as
        print 'categories = ', self.categories
        print 'url = ', self.url

        print 'data from processing...'
        print 'Division = ', str(self.division)
        print 'Level = ', str(self.level)
        print 'Date = ', str(self.date)
        print 'Time = ', str(self.time)

        return


class UpdateDataStore:
    #TODO: handle backups, fixing column changes, updating data
    def __init__(self):
        self.tc_prob_obj = TopCoderProblemDetails()
        self.cols = self.tc_prob_obj.column_order
        self.file_path = DATA_STORE_FILE_PATH

        if not os.path.isfile(self.file_path):
            print 'ERROR: invalid file path provided. Exiting!'
            print "If you haven't created the file, create an empty file in that path"
            sys.exit(1)

        self.do_first_time_init()

    def update_data(self, tc_dict):
        if self.check_if_already_present(tc_dict):
            print "You've already solved this problem :(. Not updating it again"
            return
        fh = open(self.file_path, 'a+')

        for col in self.cols:
            if col in tc_dict:
                fh.write(tc_dict[col])
                fh.write(',')

        fh.write('\n')
        fh.close()

    def check_if_already_present(self, tc_dict):
        fh = open(self.file_path, 'Ur')
        for line in csv.reader(fh, delimiter=',', skipinitialspace=True):

            # checking just the problem name
            if line[0] == tc_dict[self.tc_prob_obj.col_problem_name]:
                return True

        return False

    def do_first_time_init(self):
        file_size = os.path.getsize(self.file_path)
        print 'Exiting file size = ', file_size
        if file_size == 0:
            # write the column names to file
            fh = open(self.file_path, 'a+')
            for col in self.cols:
                fh.write(str(col))
                fh.write(',')

            fh.write('\n')
            fh.close()


def check_is_url(url):
    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url):
        return True
    else:
        return False


def identify_and_get_right_url(url):
    tree = html.parse(url).getroot()
    is_problem_statement_string = tree.xpath('/html/body/table/tr/td[3]/table[1]/tr/td[3]/span/text()')[0].strip(' \t\n\r')

    # check if its a Problem statement page that is passed
    if re.search(r'Problem Statement', is_problem_statement_string):
        problem_detail_url = tree.xpath('/html/body/table/tr/td[3]/table[2]/tr[1]/td/table/tr[10]/td/a/@href')[0].strip(' \t\n\r')
        url = 'http://community.topcoder.com' + problem_detail_url
        print 'Given url is a problem statement url, trying to get a problem detailed url out of it'

        if check_is_url(url):
            print 'Extracted problem detailed page url = ', url
            return url
        else:
            print "ERROR: couldn't find problem detailed page url. Exiting!"
            sys.exit(1)

    # check if its a Problem detail page url
    tree = html.parse(url).getroot()
    is_problem_detail_string = tree.xpath('/html/body/table/tr/td[3]/table/tr/td[3]/span/text()')[0].strip(' \t\n\r')
    if re.search(r'Problem Detail', is_problem_detail_string):
        print 'Given url is a problem detail url'
        return url

    print "ERROR: Doesn't look like a topcoder url"
    sys.exit(1)


def get_content_from_url_and_store(url):
    try:
        tree = html.parse(url).getroot()

        tc_prob = TopCoderProblemDetails()
        tc_prob.problem_name = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[1]/td[2]/a/text()')[0].strip(' \t\n\r')
        tc_prob.used_in = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[2]/td[2]/a/text()')[0].strip(' \t\n\r')
        tc_prob.used_as = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[3]/td[2]/text()')[0].strip(' \t\n\r')
        tc_prob.categories = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[4]/td[2]/text()')[0].strip(' \t\n\r')
        tc_prob.url = url

        tc_prob.process_data()
        tc_prob.print_content()
        return tc_prob
    except Exception, e:
        print 'Something Went Wrong :('
        print 'Exception: ', str(e)
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        url = ''.join(sys.argv[1:])
    else:
        print 'Enter TC page url = '
        url = sys.stdin.readline().rstrip()

    print 'Given url = ', url
    #Test
    # url = 'http://community.topcoder.com/tc?module=ProblemDetail&rd=16077&pm=13219' #Problem detail url
    # url = 'http://community.topcoder.com/stat?c=problem_statement&pm=11278' #Problem statement url
    if check_is_url(url):
        url = identify_and_get_right_url(url)
        tc_prob_obj = get_content_from_url_and_store(url)
        UpdateDataStore().update_data(tc_prob_obj.result_dict)

    else:
        print 'ERROR: not a valid url'

if __name__ == '__main__':
    main()