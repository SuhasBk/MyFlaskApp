#!/usr/bin/python3

import time,sys,os,selenium
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from subprocess import call

#Global variables:
fails = 0
url = "http://www.my-gurukul.com/login.aspx?BROWSERWINDOW=&BROWSER=FF&DF=MM/DD/YYYY&CF=MYGURUKUL&SID=1022"
logged_in_url = 'http://www.my-gurukul.com/frmImygurukul.aspx'

print("Welcome To MyGurukul Terminal Client\n")
usn=sys.argv[1]
pas=sys.argv[2]

chrome_options = Options()
chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
chrome_options.headless = True
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
b = webdriver.Chrome(chrome_options=chrome_options)

#collecting data based on selection type:
def data():
    #attendance
    #fetch raw data:
    u = b.find_elements_by_class_name('underline')
    u.pop().click()
    time.sleep(5)

    b.switch_to.frame('mygurukuliframe')
    try:
        att = b.find_element_by_class_name('tblbrdr')
        tr = att.find_elements_by_tag_name('tr')[1:]
    except:
        b.quit()
        exit("Attendance error")

    for index,rows in enumerate(tr):
        cols = rows.find_elements_by_tag_name('td')
        print(index," - SUBJECT NAME : ",cols[0].text.lstrip(),end=' :\n')
        print("CLASS HELD : ",cols[2].text.lstrip())
        print("ATTEND : ",cols[3].text.lstrip())
        print("ABSENT : ",cols[5].text.lstrip())
        print("ATTENDANCE PERCENTAGE : ",cols[6].text.lstrip(),end='%\n\n')

    sub = input("\nPlease select the subject to know the complete details... ('exit' to quit)\n")

    for index in range(len(tr)):
        if sub == str(index):
            tr[index].find_elements_by_tag_name('td')[2].click()
            time.sleep(2)
            b.switch_to_window(b.window_handles[1])

            months = b.find_element_by_id('att_def').find_elements_by_tag_name('tr')
            for i,j in enumerate(months):
                temp_month = j.find_elements_by_tag_name('td')
                print(i,' - ',temp_month[0].get_attribute('id').upper(),end=' :\n')
                print('CLASS HELD - ',temp_month[1].text)
                print('ABSENT - ',temp_month[2].text)
                print('PRESENT - ',temp_month[3].text)
                print('PRESENT % - ',temp_month[4].text,end='%\n\n')

            month = input("\nSelect the month... ('exit' to quit, 'q' to go back)\n")

            count = 0

            for i,j in enumerate(months[:]):
                if month == str(i):
                    j.find_element_by_tag_name('td').click()
                    time.sleep(2)
                    b.close()
                    b.switch_to_window(b.window_handles[1])
                    details = b.find_element_by_id('att_def').find_elements_by_tag_name('tr')

                    for rows in details:
                        temp_d = rows.find_elements_by_tag_name('td')
                        status = temp_d[4].find_element_by_tag_name('img').get_attribute('title').lower()
                        if status == 'absent':
                            count+=1
                            print("\nDATE - ",temp_d[0].text.lstrip())
                            print("DAY - ",temp_d[1].text.lstrip())
                            print("STATUS - "+status.upper())

                    if count == 0:
                        print("Attended all classes this month!\n")

                elif month == 'exit':
                    return
                elif month == 'q':
                    pass
        elif sub == 'exit':
            return

#handle login, circulars and feedback forms:
def handler():
    b.get(url)
    b.find_element_by_id('txtUserName').send_keys(usn.upper())
    b.find_element_by_id('txtPassword').send_keys(pas.upper())
    b.find_element_by_id('Validate').click()

    if b.current_url == logged_in_url:
        print('\nLogged in successfully!\n')
        time.sleep(1)
        data()
        return
    else:
        global fails
        fails+=1
        print("Failed {} time(s)".format(fails))
        if fails == 5:
            b.quit()
            exit('Check USN/Password and try again')
        handler()

#entry point to the portal:
try:
    handler()
finally:
    try:
        b.quit()
        exit('Thank you for using MyGururkul!')
    except OSError:
        pass
