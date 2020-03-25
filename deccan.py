#!/usr/bin/python3
import selenium,time,os,shutil,sys,webbrowser,smtplib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from PyPDF2 import PdfFileMerger
from subprocess import Popen,PIPE
from threading import Thread
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

class EPaper:

    def __init__(self):
        self.merger = PdfFileMerger()
        self.order = []
        self.date = ""
        self.folder_name = "deccan_temp_files"
        self.file_name = ""

        try:
            os.mkdir(self.folder_name)
        except FileExistsError:
            pass

        mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", os.path.join(os.getcwd(),self.folder_name))
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
        fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
        fp.set_preference("pdfjs.disabled", True)
        op = Options()
        op.headless = True

        if sys.platform == 'linux':
            log_path = '/dev/null'
        else:
            log_path = 'NUL'

        try:
            self.browser = webdriver.Firefox(options=op,firefox_profile=fp,service_log_path=log_path)
            self.browser.get("http://www.deccanheraldepaper.com/")
        except:
            exit(42)

    def edition(self, REFRESH_COUNT=0):
        def choose(id,param,limit=None):
            DEFAULT_VALUE = 0
            self.browser.find_element_by_id('btnPublicationsPanel').click()
            data_menu = self.browser.find_element_by_id(id)
            data = data_menu.find_elements_by_tag_name('option')[1:]

            if os.environ.get('HIDDEN_ID') == 'BATMAN':
                unit = data[DEFAULT_VALUE]
            else:
                if param == 'city':
                    for i,j in enumerate(data[:limit],1):
                        if i==1:
                            print(str(i),' - ',j.get_attribute('value'),' [default]')
                        else:
                            print(str(i),' - ',j.get_attribute('value'))
                else:
                    for i,j in enumerate(data[:limit],1):
                        s = j.get_attribute('value')
                        d = (s[6:]+'/'+s[4:6]+'/'+s[:4])
                        if i==1:
                            print(str(i),' - ',d,' [default]')
                        else:
                            print(str(i),' - ',d)

                ch = input(f"\nChoose the {param}:\n> ")
                if len(ch) == 0:
                    unit = data[DEFAULT_VALUE]
                else:
                    for i,j in enumerate(data[:limit],1):
                        if ch == str(i):
                            unit = data[i-1]
                            break

            if param == 'date':
                s = unit.get_attribute('value')
                self.date = (s[6:]+'_'+s[4:6]+'_'+s[:4])
                self.file_name = self.date + '_epaper.pdf'

            unit.click()
            return

        try:
            choose('pubFilterEdition','city')
            time.sleep(2)
            choose('pubFilterPubDate','date',7)
        except:
            REFRESH_COUNT += 1
            if REFRESH_COUNT >= 10:
                print("1: ", REFRESH_COUNT, "\n", "WE ARE IN THE DEEP")
                self.browser.refresh()
                self.edition(REFRESH_COUNT=0)
            time.sleep(3)
            print("2: ",REFRESH_COUNT)
            self.edition(REFRESH_COUNT)

        time.sleep(3)
        return

    def info(self):
        print("\nNumber of pages : "+str(self.browser.execute_script('return cxdCmp.infra.getPages().length'))+"\n\nProgress : \nPlease wait...",end='')

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
                f = os.path.join(self.folder_name,i.get_attribute('src')[-10:]).replace('png','pdf')
                self.browser.execute_script("arguments[0].click();",i)
                print('\r',count,' : ',f,end='')
                count+=1
                self.order.append(f)
                time.sleep(1)

            # Go back and click on 'next' button to download remaining pages
            time.sleep(2)
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

    def view(self):
        print(f"\n\nYour E-Paper : {self.file_name} is ready!!!\n")
        if 'win' in sys.platform.lower():
            webbrowser.open(self.file_name)
        else:
            Popen(["xdg-open",self.file_name],stdout=PIPE,stderr=PIPE,close_fds=True)

    def mail(self):
        message = MIMEMultipart()
        sender_email = "kowligi1998@gmail.com"

        def build_payload():
            message["From"] = sender_email
            message["Subject"] = f"Deccan Herald E-Paper on {self.date.replace('_','/')}"

            with open(self.file_name,"rb") as f:
                part = MIMEBase("application","octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition",f"attachment; filename={self.file_name}")
            message.attach(part)

        t = Thread(target=build_payload)
        t.start()

        sender_password = getpass("Enter the sender email password\n> ")
        recepient = input("Enter the recepient Email ID\n> ")
        extra_msg = input("Please enter any personal message/note for the recepient and then press Enter\n> ")

        if t.isAlive():
            print("Sending mail... Please wait...")
            t.join()

        message["To"] = recepient
        message.attach(MIMEText(extra_msg+"\n\n\nhttps://github.com/SuhasBk/Deccan_EPaper/"))
        final_payload = message.as_string()

        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(sender_email,sender_password)
            server.sendmail(sender_email,recepient,final_payload)
        print("E-mail sent successfully!!!")

if __name__ == '__main__':
    try:        
        deccan = EPaper()        
        deccan.edition()
        deccan.info()
        deccan.download()
        #deccan.view()

        if os.environ.get("HIDDEN_ID") != 'BATMAN':         # personal preference
            share = input("\nDo you want to mail it? ('Y' / 'y')\n> ")
            if 'y' in share.lower():
                deccan.mail()
    finally:
        shutil.rmtree("deccan_temp_files")
