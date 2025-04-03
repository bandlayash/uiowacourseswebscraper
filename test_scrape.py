from bs4 import BeautifulSoup
import requests
import re

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

def getCourses():
    courses = []
    completed_depts = []

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
                        pattern = r'([A-Z]+:)(\d+)\s+(.*?)\s+(\d+\s+s\.h\.)'
                        match = re.match(pattern, course_text)
                        
                        if match:
                            code_prefix = match.group(1).strip(':')  # Remove the colon
                            course_number = match.group(2)
                            title = match.group(3).strip()
                            
                            # Create a dictionary or tuple with the parsed information
                            course_info = {
                                'dept_code': code_prefix,
                                'course_number': course_number,
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
        progress_update = f"{code.upper()} Completed"
        print(progress_update)
    return courses


                

def main():
    print(getCourses())

if __name__ == "__main__":
    main()