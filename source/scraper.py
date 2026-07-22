from bs4 import BeautifulSoup
import requests 

url = "https://calendar.macewan.ca/course-descriptions/cmpt/"
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
course_dict = {}
courses = soup.find_all('div', class_ = "courseblock")
for course in courses:
    str = course.find('strong').text
    list = str.split('\n')
    ccode = list[0].replace('\xa0', ' ')
    title = list[1]
    credits = list[2][:1]
    schedule = '(' + list[2][-6:] + ')'
    desc = course.find(class_ = "courseblockdesc noindent").text
    check_preq = course.find('p', class_ = "courseblockextra noindent")
    if check_preq:
        preq = check_preq.text.replace('Prerequisites: ', '').replace('\xa0', ' ')
    else:
        preq = 'NONE'
    course_dict.update({ccode:{'Title':title, 'Credits':credits, 'Schedule':schedule, 'Description':desc, 'Prerequisites': preq}})
    print(course_dict)