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
		# wiki dump is in utc. We subtract 2 hours because that's the latest one they have available
		date = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
		return [(date.strftime("%Y"), date.strftime("%m"), 
				 date.strftime("%d"), date.strftime("%H"))]
	else:
		# parse input dates range
		dates = []
		try:
			# Check if user inputted the date in the correct format
			date1 = datetime.datetime.strptime(sys.argv[1], "%Y/%m/%d:%H")
			if len(sys.argv) == 2:
				return [(date1.strftime("%Y"), date1.strftime("%m"), 
				 		 date1.strftime("%d"), date1.strftime("%H"))]
			date2 = datetime.datetime.strptime(sys.argv[2], "%Y/%m/%d:%H")
		except Exception as e:
			print("Date is either incorrect or in an invalid format.")
			print("Please validate the date and type it as: 2018/08/22:05")
			sys.exit()

		if date1 > date2:
			print("Please have the 2nd date being later than the 1st date.")
			sys.exit()
		while date1 <= date2:
			# Create a date for each hour in the range
			dates.append((date1.strftime("%Y"), date1.strftime("%m"), 
						  date1.strftime("%d"), date1.strftime("%H")))
			date1 += datetime.timedelta(hours=1)

		return dates

def insert_sorted(lis, tup):
	# uses binary search to find where to insert the item in a sorted list.
	# the complexity is dominated by the inset method, hence O(n)
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
	''' 
	Creates a dictionary of domain names, and for each domain, a small dictionary for each page.
	This approach was chosen because we need to constantly check the blacklist. By making it a 
	dictionary of dictionaries, we ensure constant lookup time. The main drawback is that it 
	can take up large amounts of storage, but it greatly increases the runtime of the application.
	'''
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

def validate_page(domain, page, blacklist):
	# Checks if page is blacklisted and if the domain is wikipedia.org.
	if domain in blacklist:
		if page == blacklist.get(page):
			return False

	if "." in domain:
		if ".m" in domain:
			if domain[-2:] != '.m':
				return False
		else:
			return False

	return True

def calculate_top_25():
	blacklist = make_blacklist()

	for date in parse_dates():
		# runs the code and write a file for each day
		year, month, day, hour = date

		file_path = "./data/wikicount_{0}-{1}-{2}-{3}.json".format(year, month, day, hour)

		if os.path.exists(file_path):
			print("This date has already been computed, the count is here: " + file_path)
			continue
		else:
			os.makedirs(os.path.dirname(file_path), exist_ok=True)
		
		url = "https://dumps.wikimedia.org/other/pageviews/" + \
				"{0}/{0}-{1}/pageviews-{0}{1}{2}-{3}0000.gz".format(year, month, day, hour)
		
		response = requests.get(url)
		if response.status_code == 404:
			print("The date you entered is not valid, please try again!")
			print("Enter the date in 'YYYY/MM/DD:HH' format, with valid values.")
			print(url)
			return

		# read in the file and decompress it as a stream
		file_stream = gzip.open(BytesIO(response.content), 'rt', encoding='utf-8')
		domains = {} # dict(domain, list[tuple(page, page_count)])
		current_domain = ""
		domain_count = 0

		for line in file_stream:
		    s = line.split(" ")[:-1]
		    if len(s) != 3:
		        # bad format
		        continue

		    domain, page, page_count = line.split(" ")[:-1]
		    page_count = int(page_count)

		    # Reset the domain count when we reach a new domain in the file
		    if domain != current_domain:
		        current_domain = domain
		        domain_count = 0

		    if not validate_page(domain, page, blacklist):
		    	continue

		    if domain not in domains:
		        domains[domain] = [(page, page_count)]
		        domain_count += 1
		    else:
		        domain_top_25 = domains[domain]
		        if domain_count < 25:
		            domains[domain] = insert_sorted(domain_top_25, (page, page_count))
		            domain_count += 1
		        else:
		        	# Check if the new page has a bigger count then the current lowest count
		            if domain_top_25[0][1] < page_count:
		            	# Insert ordered and remove the page with the lowest count
		                sorted_list = insert_sorted(domain_top_25, (page, page_count))[1:]
		                domains[domain] = sorted_list

		# Write count to file in json format
		with open(file_path, "w") as write_file:
			json.dump(domains, write_file)
		print("Success! The wikipedia top count is here: " + file_path)


if __name__ == '__main__':
	calculate_top_25()