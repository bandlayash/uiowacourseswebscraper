import requests
from bs4 import BeautifulSoup
import csv
import re
import time

def get_cs_department_link(base_url):
    """Get the link to the Computer Science department page."""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the Computer Science department link
    for link in soup.select('.contentarea a'):
        href = link.get('href')
        text = link.text.strip()
        
        if href and 'Computer Science' in text and re.search(r'\(CS\)', text):
            return href, text
    
    return None, None

def extract_dept_code(dept_name):
    """Extract department code from text like 'Computer Science Courses (CS)'."""
    match = re.search(r'\(([A-Z]+)\)', dept_name)
    if match:
        return match.group(1)
    return None

def get_courses_from_dept_page(dept_url, dept_name, base_url):
    """Extract course information from the CS department page."""
    full_url = base_url + dept_url if not dept_url.startswith('http') else dept_url
    print(f"Accessing: {full_url}")
    
    response = requests.get(full_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    courses = []
    dept_code = extract_dept_code(dept_name)
    
    if not dept_code:
        return courses
    
    print(f"Extracting courses for department code: {dept_code}")
    
    # Look for course blocks
    for course_block in soup.select('.courseblock'):
        # Find the course title line
        title_block = course_block.select_one('.courseblocktitle')
        if not title_block:
            continue
            
        title_text = title_block.text.strip()
        
        # Use regex to extract course code, title, and credit hours
        # Pattern: "CS:1210 Computer Science I: Fundamentals 4 s.h."
        match = re.search(fr'{dept_code}:(\d+)\s+(.+?)\s+\d+(?:\-\d+)?\s+s\.h\.', title_text)
        if match:
            course_level = match.group(1)
            course_title = match.group(2).strip()
            
            courses.append({
                'deptName': dept_code,
                'courseLevel': course_level,
                'courseTitle': course_title
            })
    
    return courses

def main():
    base_url = "https://catalog.registrar.uiowa.edu/courses/cs/"
    
    print("Starting to scrape the University of Iowa CS Course Catalog...")
    cs_dept_link = get_cs_department_link(base_url)
    cs_dept_name = "CS"
    
    if not cs_dept_link:
        print("Could not find Computer Science department link.")
        return
    
    print(f"Found Computer Science department: {cs_dept_name}")
    
    # Process CS department
    cs_courses = get_courses_from_dept_page(cs_dept_link, cs_dept_name, base_url)
    
    print(f"Extracted {len(cs_courses)} CS courses. Writing to CSV...")
    
    # Write to CSV
    with open('uiowacstest.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['deptName', 'courseLevel', 'courseTitle']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for course in cs_courses:
            writer.writerow(course)
    
    print("Scraping completed! Data saved to 'uiowacstest.csv'")
    
    # Print a sample of the results
    print("\nSample of extracted courses:")
    for i, course in enumerate(cs_courses[:5]):
        print(f"{i+1}. {course['deptName']}:{course['courseLevel']} - {course['courseTitle']}")

if __name__ == "__main__":
    main()