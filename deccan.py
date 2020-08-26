#!/usr/bin/python3
import time
import os
import shutil
import sys
import datetime
import smtplib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PyPDF2 import PdfFileMerger
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Deccan:

    def __init__(self, edition_number):
        TEMP_FOLDER = "temp_files"
        download_dir = os.path.join(os.getcwd(), TEMP_FOLDER)

        self.merger = PdfFileMerger()
        self.order = []
        self.date = ""
        self.folder_name = TEMP_FOLDER = "temp_files"
        self.file_name = ""
        self.edition_number = edition_number

        chrome_options = Options()
        # chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")

        chrome_options.add_experimental_option('prefs',  {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        log_path = '/dev/null'

        if os.environ.get("CHROMEDRIVER_PATH"):
            chrome_options.add_argument("--headless")
            self.browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options, service_log_path=log_path)
        else:
            # chrome_options.add_argument("--headless")
            self.browser = webdriver.Chrome(options=chrome_options, service_log_path=log_path)

        self.browser.set_window_size(1440, 1000)

        try:
            os.mkdir(TEMP_FOLDER)
        except FileExistsError:
            pass

        self.browser.get("http://www.deccanheraldepaper.com/")
    
    def wait_and_find(self, element, selector, root):
        try:
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((selector,element)))
            return root.find_elements(selector, element)
        except TimeoutException:
            raise Exception("Internal Server Error")
    
    def choose_edition(self):
        time.sleep(3)
        self.file_name = f'epaper{self.edition_number}.pdf'
        
        try:
            pub_btn = self.wait_and_find('btnPublicationsPanel', By.ID, self.browser)[0]
            self.browser.execute_script("arguments[0].click()", pub_btn)

            data_menu = self.browser.find_element_by_id('pubFilterEdition')
            data = data_menu.find_elements_by_tag_name('option')[1:]

            city = data[int(self.edition_number)]
            self.browser.execute_script("arguments[0].click();", city)

            time.sleep(2)
            return True, ''
        except Exception as e:
            return False, e

    def download(self):
        next = True
        count = 0
        while next:
            # Press the 'download' button and get a list of number of pages
            try:
                self.browser.find_element_by_id('btnPrintSave').click()
                time.sleep(1)
                pages = self.browser.find_elements_by_class_name('thumbImage2')
            except:
                time.sleep(3)
                self.download()

            # Download each page of paper to the temporary folder as an individual pdf file
            for i in pages:
                f = os.path.join(self.folder_name, i.get_attribute('src')[-10:]).replace('png', 'pdf')
                self.browser.execute_script("arguments[0].click();", i)
                self.order.append(f)
                count += 1

            # Go back and click on 'next' button to download remaining pages
            self.browser.find_element_by_id('printSavePanel').send_keys(Keys.ESCAPE)
            time.sleep(1)
            try:
                self.browser.find_element_by_id('btn-next').click()
            except:
                next = False

        self.browser.quit()
        self.merge()

    def merge(self):
        self.order = sorted(set(self.order), key=self.order.index)
        for page in self.order:
            self.merger.append(page)
        self.merger.write(self.file_name)
        self.merger.close()

def main():
    try:
        edition_number = sys.argv[1]
        pdf_file_name = f'epaper{edition_number}.pdf'

        if pdf_file_name in os.listdir():
            raw_time = os.stat(pdf_file_name).st_mtime
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(raw_time))
            if str(datetime.datetime.today().date()) == mod_time.split()[0]:
                pass
            else:
                os.remove(pdf_file_name)
        else:
            deccan = Deccan(edition_number)
            result = deccan.choose_edition()
            if not result[0]:
                raise Exception(result[1])
            deccan.download()

    finally:
        try:
            shutil.rmtree(deccan.folder_name)
            deccan.browser.quit()
        except:
            pass
        

if __name__ == '__main__':
    main()
