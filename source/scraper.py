from bs4 import BeautifulSoup
import requests 
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
base_url ="https://calendar.macewan.ca/course-descriptions/"

def scrape_course_offering(base_url):
    '''
    scrapes all available courses and returns them in a list
    pre: courses are ordered in webpage
    '''
    try:
        page = requests.get(base_url, headers) #returns a response object 
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")#debugging
        return False
    
    course_list = []
    soup = BeautifulSoup(page.text, 'html.parser')
    courses = soup.select('div.az_sitemap > ul li a')
    count = 0 #debugging
    for course in courses:
        texts = course.text.strip()
        course_list.append(texts[:4])
    return course_list

def scrape_department(dept_code, dept_name):
    '''
    Scrapes the passed website for course info and saves data in a structured json
    To do: configure return type, dept code only works for cmpt rn
    '''
    try:
        page = requests.get(dept_code, headers, timeout=(3.05, 10.05)) #returns a response object 
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")#debugging
        return False
    
    soup = BeautifulSoup(page.text, 'html.parser')
    course_dict = {}
    courses = soup.find_all('div', class_ = "courseblock") #list of all courses info
    for course in courses:
        header_elem = course.find('strong')
        if not header_elem:
            continue
        header_txt = header_elem.text 
        header_prts = header_txt.split('\n')
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
        preq = 'N/A'
        for p in extra_preq:
            clean_text = p.text.replace('\xa0', ' ').strip()
            if "Prerequisite" in clean_text:
                preq = clean_text.replace('Prerequisites: ', '').strip()
            elif "credit" in clean_text.lower() and clean_text not in restrictions:
                restrictions.append(clean_text)
            elif "note" in clean_text.lower() and clean_text not in notes:
                notes.append(clean_text)   
        course_dict[ccode] = {'Title':title, 'Credits':credits, 'Schedule':schedule, 'Description':desc, 'Prerequisites': preq, 'Restrictions': restrictions, 'Notes': notes}

    # Save the extracted course data to a JSON file
    with open(dept_name +'_courses.json', 'w', encoding='utf-8') as f:
        json.dump(course_dict, f, indent=4, ensure_ascii=False)
    print("Successfully saved course data to " + dept_name + "_courses.json!")
    return True

#scrape_department("https://calendar.macewan.ca/course-descriptions/cmpt/", 'english')

def subject_url_parser(base_url):
    '''
    Loops through all available courses and passes their respective name & urls to scrape_department()
    parameters:
        -base_url: url to base university page containing all offered courses
    '''
    
    courses = scrape_course_offering(base_url) #list of all offered courses
    if not courses:
            return
    
    for course in courses:
        dept_code = base_url + course.lower() + '/'
        scrape_department(dept_code, course)
    
subject_url_parser(base_url)