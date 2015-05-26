 #!/usr/bin/python
# -*- coding: utf-8 -*-
""" Converter for the cvdm bot """
import sys
import json


def convert_data():
    """ reads the raw data and converts the to
    the simple license schema """
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        raw_record = json.loads(line)

        licence_record = {
            "company_jurisdiction": 'Sierra Leone',
            "source_url": raw_record['source_url'],
            "sample_date": raw_record['sample_date'],
            "jurisdiction_classification": raw_record['type'],
            "category": 'Financial',
            "confidence": 'MEDIUM',
        }
        # the data extracted from the .xls has a 'company name' heading,
        # the html data has 'Name' instead
        #print raw_record.keys()
        if "company_name" in raw_record.keys():
            licence_record["company_name"] = raw_record['company_name']
        elif "Name" in raw_record.keys():
            licence_record["company_name"] = raw_record['Name']
        elif "name" in raw_record.keys():
            licence_record["company_name"] = raw_record['name']

        print json.dumps(licence_record)

if __name__ == "__main__":
    convert_data()
