from bs4 import BeautifulSoup
import requests 
import json
import time
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
university = "MacEwan"
domain_root = "https://calendar.macewan.ca"
base_url ="https://calendar.macewan.ca/course-descriptions/"

def scrape_department(dept_code, dept_name):
    '''
    Scrapes the passed website for course info and saves data in a structured json
    returns dictionary of courses
    '''
    try:
        page = requests.get(dept_code, headers=headers, timeout=(3.05, 10.05)) #returns a response object 
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")#debugging
        return {}
    
    soup = BeautifulSoup(page.text, 'html.parser')
    course_dict = {} #courses with respective info
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

        # extract credits
        credit_match = re.search(r'(\d+(?:\.\d+)?)', meta_data)
        credits = credit_match.group(1) if credit_match else "N/A"

        # extract schedule
        schedule_match = re.search(r'\d+-\d+-\d+(?:\.\d+)?', meta_data)
        schedule = f"({schedule_match.group(0)})" if schedule_match else "N/A"
        
        notes = []
        restrictions = []
        desc_elem = course.find(class_ = "courseblockdesc noindent")
        raw_desc = desc_elem.text.replace('\xa0', ' ') if desc_elem else ""
        if 'Note:' in raw_desc:
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
                ptext = clean_text.split(':', 1)[1]
                preq = ptext.strip()
            elif "credit" in clean_text.lower() and clean_text not in restrictions:
                restrictions.append(clean_text)
            elif "note" in clean_text.lower() and clean_text not in notes:
                notes.append(clean_text)   
        course_dict[ccode] = {'Department': dept_name, 'Title':title, 'Credits':credits, 'Schedule':schedule, 'Description':desc, 'Prerequisites': preq, 'Restrictions': restrictions, 'Notes': notes}
    return course_dict

def scrape_course_offering(domain_root, base_url):
    '''
    scrapes all available courses on university website
    pre: courses are hyperelinked in order on website
    returns true for success
    '''
    try:
        page = requests.get(base_url, headers=headers) #returns a response object 
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")#debugging
        return False
    
    course_catalog = {}
    soup = BeautifulSoup(page.text, 'html.parser')
    courses = soup.select('div.az_sitemap > ul li a')
    counter =0 #debugging
    for course in courses:
        target_url = domain_root + course['href']
        text = course.text.strip().split(' ')
        dept_name = text[0].strip()
        course_catalog.update(scrape_department(target_url, dept_name))
        time.sleep(1)
    
    # Save the extracted course catalog to a JSON file
    with open(university +'_courses.json', 'w', encoding='utf-8') as f:
        json.dump(course_catalog, f, indent=4, ensure_ascii=False)
    print("Successfully saved course catalog to " + university + "_courses.json!")
    return True

start_time = time.perf_counter()
scrape_course_offering(domain_root, base_url)
end_time = time.perf_counter()
elapsed_seconds = end_time - start_time
elapsed_minutes = elapsed_seconds /60
print(f"\nExecution Time: {elapsed_seconds:.2f} seconds ({elapsed_minutes:.2f} minutes)")