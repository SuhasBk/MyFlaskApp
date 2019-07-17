#!/usr/bin/python3

import time,sys,os,selenium

# To let Python aware of chromedriver required.. The PATH variable is modified temporarily!
os.environ['PATH'] += ':'+os.getcwd()

from getpass import getpass
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from subprocess import call

def debug(*args,**kwargs):
    while(True):
        try:
            cmd=input("Enter the commands BOSS!\n")
            if cmd=='exit':
                return
            exec(cmd)
        except:
            print('NOT WORKING!')
            pass

#Global variables:
fails = 0
debug_mode = False
url = "http://www.my-gurukul.com/login.aspx?BROWSERWINDOW=&BROWSER=FF&DF=MM/DD/YYYY&CF=MYGURUKUL&SID=1022"
logged_in_url = 'http://www.my-gurukul.com/frmImygurukul.aspx'

print("Welcome To MyGurukul Terminal Client\n")
#login details and data selection
try:
    usn=sys.argv[1]
    pas=sys.argv[2]
    d=sys.argv[3]
except(IndexError):
    print("Usage : 'guru.py [usn] [password] [a/m]\n")
    usn=input("Enter your USN :\n")
    pas=getpass("Enter the password (hidden) :\n")
    d=input("Attendance ('a') OR Marks? ('m')\n")

#headless : like a covert spy ;)
if len(sys.argv[1:])<=3:
    options = Options()
    options.headless = True
    b = webdriver.Firefox(options=options)
else:
    debug_mode = True
    print('Running in debugging mode')
    b = webdriver.Firefox()

#collecting data based on selection type:
def data():
    #attendance:
    if d == 'a' or d == 'A':
        #fetch raw data:
        u = b.find_elements_by_class_name('underline')  #Clicking the NAV link
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

        if debug_mode:
            debug()
            pass

        #b.save_screenshot('attendance.png')

    #marks:
    elif d == 'm' or d == 'M':
        #fetch raw data:
        b.switch_to.frame(b.find_element_by_id('mygurukuliframe_submenu'))
        b.find_element_by_id('imgid_14').click()
        b.switch_to.default_content()
        b.switch_to.frame('mygurukuliframe')
        time.sleep(5)
        try:
            marks = b.find_elements_by_class_name('tblbrdr')[1]
            tr = marks.find_elements_by_tag_name('tr')[1:]
        except:
            b.quit()
            exit("Marks error")

        for rows in tr:
            cols = rows.find_elements_by_tag_name('td')
            print("SUBJECT NAME : ",cols[0].text.lstrip(),end=' :\n')
            print("LA - I MARKS (10) : ",cols[8].text)
            print("MSE - I MARKS (30) : ",cols[9].text,end='\n\n')

        b.save_screenshot('marks.png')
        img = Image.open('marks.png')
        img.show()

#handle login, circulars and feedback forms:
def handler():
    try:
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

    except selenium.common.exceptions.ElementClickInterceptedException as circular:
        print("\nA circular was encountered\n")
        b.save_screenshot('circular.png')
        try:
            call("xdg-open circular.png",shell=True)
        except:
            os.system("start circular.png")
        b.find_element_by_xpath("//img[contains(@src,'images/lbxclose.jpeg')]").click()
        print('done')
        b.switch_to.default_content()
        data()
        return

#entry point to the portal:
try:
    handler()
finally:
    try:
        b.quit()
        os.remove('marks.png')
        exit('Thank you for using MyGururkul!')
    except OSError:
        pass
