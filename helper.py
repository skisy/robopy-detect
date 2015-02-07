import csv
import Tkinter

def processFile(filepath):
	with open(filepath, 'rb') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		objects = []
		for row in reader:
			objects.append(row)
		return objects

def writeFile(filepath, content):
    with open(filepath,'wb') as csv_file:
    	writer = csv.writer(csv_file, delimiter=',')
    	for obj in content:
    		writer.writerow(obj)
