from bs4 import BeautifulSoup
import requests 

url = "https://calendar.macewan.ca/course-descriptions/cmpt/" #integrated with only cmpt for now
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
course_dict = {}
courses = soup.find_all('div', class_ = "courseblock") #list of all courses info
for course in courses:
    header_elem = course.find('strong')
    if not header_elem:
        continue
    header_txt = header_elem.text
    header_prts = str.split('\n')
    ccode = header_prts[0].replace('\xa0', ' ').strip() #course code/ID
    title = header_prts[1].strip() if len(header_prts) > 1 else "N/A"
    meta_data = header_prts[2] if len(header_prts) > 2 else ""
    credits = meta_data[:1] if meta_data else "N/A"
    schedule = '(' + meta_data[-6:] + ')' if len(meta_data) >= 6 else 'N/A'
    notes = []
    restrictions = []
    desc_elem = course.find(class_ = "courseblockdesc noindent")
    raw_desc = desc_elem.text.replace('\xa0', ' ') if desc_elem else ""
    if 'Note' in raw_desc:
        desc_prts = raw_desc.split("Note:")
        desc = desc_prts[0].strip()
        for part in desc_prts[1:]:
            full_note_text = "Note: " + part.strip()
            if "credit" in full_note_text.lower():
                restrictions.append(full_note_text)
            else:
                notes.append(full_note_text)    #i.e in case of a suggestion rather than restriction
    else:
        desc = raw_desc
    extra_preq = course.find_all('p', class_ = "courseblockextra noindent")
    for p in extra_preq:
        clean_text = p.text.replace('\xa0', ' ').strip()
        if "Prerequisite" in clean_text:
            preq = clean_text.replace('Prerequisites: ', '').strip()
        elif "credit" in clean_text.lower() and clean_text not in restrictions:
            restrictions.append(clean_text)
        elif "note" in clean_text.lower() and clean_text not in notes:
            notes.append(clean_text)   
    course_dict[ccode] = {'Title':title, 'Credits':credits, 'Schedule':schedule, 'Description':desc, 'Prerequisites': preq, 'Restrictions': restrictions, 'Notes': notes}
print(course_dict)