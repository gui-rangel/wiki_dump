import sys
import gzip
import requests
from datetime import datetime
from io import BytesIO

def insert_sorted(lis, tup):
    lo, hi = 0, len(lis)
    while lo < hi:
        mid = (lo + hi) // 2
        if tup[1] < lis[mid][1]:
            hi = mid
        else:
            lo = mid + 1
    lis.insert(lo, tup)
    return lis

def parse_dates():
	if len(sys.argv) == 1:
		# wiki dump is in utc
		# date = datetime.utcnow()
		date = datetime.now()
		year, month, day, hour = \
			date.strftime("%Y"), date.strftime("%m"), date.strftime("%d"), date.strftime("%H")
	else:
		# parse input dates, convert to utc
		pass

	return (year, month, day, hour)

def main():
	year, month, day, hour = parse_dates()
	
	url = "https://dumps.wikimedia.org/other/pageviews/" + \
			"{0}/{0}-{1}/pageviews-{0}{1}{2}-{3}0000.gz".format(year, month, day, hour)
	
	response = requests.get(url)
	# handle bad response
	if response.status_code == 404:
		print("404")
		print(url)
		return

	file_stream = gzip.open(BytesIO(response.content), 'rt', encoding='utf-8')

	domains = {}
	for line in file_stream:
	    domain, page, page_count = line.split(" ")[:-1]
	    page_count = int(page_count)
	    if "." in domain:
	        # Means it's not in wikipedia.org, but other wiki foundation sites: URL
	        continue
	    if domain not in domains:
	        # tuple(List[tuple(page, page_count)], domain_count)
	        domains[domain] = ([(page, page_count)], 1)
	    else:
	        d = domains[domain]
	        if d[1] < 25:
	            sorted_list = insert_sorted(d[0], (page, page_count))
	            domains[domain] = (sorted_list, d[1]+1)
	        else:
	            if d[0][0][1] < page_count:
	                sorted_list = insert_sorted(d[0], (page, page_count))[1:]
	                domains[domain] = (sorted_list, d[1])


if __name__ == '__main__':
	main()