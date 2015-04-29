""" This is the opencoproprates bot for mission 768
http://missions.opencorporates.com/missions/768
"""
import requests
import xlrd
import json
import datetime

DOCUMENT_LINK = "http://www.bsl.gov.sl/Directory_of_Financial_&_" \
                + "Non-Bank_Financial_Institutions/" \
                + "COMMERCIAL_BANKS_&_ADDRESSES.xls"
SHEET_LOCATION = "./sheet.xls"

def download():
    """ This downloads the file and stores it to the local disk"""
    with open(SHEET_LOCATION, "wb") as handle:
        response = requests.get(DOCUMENT_LINK)
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
    current_branches = []
    current_company_name = ""
    sample_date = datetime.date.today().isoformat()
    while curr_row < num_rows:
        curr_row += 1
        company_name = worksheet.cell_value(curr_row, 0)
        if company_name != "":
            if current_company_name != "":
                bank_object = {"company_name": current_company_name,
                               "branches": current_branches,
                               "sample_date": sample_date,
                               "source_url": DOCUMENT_LINK
                              }
                all_banks.append(bank_object)
            current_company_name = company_name.strip()
            current_branches = []
        branch_name = worksheet.cell_value(curr_row, 1)
        branch_name = branch_name.strip()
        branch_address = worksheet.cell_value(curr_row, 2)
        if not branch_name == "" and not branch_address == "":
            branch_dict = {"branch": branch_name, "address": branch_address}
            current_branches.append(branch_dict)

    all_banks.append({"company_name": current_company_name,
                      "branches": current_branches,
                      "sample_date": sample_date,
                      "source_url": DOCUMENT_LINK
                     })

    for bank in all_banks:
        print json.dumps(bank)

def main():
    """ The main function """
    download()
    extract_data()


if __name__ == "__main__":
    main()
