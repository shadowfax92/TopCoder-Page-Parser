#!/usr/bin/python
import sys
from lxml import html
import requests
import os
import re
import time
import datetime

PROBLEM_DETAIL_URL='tc_problem_detail_page'
PROBLEM_STATEMENT_URL = 'tc_problem_statement_page'
DATA_STORE_FILE_PATH = 'topcoder_data.csv'


class TopCoderProblemDetails:
    def __init__(self):
        self.problem_name = None
        self.used_in = None
        self.used_as = None
        self.categories = None

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

        self.column_order = [self.col_problem_name,
                             self.col_used_in,
                             self.col_division,
                             self.col_level,
                             self.col_date,
                             self.col_time,
                             self.col_used_as,
                             self.col_categories]

        self.result_dict = dict()
        pass

    def process_data(self):
        self.get_more_from_used_as()
        self.store_date_and_time()
        self.create_dictionary()

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


    def print_content(self):
        print 'problem_name = ', self.problem_name
        print 'used_in = ', self.used_in
        print 'used_ad = ', self.used_as
        print 'categories = ', self.categories

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
        fh = open(self.file_path, 'a+')

        for col in self.cols:
            if col in tc_dict:
                fh.write(tc_dict[col])
                fh.write(',')

        fh.write('\n')
        fh.close()

    def do_first_time_init(self):
        file_size = os.path.getsize(self.file_path)
        print file_size
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


def identify_what_url_type(url):
    #TODO: add stuff here to figure the url type
    return PROBLEM_DETAIL_URL


def get_content_from_url_and_store(url):
    tree = html.parse(url).getroot()

    tc_prob = TopCoderProblemDetails()
    tc_prob.problem_name = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[1]/td[2]/a/text()')[0].strip(' \t\n\r')
    tc_prob.used_in = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[2]/td[2]/a/text()')[0].strip(' \t\n\r')
    tc_prob.used_as = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[3]/td[2]/text()')[0].strip(' \t\n\r')
    tc_prob.categories = tree.xpath('/html/body/table/tr/td[3]/div/table[1]/tr[4]/td[2]/text()')[0].strip(' \t\n\r')

    tc_prob.process_data()
    tc_prob.print_content()

    return tc_prob


def main():
    print 'Enter TC page url = '
    url = sys.stdin.readline().rstrip()
    # url = 'http://community.topcoder.com/tc?module=ProblemDetail&rd=16077&pm=13219'

    if check_is_url(url):
        url_type = identify_what_url_type(url)

        if url_type == PROBLEM_DETAIL_URL:
            tc_prob_obj = get_content_from_url_and_store(url)
            UpdateDataStore().update_data(tc_prob_obj.result_dict)

    else:
        print 'ERROR: not a valid url'

if __name__ == '__main__':
    main()