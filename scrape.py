import requests
from bs4 import BeautifulSoup
import csv
import re
import time

def get_departments_links(base_url):
    """Get links to all department pages from the main catalog page."""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all department links
    dept_links = []
    dept_names = []
    
    # The department links are typically in an element with class 'courseblock'
    for link in soup.select('.contentarea a'):
        href = link.get('href')
        text = link.text.strip()
        
        # Look for department course links that have a pattern like "Accounting Courses (ACCT)"
        if href and 'courses/' in href and re.search(r'\([A-Z]+\)', text):
            dept_links.append(href)
            dept_names.append(text)
    
    return dept_links, dept_names

def extract_dept_code(dept_name):
    """Extract department code from text like 'Accounting Courses (ACCT)'."""
    match = re.search(r'\(([A-Z]+)\)', dept_name)
    if match:
        return match.group(1)
    return None

def get_courses_from_dept_page(dept_url, dept_name, base_url):
    """Extract course information from a department page."""
    full_url = base_url + dept_url if not dept_url.startswith('http') else dept_url
    response = requests.get(full_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    courses = []
    dept_code = extract_dept_code(dept_name)
    
    if not dept_code:
        return courses
    
    # Look for course blocks
    for course_block in soup.select('.courseblock'):
        # Find the course title line
        title_block = course_block.select_one('.courseblocktitle')
        if not title_block:
            continue
            
        title_text = title_block.text.strip()
        
        # Use regex to extract course code, title, and credit hours
        # Pattern: "ACCT:1300 First-Year Seminar 1 s.h."
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
    base_url = "https://catalog.registrar.uiowa.edu/courses/"
    
    print("Starting to scrape the University of Iowa Course Catalog...")
    dept_links, dept_names = get_departments_links(base_url)
    
    print(f"Found {len(dept_links)} departments. Starting to extract courses...")
    
    all_courses = []
    
    # Process each department
    for i, (dept_link, dept_name) in enumerate(zip(dept_links, dept_names)):
        print(f"Processing {dept_name} ({i+1}/{len(dept_links)})")
        dept_courses = get_courses_from_dept_page(dept_link, dept_name, base_url)
        all_courses.extend(dept_courses)
        
        # Sleep briefly to be respectful to the server
        time.sleep(1)
    
    print(f"Extracted {len(all_courses)} courses. Writing to CSV...")
    
    # Write to CSV
    with open('uiowa_courses.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['deptName', 'courseLevel', 'courseTitle']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for course in all_courses:
            writer.writerow(course)
    
    print("Scraping completed! Data saved to 'uiowa_courses.csv'")

if __name__ == "__main__":
    main()