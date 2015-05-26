""" This is the opencoproprates bot for mission 768
http://missions.opencorporates.com/missions/768
"""
import requests
import xlrd
import json
import datetime
import turbotlib
import subprocess
import re
from bs4 import BeautifulSoup

DOCUMENT_LINK = "http://www.bsl.gov.sl/Directory_of_Financial_&_" \
                + "Non-Bank_Financial_Institutions/" \
                + "COMMERCIAL_BANKS_&_ADDRESSES.xls"
SHEET_LOCATION = "%s/sheet.xls" % turbotlib.data_dir()
SOURCES = ["http://www.bsl.gov.sl/ntl_lottery.html",
           "http://www.bsl.gov.sl/housing_fin.html",
           "http://www.bsl.gov.sl/insurance_cos.html",
           "http://www.bsl.gov.sl/savings_loans.html",
           "http://www.bsl.gov.sl/finance_houses.html"
          ]
COMMUNITY_BANK_DOC_LINK = "http://www.bsl.gov.sl/Directory_of_Financial_&_Non-Bank_Financial_Institutions/COMMUNITY_BANKS_&_ADDRESSES.doc"
COMMUNIY_BANK_LOCATION = "%s/comunity_banks.doc" % turbotlib.data_dir()

SAMPLE_DATE = datetime.date.today().isoformat()

def download_community_banks():
    """ download the community banK information and convert it """
    download(COMMUNITY_BANK_DOC_LINK, COMMUNIY_BANK_LOCATION)
    subprocess.call(['libreoffice',
                     '--headless',
                     '--convert-to',
                     'html',
                     COMMUNIY_BANK_LOCATION,
                     '--outdir',
                     turbotlib.data_dir()]
                   )

def extract_community_bank_data():
    with open("%s/comunity_banks.html" % turbotlib.data_dir()) as infile:
        html_content = infile.read()
        content = BeautifulSoup(html_content)
        table = content.find("table")
    for j, row in enumerate(table("tr")):
        # skip the headings
        if j == 0:
            continue
        data = {}
        for i, cell in enumerate(row("td")):
            strings = [string for string in cell.strings]
            value = clean(strings[1])
            if i == 0:
                data['name'] = value
            elif i == 1:
                data['address'] = value
        print data


def download(link, savepath):
    """ This downloads the file and stores it to the local disk"""
    with open(savepath, "wb") as handle:
        response = requests.get(link)
        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)



def extract_data():
    """ This extract the data from the downloaded file"""
    workbook = xlrd.open_workbook(SHEET_LOCATION)
    worksheet = workbook.sheet_by_name("BNK BRANCHES")
    num_rows = worksheet.nrows - 1
    curr_row = 3
    all_banks = []
    while curr_row < num_rows:
        curr_row += 1
        is_new_root_bank = worksheet.cell_value(curr_row, 0) != ""
        if is_new_root_bank:
            bank_name = worksheet.cell_value(curr_row, 0)
            bank_name = bank_name.strip()
            bank_object = {"company_name": bank_name,
                           "branches": [],
                           "sample_date": SAMPLE_DATE,
                           "source_url": DOCUMENT_LINK
                          }
            all_banks.append(bank_object)
        branch_name = worksheet.cell_value(curr_row, 1)
        branch_name = branch_name.strip()
        branch_address = worksheet.cell_value(curr_row, 2)
        row_is_empty = (branch_name == "" and branch_address == "")
        if not row_is_empty:
            branch_dict = {"branch": branch_name, "address": branch_address}
            all_banks[-1]["branches"].append(branch_dict)

    for bank in all_banks:
        print json.dumps(bank)

def main():
    """ The main function """
    #download_community_banks()
    extract_community_bank_data()
    #download(DOCUMENT_LINK, SHEET_LOCATION)
    #extract_data()
    #for source in SOURCES:
        #extract_companies(source)


def extract_companies(source_url):
    """ Gets the insurance companies """
    html_content = requests.get(source_url).text
    content = BeautifulSoup(html_content)
    table = content.findAll("table")[5]
    companies = table_to_json(table)
    for company in companies:
        company["source_url"] = source_url
        company["sample_date"] = SAMPLE_DATE
        print json.dumps(company)


def table_to_json(bs4_table):
    """ converts a BeautifulSoup table to a json array with
    dictionaries as values. Those contain the table headings
    as keys and the cell values as values """
    table_data = []
    for row in bs4_table("tr"):
        row_values = []
        for cell in row("td"):
            values = [string for string in cell.strings]
            if len(values) == 1:
                row_values.append(clean(values[0]))
            else:
                row_values.append([clean(value) for value in values])
        table_data.append(row_values)
    headings = table_data.pop(0)
    all_values = []
    for line in table_data:
        structure = dict((headings[i], line[i]) for i in range(len(line)))
        all_values.append(structure)
    return all_values

def clean(string):
    """ delete newlines and whitespace inside of string """
    without_newline = string.replace("\r\n", "")
    return re.sub(r"\s\s+", " ", without_newline)



if __name__ == "__main__":
    main()
