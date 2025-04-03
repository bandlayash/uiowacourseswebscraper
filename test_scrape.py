from bs4 import BeautifulSoup
import requests
import re
import csv

dept_names = []

base_url = "https://catalog.registrar.uiowa.edu/courses/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

for link in soup.find_all('a', href = True):
    href = link["href"]

    if href.startswith('/courses/') and href != '/courses/':
        segment = href.strip('/').split('/')
        if len(segment) >= 2:
            if 'class' not in link.attrs:
                dept_name = segment[1]
                dept_names.append(dept_name)
dept_names = list(dict.fromkeys(dept_names))

# get courses from all of the departments
def getCourses():
    courses = []
    completed_depts = []

    # loop through all the depts and get courses from every dept
    for code in dept_names:
        dept_url = f"{base_url}{code}/"

        try:
            response = requests.get(dept_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                course_blocks = soup.find_all('div', class_='courseblock')

                for block in course_blocks:
                    course_title_element = block.find('p', class_='courseblocktitle')
                    if course_title_element:
                        course_text = course_title_element.text.strip()
                        
                        # Parse using regex
                        # Pattern matches: code prefix (CS:), course number (1000), title, and s.h.
                        pattern = r'([A-Z]+:\d+)\s+(.*?)\s+(\d+\s+s\.h\.)'
                        match = re.match(pattern, course_text)
                        
                        if match:
                            course_code = match.group(1) 
                            title = match.group(2).strip()
                            
                            # Create a dictionary or tuple with the parsed information
                            course_info = {
                                'course_code': course_code,
                                'title': title
                            }
                            
                            courses.append(course_info)
                            
            else:
                print(f"Failed to access {dept_url}, status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error accessing {dept_url}: {e}")
            return []
        
        completed_depts.append(code)
        #progress update for every dept completed
        progress_update = f"{code.upper()} Completed"
        print(progress_update)
    return courses

def export_to_csv(courses, filename="test_courses.csv"):
    # Open a file for writing
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Define the fieldnames with your desired column names
        fieldnames = ['course_code', 'course_title']
        
        # Create a DictWriter
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write the data rows with the correct mapping
        for course in courses:
            writer.writerow({
                'course_code': course['course_code'],
                'course_title': course['title']
            })
    
    print(f"CSV file '{filename}' has been created successfully.")

                

def main():
    courses = getCourses()
    print(f"Found {len(courses)} courses")

    # example
    print(courses[1])

    # export
    export_to_csv(courses)

if __name__ == "__main__":
    main()