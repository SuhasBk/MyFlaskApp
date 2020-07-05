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

class Deccan:

    def __init__(self):
        TEMP_FOLDER = "temp_files"
        download_dir = os.path.join(os.getcwd(), TEMP_FOLDER)

        self.merger = PdfFileMerger()
        self.order = []
        self.date = ""
        self.folder_name = TEMP_FOLDER = "temp_files"
        self.file_name = ""

        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")

        chrome_options.add_experimental_option('prefs',  {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        log_path = "NUL" if sys.platform.startswith('win') else '/dev/null'

        if os.environ.get("CHROMEDRIVER_PATH"):
            self.browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options, service_log_path=log_path)
        else:
            self.browser = webdriver.Chrome(options=chrome_options, service_log_path=log_path)

        print("Chrome browser initialized")
        try:
            os.mkdir(TEMP_FOLDER)
        except FileExistsError:
            pass

        self.browser.get("http://www.deccanheraldepaper.com/")

    def edition(self, REFRESH_COUNT=0):
        def choose(id, param, limit=None):
            DEFAULT_VALUE = 0
            self.browser.find_element_by_id('btnPublicationsPanel').click()
            data_menu = self.browser.find_element_by_id(id)
            data = data_menu.find_elements_by_tag_name('option')[1:]

            if param == 'date':
                unit = data[DEFAULT_VALUE]
                s = unit.get_attribute('value')
                self.date = (s[6:]+'_'+s[4:6]+'_'+s[:4])
                self.file_name = f'epaper{sys.argv[2]}.pdf'
            else:
                unit = data[int(sys.argv[2])]

            unit.click()
            return

        try:
            choose('pubFilterEdition', 'city')
            time.sleep(2)
            choose('pubFilterPubDate', 'date', 7)
        except:
            REFRESH_COUNT += 1
            if REFRESH_COUNT >= 10:
                self.browser.refresh()
                self.edition(REFRESH_COUNT=0)
            time.sleep(3)
            self.edition(REFRESH_COUNT)

        time.sleep(3)
        return

    def download(self):
        next = True
        count = 0
        while next:
            # Press the 'download' button and get a list of number of pages
            try:
                self.browser.find_element_by_id('btnPrintSave').click()
                time.sleep(2)
                pages = self.browser.find_elements_by_class_name('thumbImage2')
            except:
                time.sleep(3)
                self.download()

            # Download each page of paper to the temporary folder as an individual pdf file
            for i in pages:
                f = os.path.join(self.folder_name, i.get_attribute('src')[-10:]).replace('png', 'pdf')
                print('\r', count, ' : ', f, end='')
                self.browser.execute_script("arguments[0].click();", i)
                self.order.append(f)
                count += 1
                time.sleep(1)

            # Go back and click on 'next' button to download remaining pages
            time.sleep(1)
            self.browser.find_element_by_id('printSavePanel').send_keys(Keys.ESCAPE)
            time.sleep(2)
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

def mail(file_name):
        message = MIMEMultipart()
        part = MIMEBase("application", "octet-stream")
        message["Subject"] = f"Deccan Herald E-Paper on {str(datetime.date.today())}"

        with open(file_name,"rb") as f:
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition",f"attachment; filename={file_name}")
        message.attach(part)

        sender_email = "kowligi1998@gmail.com"
        sender_password = os.environ.get('MYPWD')

        recepients = sys.argv[1]
        message["From"] = sender_email
        message.attach(MIMEText("\n\n\nhttps://github.com/SuhasBk/ePapers/"))
        final_payload = message.as_string()

        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(sender_email,sender_password)
            server.sendmail(sender_email,recepients,final_payload)

def main():
    try:
        if 'file_exists' in sys.argv:
            pass
        else:
            deccan = Deccan()
            deccan.edition()
            deccan.download()
        print("Successfully downloaded! Sending file...")
    finally:
        try:
            shutil.rmtree(deccan.folder_name)
            deccan.browser.quit()
        except:
            pass
        mail(f'epaper{sys.argv[2]}.pdf')

if __name__ == '__main__':
    main()
