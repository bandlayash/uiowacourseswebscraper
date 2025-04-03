from bs4 import BeautifulSoup
import requests

def getDeptLinks(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    deptNames = []

    for link in soup.find_all('a', href = True):
        href = link["href"]

        if href.startswith('/courses/') and href != '/courses/':
            segment = href.strip('/').split('/')
            if len(segment) >= 2:
                if 'class' not in link.attrs:
                    deptName = segment[1]
                    deptNames.append(deptName.upper())
    return deptNames

def getCourses(base_url, dept_code):
    dept_url = f"{base_url}{dept_code}/"

    try:
        response = requests.get(dept_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            courses = []
            course_blocks = soup.find_all('div', class_='courseblock')

            for block in course_blocks:
                course_title_element = block.find('p', class_='courseblocktitle')
                if course_title_element:
                    course_title = course_title_element.text.strip()
                    courses.append(course_title)

            return courses
        else:
            print(f"Failed to access {dept_url}, status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error accessing {dept_url}: {e}")
        return []


                

def main():
    base_url = "https://catalog.registrar.uiowa.edu/courses/"
    print(getCourses(base_url, "cs"))

if __name__ == "__main__":
    main()