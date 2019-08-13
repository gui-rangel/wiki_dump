import sys
import os
import gzip
import json
import requests
import datetime
from io import BytesIO

BLACKLIST = "https://s3.amazonaws.com/dd-interview-data/data_engineer/wikipedia/blacklist_domains_and_pages"

def parse_dates():
	if len(sys.argv) == 1:
		# wiki dump is in utc
		date = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
		return [(date.strftime("%Y"), date.strftime("%m"), 
				 date.strftime("%d"), date.strftime("%H"))]
	else:
		# parse input dates, convert to utc
		dates = []
		for user_date in sys.argv[1:]:
			date = datetime.datetime.strptime(user_date, "%Y/%m/%d:%H")
			dates.append((date.strftime("%Y"), date.strftime("%m"), 
						  date.strftime("%d"), date.strftime("%H")))
		return dates

def insert_sorted(lis, tup):
    low, high = 0, len(lis)
    while low < high:
        mid = (low + high) // 2
        if tup[1] < lis[mid][1]:
            high = mid
        else:
            low = mid + 1
    lis.insert(low, tup)
    return lis

def make_blacklist():
	response = requests.get(BLACKLIST)
	if response.status_code == 404:
		print(url)
		print("Blacklist file not found, everyone is included!!")
		return

	blacklist = {}
	for line in BytesIO(response.content):
	    line = str(line, 'utf-8')[:-1]
	    domain, page = line.split(" ")
	    if domain in blacklist:
	        blacklist[domain][page] = None
	    else:
	        blacklist[domain] = {page:None}
	return blacklist

def make_blacklist2():
	response = requests.get(BLACKLIST)
	if response.status_code == 404:
		print(url)
		print("Blacklist file not found, everyone is included!!")
		return

	blacklist = {}
	for line in BytesIO(response.content):
	    line = str(line, 'utf-8')[:-1]
	    domain, page = line.split(" ")
	    if domain in blacklist:
	        blacklist[domain].append(page)
	    else:
	        blacklist[domain] = [page]
	return blacklist

def validate_page(domain, page, blacklist):
	if "." in domain:
		if ".m" in domain:
			# TODO: check mobile
			return False
		else:
			return False

	if domain in blacklist:
		if page == blacklist.get(page):
			return False
	return True

def main():
	blacklist = make_blacklist()

	for date in parse_dates():
		year, month, day, hour = date

		file_path = "./data/wikicount_{0}-{1}-{2}-{3}.json".format(year, month, day, hour)

		if os.path.exists(file_path):
			print("This date has already been computed, the count is here: " + file_path)
			continue
		
		url = "https://dumps.wikimedia.org/other/pageviews/" + \
				"{0}/{0}-{1}/pageviews-{0}{1}{2}-{3}0000.gz".format(year, month, day, hour)
		
		response = requests.get(url)
		if response.status_code == 404:
			print("The date you entered is not valid, please try again!")
			print("Enter the date in 'YYYY/MM/DD:HH' format, with valid values.")
			print(url)
			return

		file_stream = gzip.open(BytesIO(response.content), 'rt', encoding='utf-8')
		domains = {}
		current_domain = ""
		domain_count = 0

		for line in file_stream:
		    domain, page, page_count = line.split(" ")[:-1]
		    page_count = int(page_count)

		    if domain != current_domain:
		        current_domain = domain
		        domain_count = 0

		    if not validate_page(domain, page, blacklist):
		    	continue

		    if domain not in domains:
		        # List[tuple(page, page_count)]
		        domains[domain] = [(page, page_count)]
		        domain_count += 1
		    else:
		        d = domains[domain]
		        if domain_count < 25:
		            domains[domain] = insert_sorted(d, (page, page_count))
		            domain_count += 1
		        else:
		            if d[0][1] < page_count:
		                sorted_list = insert_sorted(d, (page, page_count))[1:]
		                domains[domain] = sorted_list

		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		with open(file_path, "w") as write_file:
			json.dump(domains, write_file)


if __name__ == '__main__':
	main()