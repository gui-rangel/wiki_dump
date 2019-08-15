import os
import unittest
import datetime
import wiki_dump

class TestWikiTopCount(unittest.TestCase):

	def find_file(self, date):
		date = (date.strftime("%Y"), date.strftime("%m"), 
				date.strftime("%d"), date.strftime("%H"))
		year, month, day, hour = date
		file_path = "./data/wikicount_{0}-{1}-{2}-{3}.json".format(year, month, day, hour)
		return os.path.exists(file_path)

	def test_no_date(self):
		date = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
		wiki_dump.calculate_top_25([])
		self.assertTrue(self.find_file(date))

	def test_single_date(self):
		date = '2018/08/22:05'
		wiki_dump.calculate_top_25([date])
		date = datetime.datetime.strptime(date, "%Y/%m/%d:%H")
		self.assertTrue(self.find_file(date))

	def test_date_range(self):
		date1, date2 = '2018/08/22:05', '2018/08/22:08'
		wiki_dump.calculate_top_25([date1, date2])

		date1 = datetime.datetime.strptime(date1, "%Y/%m/%d:%H")
		date2 = datetime.datetime.strptime(date2, "%Y/%m/%d:%H")

		working = True
		while date1 <= date2:
			date1 += datetime.timedelta(hours=1)
			working = self.find_file(date1)
			if not working:
				break
		self.assertTrue(working)


if __name__ == '__main__':
    unittest.main()