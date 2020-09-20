import webbrowser
import time
# import pyperclip
import xmltodict
import smtplib
import json
import csv
import glob
import os
import sys
import urllib
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
JAZZ_NET_USERNAME = "sb063964"
# JAZZ_NET_PASSWORD = "myjarvis@123"
JAZZ_NET_PASSWORD = sys.argv[1] #you need to pass your password as command-line argument
GET_FROM_PAGE = sys.argv[2] #you need to pass the page-number from which script should get testcases as command-line argument


JAZZ_RESOURCES_BASE_URL = r"https://jazz.cerner.com:9443/qm/service/com.ibm.rqm.integration.service.IIntegrationService/resources/"
JAZZ_GET_ALL_PROJECTS_URL = JAZZ_RESOURCES_BASE_URL + r"projects"
JAZZ_GET_PROJECT_TESTSCRIPTS_URL = JAZZ_RESOURCES_BASE_URL + r"{}/testscript?page={}"
JAZZ_GET_PROJECT_TESTCASES_URL = JAZZ_RESOURCES_BASE_URL + r"{}/testcase?page={}"
JAZZ_GET_TESTSCRIPT_BY_ID_URL = JAZZ_RESOURCES_BASE_URL + r"{}/testscript/urn:com.ibm.rqm:testscript:{}"
JAZZ_GET_TESTCASE_BY_TITLE_URL = JAZZ_RESOURCES_BASE_URL + r"{}/testcase?fields=feed/entry/content/testcase[title='{}']/*"
JAZZ_GET_TESTCASE_BY_ID_URL = JAZZ_RESOURCES_BASE_URL + r"{}/testcase/urn:com.ibm.rqm:testcase:{}?calmlinks=true"

# RQM_URL_UTILITY_FOLDER = r"//userprofiles01/XDdata06/SB063964/Desktop/jan_2019_rqm/"
RQM_URL_UTILITY_FOLDER = r'C:/Users/SB063964/Desktop/jazz_'+r'{}'.format(str(date.today()))+r'/'
os.makedirs(RQM_URL_UTILITY_FOLDER, exist_ok=True)
RQM_URL_UTILITY_JAR_PATH = r"C:/Users/SB063964/RQMUrlUtility.jar"

os.mkdir(RQM_URL_UTILITY_FOLDER+r'selenium_projects')
os.mkdir(RQM_URL_UTILITY_FOLDER+r'selenium_testcases')
os.mkdir(RQM_URL_UTILITY_FOLDER+r'selenium_testcase_details')
os.mkdir(RQM_URL_UTILITY_FOLDER+r'selenium_testscript_details')


def _finditem(obj, key):
    if isinstance(obj, list):
        for o in obj:
            return _finditem(o, key)
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = _finditem(v, key)
            if item is not None:
                return item


def run_rqm_url_utility(result_write_path, jazz_get_resources_url):
    """Used to make requests to Jazz API's -
    by making use of the RQM-URL-Utility Jar .
    The API Response is also written to a file .

    Params:
    jazz_get_resources_url - > API URL  for which you want to make a Request .
    result_write_path - > Path to which you want to write the API Response . """

    rqm_utility_dict = {
        'rqm_jar_path': RQM_URL_UTILITY_JAR_PATH,
        'user': JAZZ_NET_USERNAME,
        'password': JAZZ_NET_PASSWORD,
        'write_to_path': result_write_path,
        # 'get_jazz_testscripts_url': urllib.parse.quote(jazz_get_resources_url)
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

    # rqm = subprocess.run(args, shell=True) # DO NOT DELETE - OLD WORKING LINE
    try:
        subprocess.check_output(args, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("sowjanya13fb@gmail.com", "jarvis@123")
        #
        # msg = str(e.output)
        # server.sendmail("sowjanya13fb@gmail.com", "sbhatm1213@gmail.com", msg)
        # server.quit()

    # rqm.check_returncode() # DO NOT DELETE - OLD WORKING LINE


def get_testcase_by_id(project, testcase_id):
    """Get single Testcase Details - By ID .

    Params:
    project - > Project title .
    testcase_id - > ID of Testcase - of which you want to get the Details .

    Then call method to get details of Testscripts that come under this Testcase."""

    write_to_path = RQM_URL_UTILITY_FOLDER + r'selenium_testcase_details/{}_testcase_{}.txt'.format(project, testcase_id)

    run_rqm_url_utility(write_to_path, JAZZ_GET_TESTCASE_BY_ID_URL.format(project, testcase_id))

    try:
        if os.path.isfile(write_to_path):
            with open(write_to_path, 'r', encoding='utf8') as testcase_file:
                testcase_details = testcase_file.read()
        else:
            run_rqm_url_utility(write_to_path, JAZZ_GET_TESTCASE_BY_ID_URL.format(project, testcase_id))
            with open(write_to_path, 'r', encoding='utf8') as testcase_file:
                testcase_details = testcase_file.read()

        testcase_details_dict = xmltodict.parse(testcase_details)

        # print(testcase_details_dict)

        all_testscripts = None

        if isinstance(testcase_details_dict['ns2:testcase'].get('ns2:testscript'), dict):
            all_testscripts = [testcase_details_dict['ns2:testcase']['ns2:testscript']]
        elif isinstance(testcase_details_dict['ns2:testcase'].get('ns2:testscript'), list):
            all_testscripts = testcase_details_dict['ns2:testcase']['ns2:testscript']

        if all_testscripts:
            for testscript in all_testscripts:
                get_testscript_url = testscript['@href']
                testscript_title = get_testscript_url.split('/testscript/')
                testscript_id = get_testscript_url.split(':testscript:')
                # print(str(testscript_title))
                # print(str(testscript_id))
                if len(testscript_id) > 1:
                    print(" Testscript ID >>> "+str(testscript_id)+" >>> Now get details of this Testscript . ")
                    write_testscript_to_path = RQM_URL_UTILITY_FOLDER + r'selenium_testscript_details/testscript_{}.txt'.format(testscript_id[1])
                elif len(testscript_title) > 1:
                    print(" Testscript Title >>> "+str(testscript_title)+" >>> Now get details of this Testscript . ")
                    write_testscript_to_path = RQM_URL_UTILITY_FOLDER + r'selenium_testscript_details/testscript_{}.txt'.format(testscript_title[1])

                # print(write_testscript_to_path)
                # print(get_testscript_url)
                if write_testscript_to_path:
                    run_rqm_url_utility(write_testscript_to_path, get_testscript_url)

    except Exception as e:
        print(str(e))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("sowjanya13fb@gmail.com", "jarvis@123")
        #
        # msg = str(e)
        # server.sendmail("sowjanya13fb@gmail.com", "sbhatm1213@gmail.com", msg)
        # server.quit()
        # jazz_login()
        pass
    # print(xmltodict.parse(testcase_details))

#97200 completed => running from 0 again. to get the missed testcases
# def get_testcases(project, testcases_url=None, get_page=549):
def get_testcases(project, testcases_url=None, get_page=GET_FROM_PAGE):
    """Get Testcases of a Project using Pagination => Route used '/<project-name>/testcase?token=<token>&page=<page-num>'

    Above route will return List of <pageSize> [currently default 50] Testcase Links that come under project.
    Loop through Testcase links =>
    Then call method to get Details of Testcase.
    """
    try:
        # Open new tab
        BROWSER.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')

        default_page_zero = None
        # Load Testcase route, which gives XML response.
        if testcases_url is None:
            default_page_zero = True
            print("url-to-fetch:")
            print(JAZZ_GET_PROJECT_TESTCASES_URL.format(project, get_page))
            BROWSER.get(JAZZ_GET_PROJECT_TESTCASES_URL.format(project, get_page))
        else:
            print("url-to-fetch:")
            print(testcases_url.format(project, get_page))
            BROWSER.get(testcases_url.format(project, get_page))

        testcases_pre_tag_present = EC.presence_of_element_located((By.CSS_SELECTOR, 'body > pre'))
        WebDriverWait(BROWSER, TIMEOUT).until(testcases_pre_tag_present)
        time.sleep(2)

        # The XML is inside a <PRE> tag. So to get the XML, get the text inside 'PRE'
        testcases_pre_tag = BROWSER.find_element_by_tag_name('pre')
        testcases_xml_text = testcases_pre_tag.text

        # Convert the XML to JSON
        all_testcases_dict = xmltodict.parse(testcases_xml_text)

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

        if default_page_zero:
            # Write the JSON form of the response to file at
            # 'jan_2019_rqm\\selenium_testcases\\project_page_{}_testcases_page_{}.txt'
            with open('\\\\userprofiles01\\XDdata06\\SB063964\\Desktop\\jan_2019_rqm\\selenium_testcases\\project_page_{}_testcases_page_{}.txt'.format(project,
                    str(0)), 'w', encoding='utf8') as selenium_testcases_file:
                selenium_testcases_file.write(json.dumps(all_testcases_dict))
        else:
            # Write the JSON form of the response to file at
            # 'jan_2019_rqm\\selenium_testcases\\project_page_{}_testcases_page_{}.txt'
            with open('\\\\userprofiles01\\XDdata06\\SB063964\\Desktop\\jan_2019_rqm\\selenium_testcases\\project_page_{}_testcases_page_{}.txt'.format(project,
                    str(current_page)), 'w', encoding='utf8') as selenium_testcases_file:
                selenium_testcases_file.write(json.dumps(all_testcases_dict))


        # Loop through each Testcase, and call method to get Testcase Details using the particular Testcase ID
        for testcase in all_testcases_dict['feed']['entry']:
            # print(testcase['id'])
            # print(testcase['title']['#text'])
            testcase_title = testcase['title']['#text']

            for link in testcase['link']:
                # print(json.dumps(link))
                if link['@title'] == 'Web Console':
                    testcase_id = link['@href'].split('&id=')[1]

                    print("Test Case ID >>> "+str(testcase_id)+" >>> Now get details of this Test Case .")

                    # just adding logic to not get testcase details for testcase files which i have already generated :
                    # uncomment when real script need to be kept :
                    testcase_file_path = RQM_URL_UTILITY_FOLDER + r'selenium_testcase_details/{}_testcase_{}.txt'.format(
                        project, testcase_id)
                    if not os.path.isfile(testcase_file_path):
                        # get_testscript_by_id(project, testscript_id)
                        get_testcase_by_id(project, testcase_id)

        # If Current page is not the Last page, get next <page-size> [currently default 50] Testcases ,
        # by making Recursive call .
        if int(last_page) > int(current_page):
            get_testcases(project, next_page_link)
        else:
            print("Please check the files generated .")

    except TimeoutException as e:
        print("Timed out waiting for page to load")
        # print(str(e))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("sowjanya13fb@gmail.com", "jarvis@123")
        #
        # msg = str(e)
        # server.sendmail("sowjanya13fb@gmail.com", "sbhatm1213@gmail.com", msg)
        # server.quit()
        jazz_login()


def jazz_login():
    """Login to 'jazz.cerner.com'

    And after login is successful, make a request to '/projects' route =>
    This will give you the XML response => List of all projects .
    Convert the XML to JSON and write to file 'jan_2019_rqm\\selenium_projects\\projects.txt'

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

        if isinstance(all_projects_dict['feed'].get('entry'), dict):
            all_projects_entries = [all_projects_dict['feed']['entry']]
        elif isinstance(all_projects_dict['feed'].get('entry'), list):
            all_projects_entries = all_projects_dict['feed']['entry']

        project_titles = [project['content']['ns2:project']['ns2:alias']['#text']
                          for project in all_projects_entries]

        print("All Projects => " + str(project_titles))

        # Write the JSON form of the response to file at
        # 'jan_2019_rqm\\selenium_projects\\projects.txt'
        # with open('\\\\userprofiles01\\XDdata06\\SB063964\\Desktop\\jan_2019_rqm\\selenium_projects\\projects.txt',
        with open(RQM_URL_UTILITY_FOLDER+r'selenium_projects/projects.txt',
                  'w', encoding='utf8') as selenium_projects_file:
            selenium_projects_file.write(json.dumps(all_projects_dict))

        # Loop through each Project, call method to get Testcases associated with the particular Project
        for project in project_titles:
            # get_testscripts(project, )
            get_testcases(project)

        time.sleep(2)

    except TimeoutException as e:
        print("Timed out waiting for page to load")
        # print(str(e))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("sowjanya13fb@gmail.com", "jarvis@123")
        #
        # msg = str(e)
        # server.sendmail("sowjanya13fb@gmail.com", "sbhatm1213@gmail.com", msg)
        # server.quit()
        jazz_login()


if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    jazz_login()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

    # get_test_cases_json()

#
# def get_rqm_error_logs():
#     logging.basicConfig(filename=MEDIA_ROOT + '/jazz/logs_{}.txt'.format(datetime.datetime.date(datetime.datetime.now())),
#                         format='%(asctime)s %(message)s', level=logging.DEBUG)
#     # all_testcase_files = glob.glob(MEDIA_ROOT + '/jazz/testcase_details/*.txt')
#     testcase_pages = glob.glob(MEDIA_ROOT + '/jazz/selenium_testcases/*.txt')
#     print("Number of pages => " + str(len(testcase_pages)))
#     pages = [int(page.split("page_")[2].split(".txt")[0]) for page in testcase_pages]
#     # print(sorted(pages)[::-1][:50])
#     # print(sorted(testcase_pages)[::-1][:30])
#     # exit()
#     all_testcase_links = []
#     for page in sorted(testcase_pages):
#         with open(page) as testcase_page:
#             page_details = json.loads(testcase_page.read())
#             current_50_links = [ent['link']
#                                 for ent in page_details['feed']['entry']]
#             all_testcase_links += current_50_links
#
#     # print(all_testcase_links[::-1][:50])
#     # exit()
#     tc_filenames = []
#     all_tc_ids = []
#     for tc_links in all_testcase_links:
#         for links in tc_links:
#             if links['@title'] == 'Web Console':
#                 tc_id = links['@href'].split('&id=')[1]
#             elif 'com.ibm.rqm.integration.service.IIntegrationService/resources/' in links['@href']:
#                 tc_project = links['@href'].split(
#                     'com.ibm.rqm.integration.service.IIntegrationService/resources/')[1].split('/testcase')[0]
#         tc_file_name = MEDIA_ROOT + '/jazz/testcase_details\\' + \
#                        str(tc_project) + '_testcase_' + str(tc_id) + '.txt'
#         all_tc_ids.append(tc_id)
#         tc_filenames.append(tc_file_name)
#
#     print("Actual number of testcases to be got => " + str(len(list(set(tc_filenames)))))
#
#     all_testcase_files = glob.glob(MEDIA_ROOT + '/jazz/testcase_details/*.txt')
#
#     print("But number of testcases got => " + str(len(list(set(all_testcase_files)))))
#
#     missed_tc_filenames = []
#     missed_ts_filenames = []
#     readerror_tc_filenames = []
#     readerror_ts_filenames = []
#     missed_tc_filenames += [filename for filename in tc_filenames if filename not in all_testcase_files]
#     # for filename in list(set(tc_filenames)):
#     #     if filename not in list(set(all_testcase_files)):
#     #         print(filename)
#     #         exit()
#     # print(missed_tc_filenames[:20])
#     print("So number of missed testcases => " + str(len(missed_tc_filenames)))
#
#     df_tc = pd.DataFrame({'missed_testcase_links': missed_tc_filenames})
#     df_tc.to_csv(MEDIA_ROOT + '/jazz/missed_testcases_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
#     # exit()
#
#     readtcfile_errors_count = 0
#     readtsfile_errors_count = 0
#     ts_notfound_count = 0
#     for testcase_file in all_testcase_files:
#         # print(testcase_file)
#         with open(testcase_file, encoding="utf8") as testcase_details:
#             try:
#                 testcase_details_str = testcase_details.read()
#                 testcase_details_dict = xmltodict.parse(testcase_details_str)
#             except Exception as e:
#                 logging.error("Some Error while trying to read Testcase file : \n" + testcase_file, str(e))
#                 readtcfile_errors_count += 1
#                 readerror_tc_filenames += [testcase_file]
#
#             # logging.info("testscripts = >>>"+str(testcase_details_dict['ns2:testcase'].get('ns2:testscript')))
#
#             all_testscripts = None
#             if isinstance(testcase_details_dict['ns2:testcase'].get('ns2:testscript'), dict):
#                 all_testscripts = [
#                     testcase_details_dict['ns2:testcase']['ns2:testscript']]
#             elif isinstance(testcase_details_dict['ns2:testcase'].get('ns2:testscript'), list):
#                 all_testscripts = testcase_details_dict['ns2:testcase']['ns2:testscript']
#
#             if all_testscripts:
#                 for testscript in all_testscripts:
#                     get_testscript_url = testscript['@href']
#                     testscript_title = get_testscript_url.split('/testscript/')
#                     testscript_id = get_testscript_url.split(':testscript:')
#
#                     testscript_file_xml = None
#                     if len(testscript_id) > 1:
#                         # testscript_file_xml = os.path.join(
#                         #     MEDIA_ROOT, 'jazz', 'testscript_details', 'testscript_' + str(testscript_id[1]) + '.txt')
#                         testscript_file_xml = MEDIA_ROOT + '/jazz/testscript_details/testscript_{}.txt'.format(str(testscript_id[1]))
#                     elif len(testscript_title) > 1:
#                         # testscript_file_xml = os.path.join(
#                         #     MEDIA_ROOT, 'jazz', 'testscript_details', 'testscript_' + str(testscript_title[1]) + '.txt')
#                         testscript_file_xml = MEDIA_ROOT + '/jazz/testscript_details/testscript_{}.txt'.format(str(testscript_title[1]))
#
#                     if testscript_file_xml:
#                         if os.path.exists(testscript_file_xml):
#                             # print("Testscript file EXISTS => " + testscript_file_xml)
#                             # logging.info("Testscript file EXISTS => " + testscript_file_xml)
#                             with open(testscript_file_xml, 'r', encoding="utf8") as testscript_file:
#                                 try:
#                                     testscript_details_str = testscript_file.read()
#                                     testscript_details_dict = xmltodict.parse(testscript_details_str)
#                                 except Exception as e:
#                                     # logging.error("Some Error while trying to read Testscript file : \n" + testscript_file_xml)
#                                     readtsfile_errors_count += 1
#                                     readerror_ts_filenames += [get_testscript_url]
#                         else:
#                             # logging.error("Testscript file was NOT FOUND for : " + testscript_file_xml)
#                             ts_notfound_count += 1
#                             missed_ts_filenames += [get_testscript_url]
#             else:
#                 continue
#     print(readtcfile_errors_count)
#     print(readtsfile_errors_count)
#     print(ts_notfound_count)
#
#     df_ts = pd.DataFrame({'missed_testscript_links': missed_ts_filenames})
#     df_ts.to_csv(MEDIA_ROOT + '/jazz/missed_testscripts_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
#
#     df_tc_read = pd.DataFrame({'read_tc_errors': readerror_tc_filenames})
#     df_tc_read.to_csv(MEDIA_ROOT + '/jazz/readerror_tc_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
#     df_ts_read = pd.DataFrame({'read_ts_errors': readerror_ts_filenames})
#     df_ts_read.to_csv(MEDIA_ROOT + '/jazz/readerror_ts_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
#     return True
