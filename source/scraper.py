from bs4 import BeautifulSoup
import requests 

url = "https://calendar.macewan.ca/course-descriptions/cmpt/"
response = requests.get(url)