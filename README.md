# wiki_dump

The goal of this project is to compute the top 25 pages on Wikipedia for each sub-domain. 

The main algorithm is to traverse the file line by line and extract the domain, page and page_count. The data structure created to keep track of the top 25 pages is a dictionary where the key is the domain code (en, it, pt,...), and the value is a list of tuples, where each tuple is a page and its associated count. Since the input file is ordered by the domain name, we keep track of the current domain we're evaluating and how many 
pages so far in that domain. If we have not yet reached 25 pages for that domain, we keep adding pages. If we have reached 25 pages, then we insert the list while keeping it sorted, and remove the page with the least count. That way, we keep a running tab of the top 25 pages per domain.

To execute the file just rung 'python3 wiki_dump.py [DATE1-DATE2]', where date is in the format 'YYYY/MM/DD:HH', like 2018/08/22:05. If no date range is provided, it'll default for the latest completed hour wikipedia has data for.

To execute the unit tests, simply run 'python3 wiki_dump_test.py'.

Main Assumptions:
	Dates to be considered are in UTC.

Extra Considerations:
	A few things would be done a bit differently for a production setting. For starters, we would have extra unit tests for important functions (like 'validate_page' or 'insert_sorted'). Also, parts of the code could easily be parralellized, like creating the blacklist, and instead of traversing the entire input file serially, we could split the file according to the number of domains, therefore each individual process would calculate a different domain.	

	For running this application continuosly, one idea is to have a separate application that constantly checks the main wikipedia dump, and only starts this main count application when wikipedia has created a new data dump. Moreover, we don't need to create the blacklist data structure every single time, we can create it in the beginning and having it shared for each time the program runs.

	For testing, besides the tests provided, one labor-intensive way is to simply order the input file by count and domain, and check if the algorithm produces the same values.

	One improvement of this application would be to parallellize some of the heavy linear computation. Another one would be, in case the blacklist is too large, keep it on a structure that requires less space and more processing speed.