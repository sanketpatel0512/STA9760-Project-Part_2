from sodapy import Socrata
import json
import argparse
import os
from elasticsearch import Elasticsearch
from datetime import datetime


es = Elasticsearch()

#Define Main Function For NYC Parking Violation Data Collection & Output
def main(page_size,num_pages,output):
	client = Socrata("data.cityofnewyork.us",dict(os.environ)["APP_KEY"]) #APP_KEY is APP_TOKEN from Socrata
	off_set = 0

	# If statement to define number of calls if input not provided by user
	if num_pages == False:
		lines = client.get("nc67-uf89",select='COUNT(*)')
		int_count = int(lines[0]['COUNT'])
		num_pages = (int_count//page_size)+1

	# Open Output file provided by user		
	if output != False:
		outfile = open(output, 'w')

	#For loop to Call Data from NYC Open Data
	for i in range(num_pages):
		d = client.get("nc67-uf89",limit=page_size,offset = off_set)
		# Output data based on user's choice
		# Print Data In Stdout
		for j in d:
			if output == False:
				print(j)
			# Save data to output file
			else:
				json.dump(j, outfile)
				outfile.write('\n')
			#Change Data to relevant datatypes
			j['issue_date'] = datetime.strptime(j['issue_date'],'%m/%d/%Y').date()
			if 'fine_amount' in j:
				j['fine_amount'] = float(j['fine_amount'])
				j['penalty_amount'] = float(j['penalty_amount'])
				j['interest_amount'] = float(j['interest_amount'])
				j['reduction_amount'] = float(j['reduction_amount'])
				j['payment_amount'] = float(j['payment_amount'])
				j['amount_due'] = float(j['amount_due'])
			
			res = es.index(index = "nyc-violations",doc_type = 'json',body=j)
		off_set += page_size

# Define and parse Commmandline arguments from user
parser = argparse.ArgumentParser(description = 'Inputs for Parking Violation Data Collection')
parser.add_argument('--page_size',type = int, required =True, help = 'Required Argument: Input number of data records to pull in one call')
parser.add_argument('--num_pages', type = int, default = False,help = 'Optional Argument: Input number of calls to perform on the dataset')
parser.add_argument('--output', type = str, default = False,help = 'Optional Argument: Provide *.json file name to save data in file')
		
# Pass the argument inputs to the main function
if __name__ == '__main__':
	args = parser.parse_args()
	main(**vars(args))