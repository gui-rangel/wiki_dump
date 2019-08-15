# wiki_dump

The goal of this project is to compute the top 25 pages on Wikipedia for each sub-domain. 

The main algorithm is to traverse the file line by line and extract the domain, page and page_count. The data structure created to keep track of the top 25 pages is a dictionary where the key is the domain code (en, it, pt,...), and the value is a list of tuples, where each tuple is a page and its associated count. Since the input file is ordered by the domain name, we keep track of the current domain we're evaluating and how many 
pages so far in that domain. If we have not yet reached 25 pages for that domain, we keep adding pages. If we have reached 25 pages, then we insert the list while keeping it sorted, and remove the page with the least count. That way, we keep a running tab of the top 25 pages per domain.

To execute the file just rung 'python3 wiki_dump.py [DATE1-DATE2]', where date is in the format 'YYYY/MM/DD:HH', like 2018/08/22:05. If no date range is provided, it'll default for the latest completed hour wikipedia has data for.

