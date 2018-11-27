import webbrowser
import time
import pyperclip
import xmltodict
import json
import shlex, subprocess
from datetime import date
# from robobrowser import RoboBrowser
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


CHROME_DRIVER_PATH = "C:\\Program Files (x86)\\chromedriver_win32\\chromedriver"
BROWSER = webdriver.Chrome(CHROME_DRIVER_PATH)
TIMEOUT = 30

JAZZ_LOGIN_URL = r"https://jazz.cerner.com:9443/qm/auth/authrequired"
JAZZ_NET_USERNAME = "RRCGuest"
JAZZ_NET_PASSWORD = "readOnly*"

JAZZ_GET_ALL_PROJECTS_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/projects"
JAZZ_GET_PROJECT_TESTSCRIPTS_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testscript?page={}"
JAZZ_GET_PROJECT_TESTCASES_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testcase?page={}"
JAZZ_GET_TESTSCRIPT_BY_ID_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testscript/urn:com.ibm.rqm:testscript:{}"
JAZZ_GET_TESTCASE_BY_TITLE_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testcase?fields=feed/entry/content/testcase[title='{}']/*"
JAZZ_GET_TESTCASE_BY_ID_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testcase/urn:com.ibm.rqm:testcase:{}"


#
# def get_testscript_by_id(project, testscript_id):
#     BROWSER.get(JAZZ_GET_TESTSCRIPT_BY_ID_URL.format(project, testscript_id))
#
#     testscript_pre_tag_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'body > pre'))
#     WebDriverWait(BROWSER, TIMEOUT).until(testscript_pre_tag_present)
#     time.sleep(2)
#
#     testscript_pre_tag = BROWSER.find_element_by_tag_name('pre')
#     testscript_xml_text = testscript_pre_tag.text
#     testscript_dict = xmltodict.parse(testscript_pre_tag)
#
#     with open('rqm_url_utility_testing\\selenium_testscript_details\\testscript_{}.txt'.format(testscript_id),
#               'w') as selenium_testscript_file:
#         selenium_testscript_file.write(json.dumps(testscript_dict))
#

def run_rqm_url_utility(result_write_path, jazz_get_resources_url):
    """Used to make requests to Jazz API's -
    by making use of the RQM-URL-Utility Jar .
    The API Response is also written to a file .

    Params:
    jazz_get_resources_url - > API URL  for which you want to make a Request .
    result_write_path - > Path to which you want to write the API Response . """

    rqm_utility_dict = {
        'rqm_jar_path': 'C:/RQM-Extras-RQMUrlUtil-5.0.2/RQMUrlUtility.jar',
        'user': 'RRCGuest',
        'password': 'readOnly*',
        'write_to_path': result_write_path,
        'get_jazz_testscripts_url': jazz_get_resources_url
    }

    command_rqm_utility_jar_run = r"""
        java -jar {rqm_jar_path}
        -command GET
        -user {user}
        -password {password}
        -filepath {write_to_path}
        -url {get_jazz_testscripts_url}
    """.format(**rqm_utility_dict)

    args = shlex.split(command_rqm_utility_jar_run)
    # print(args)

    rqm = subprocess.run(args, shell=True)
    rqm.check_returncode()

#
# def get_jazz_testscript_by_id_popen(project, testscript_id):
#     """Get single Testscript Details - By ID .
#
#     Params:
#     project - > Project title .
#     testscript_id - > ID of Testscript - of which you want to get the Details ."""
#
#     write_to_path = 'C:/Users/SB063964/Desktop/rqm_url_utility_testing/selenium_testscript_details/rqm_testscript_{}.txt'.format(testscript_id)
#     # get_jazz_testscripts_url = "https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testscript?fields=feed/entry/content/testscript[title='{}']/*"\
#     get_jazz_testscript_url = "https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testscript/urn:com.ibm.rqm:testscript:{}".format(project, testscript_id)
#
#     run_rqm_url_utility(write_to_path, get_jazz_testscript_url)
#
#     with open(write_to_path, 'r') as testscript_file:
#         testscript_details = testscript_file.read()
#
#
# def get_testscripts(project, testscripts_url=None, get_page=0):
#
#     try:
#         if testscripts_url is None:
#             get_jazz_testscripts_url = 'https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testscript?page={}'.format(
#                 project, get_page)
#         else:
#             get_jazz_testscripts_url = testscripts_url
#
#         BROWSER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
#         BROWSER.get(get_jazz_testscripts_url.format(project, get_page))
#
#         testscripts_pre_tag_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'body > pre'))
#         WebDriverWait(BROWSER, TIMEOUT).until(testscripts_pre_tag_present)
#         time.sleep(2)
#
#         testscripts_pre_tag = BROWSER.find_element_by_tag_name('pre')
#         testscripts_xml_text = testscripts_pre_tag.text
#         all_testscripts_dict = xmltodict.parse(testscripts_xml_text)
#
#         with open('rqm_url_utility_testing\\selenium_testscripts\\project_{}_testscripts.txt'.format(project),
#                   'w') as selenium_testscripts_file:
#             selenium_testscripts_file.write(json.dumps(all_testscripts_dict))
#
#         testscripts_pagination_links = all_testscripts_dict['feed']['link']
#
#         print("get_page parameter >>> " + str(get_page))
#
#         current_page, next_page, last_page = 0, 0, 0
#
#         for link in testscripts_pagination_links:
#             if link["@rel"] == "self":
#                 current_page_link = link["@href"]
#                 current_page = current_page_link.split('&page=')[1]
#                 token = current_page_link.split('token=')[1].split('&amp;')[0]
#             elif link["@rel"] == "next":
#                 next_page_link = link["@href"]
#                 next_page = next_page_link.split('&page=')[1]
#             elif link["@rel"] == "last":
#                 last_page_link = link["@href"]
#                 last_page = last_page_link.split('&page=')[1]
#
#         print("Testscripts paginations links => " + json.dumps(testscripts_pagination_links))
#         print("current >>> " + str(current_page) + " ; next >>> " + str(next_page)
#               + " ; last >>> " + str(last_page))
#
#         for testscript in all_testscripts_dict['feed']['entry']:
#             for link in testscript['link']:
#                 # print(json.dumps(link))
#                 if link['@title'] == 'Web Console':
#                     testscript_id = link['@href'].split('&id=')[1]
#                     print(testscript_id)
#
#                     # get_testscript_by_id(project, testscript_id)
#                     get_jazz_testscript_by_id_popen(project, testscript_id)
#
#         print("Nothing")
#
#         if last_page > current_page:
#             get_testscripts(project, next_page_link)
#         else:
#             print("Please check the files generated .")
#
#     except TimeoutException:
#         print("Timed out waiting for page to load")
#


def get_testcase_by_id(project, testcase_id):
    """Get single Testcase Details - By TITLE .

    Params:
    project - > Project title .
    testcase_title - > Title of Testcase - of which you want to get the Details ."""

    write_to_path = r'C:/Users/SB063964/Desktop/rqm_url_utility_testing/selenium_testcase_details/testcase_{}.txt'.format(testcase_id)

    run_rqm_url_utility(write_to_path, JAZZ_GET_TESTCASE_BY_ID_URL.format(project, testcase_id))

    with open(write_to_path, 'r') as testcase_file:
        testcase_details = testcase_file.read()

    testcase_details_dict = xmltodict.parse(testcase_details)

    # print(testcase_details_dict)

    if isinstance(testcase_details_dict['ns2:testcase'].get(['ns2:testscript']), dict):
        all_testscripts = [testcase_details_dict['ns2:testcase']['ns2:testscript']]
    elif isinstance(testcase_details_dict['ns2:testcase'].get('ns2:testscript'), list):
        all_testscripts = testcase_details_dict['ns2:testcase']['ns2:testscript']

    for testscript in all_testscripts:
        get_testscript_url = testscript['@href']
        testscript_title = get_testscript_url.split('/testscript/')
        testscript_id = get_testscript_url.split(':testscript:')
        if len(testscript_title):
            write_testscript_to_path = r'C:/Users/SB063964/Desktop/rqm_url_utility_testing/selenium_testscript_details/testscript_{}.txt'.format(testscript_title[1])
        elif len(testscript_id):
            write_testscript_to_path = r'C:/Users/SB063964/Desktop/rqm_url_utility_testing/selenium_testscript_details/testscript_{}.txt'.format(testscript_id[1])
        # print(write_testscript_to_path)
        # print(get_testscript_url)
        if write_testscript_to_path:
            run_rqm_url_utility(write_testscript_to_path, get_testscript_url)

    # print(xmltodict.parse(testcase_details))


def get_testcases(project, testcases_url=None, get_page=0):
    """Get Testcases of a Project using Pagination => Route used '/<project-name>/testcase?token=<token>&page=<page-num>'

    Above route will return List of <pageSize> [currently default 50] Testcase Links that come under project.
    Loop through Testcase links =>
    Then call method to get Details of Testcase.
    """
    try:
        if testcases_url is None:
            get_jazz_testcases_url = 'https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/{}/testcase?page={}'
        else:
            get_jazz_testcases_url = testcases_url

        BROWSER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        BROWSER.get(get_jazz_testcases_url.format(project, get_page))

        testcases_pre_tag_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'body > pre'))
        WebDriverWait(BROWSER, TIMEOUT).until(testcases_pre_tag_present)
        time.sleep(2)

        testcases_pre_tag = BROWSER.find_element_by_tag_name('pre')
        testcases_xml_text = testcases_pre_tag.text
        all_testcases_dict = xmltodict.parse(testcases_xml_text)

        with open('rqm_url_utility_testing\\selenium_testcases\\project_{}_testcases_{}.txt'.format(project,
                str(get_page)), 'w') as selenium_testcases_file:
            selenium_testcases_file.write(json.dumps(all_testcases_dict))

        testcases_pagination_links = all_testcases_dict['feed']['link']

        print("get_page parameter >>> " + str(get_page))

        current_page, next_page, last_page = 0, 0, 0

        for link in testcases_pagination_links:
            if link["@rel"] == "self":
                current_page_link = link["@href"]
                current_page = current_page_link.split('&page=')[1]
                token = current_page_link.split('token=')[1].split('&amp;')[0]
            elif link["@rel"] == "next":
                next_page_link = link["@href"]
                next_page = next_page_link.split('&page=')[1]
            elif link["@rel"] == "last":
                last_page_link = link["@href"]
                last_page = last_page_link.split('&page=')[1]

        print("Testcases paginations links => " + json.dumps(testcases_pagination_links))
        print("current page >>> " + str(current_page) + " ; next page >>> " + str(next_page)
              + " ; last page >>> " + str(last_page))

        for testcase in all_testcases_dict['feed']['entry']:
            # print(testcase['id'])
            # print(testcase['title']['#text'])
            testcase_title = testcase['title']['#text']
            for link in testcase['link']:
                # print(json.dumps(link))
                if link['@title'] == 'Web Console':
                    testcase_id = link['@href'].split('&id=')[1]
                    print("Test Case ID >>> "+str(testcase_id))

                    # get_testscript_by_id(project, testscript_id)
                    get_testcase_by_id(project, testcase_id)

        # print("Nothing")

        if last_page > current_page:
            get_testcases(project, next_page_link)
        else:
            print("Please check the files generated .")

    except TimeoutException:
        print("Timed out waiting for page to load")


def jazz_login():
    """Login to 'jazz.cerner.com'

    And after login is successful, make a request to '/projects' route =>
    This will give you the XML response => List of all projects .
    Convert the XML to JSON and write to file 'rqm_url_utility_testing\\selenium_projects\\projects.txt'

    Loop through the Project titles [which are unique as far as my knowledge] =>
    Call the method to Get Testcases of each Project
    [ where Testcases are got Page wise => currently each page size = 50. ]"""

    BROWSER.get(JAZZ_LOGIN_URL)

    try:
        username_input_present = EC.presence_of_element_located((By.NAME, "j_username"))
        WebDriverWait(BROWSER, TIMEOUT).until(username_input_present)

        username_input_box = BROWSER.find_element_by_name('j_username')
        username_input_box.send_keys(JAZZ_NET_USERNAME)

        password_input_box = BROWSER.find_element_by_name('j_password')
        password_input_box.send_keys(JAZZ_NET_PASSWORD)

        login_button = BROWSER.find_element_by_css_selector('button[type="submit"]')
        login_button.click()

        time.sleep(2)

        # Open new tab
        BROWSER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        # You can use (Keys.COMMAND + 't') on other OSs

        # Load the projects route, which gives XML response.
        BROWSER.get(JAZZ_GET_ALL_PROJECTS_URL)

        projects_pre_tag_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'body > pre'))
        WebDriverWait(BROWSER, TIMEOUT).until(projects_pre_tag_present)
        time.sleep(2)

        # The XML is inside a <PRE> tag. So to get the XML, get the text inside 'PRE'
        projects_pre_tag = BROWSER.find_element_by_tag_name('pre')
        projects_xml_text = projects_pre_tag.text

        # Convert the XML to JSON
        all_projects_dict = xmltodict.parse(projects_xml_text)

        project_titles = [project['content']['ns2:project']['ns2:alias']['#text']
                          for project in all_projects_dict['feed']['entry']]

        print("All Projects => " + str(project_titles))

        with open('rqm_url_utility_testing\\selenium_projects\\projects.txt', 'w') as selenium_projects_file:
            selenium_projects_file.write(json.dumps(all_projects_dict))

        for project in project_titles:
            # get_testscripts(project, )
            get_testcases(project)

        time.sleep(2)

    except TimeoutException:
        print("Timed out waiting for page to load")


if __name__ == "__main__":
    jazz_login()

