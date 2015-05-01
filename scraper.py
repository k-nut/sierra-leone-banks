""" This is the opencoproprates bot for mission 768
http://missions.opencorporates.com/missions/768
"""
import requests
import xlrd
import json
import datetime
import turbotlib

DOCUMENT_LINK = "http://www.bsl.gov.sl/Directory_of_Financial_&_" \
                + "Non-Bank_Financial_Institutions/" \
                + "COMMERCIAL_BANKS_&_ADDRESSES.xls"
SHEET_LOCATION = "%s/sheet.xls" % turbotlib.data_dir()


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
    sample_date = datetime.date.today().isoformat()
    while curr_row < num_rows:
        curr_row += 1
        is_new_root_bank = worksheet.cell_value(curr_row, 0) != ""
        if is_new_root_bank:
            bank_name = worksheet.cell_value(curr_row, 0)
            bank_name = bank_name.strip()
            bank_object = {"company_name": bank_name,
                           "branches": [],
                           "sample_date": sample_date,
                           "source_url": DOCUMENT_LINK
                          }
            all_banks.append(bank_object)
        branch_name = worksheet.cell_value(curr_row, 1)
        branch_name = branch_name.strip()
        branch_address = worksheet.cell_value(curr_row, 2)
        row_is_empty = (branch_name == "" and not branch_address == "")
        if not row_is_empty:
            branch_dict = {"branch": branch_name, "address": branch_address}
            all_banks[-1]["branches"].append(branch_dict)

    for bank in all_banks:
        print json.dumps(bank)

def main():
    """ The main function """
    download()
    extract_data()


if __name__ == "__main__":
    main()
