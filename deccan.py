#!/usr/bin/python3
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from PyPDF2 import PdfFileMerger
from subprocess import *
import time,os,shutil,sys

class EPaper():

    def __init__(self):
        self.merger = PdfFileMerger()
        self.order = []
        self.name = time.ctime()[:10]
        try:
            os.mkdir(self.name)
        except:
            pass

        mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", os.getcwd()+'/'+self.name)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
        fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
        fp.set_preference("pdfjs.disabled", True)

        op = Options()
        op.headless = True
        if len(sys.argv) > 1:
            self.browser = webdriver.Firefox(firefox_profile=fp)
        else:
            self.browser = webdriver.Firefox(firefox_profile=fp,firefox_options=op)
        self.browser.get("http://www.deccanheraldepaper.com/")

    def edition(self):
        try:
            self.browser.find_element_by_id('btnPublicationsPanel').click()
            edition = self.browser.find_element_by_id('pubFilterEdition')
            edition.click()
            edition.find_elements_by_tag_name('option')[1].click()
        except:
            time.sleep(3)
            self.edition()

    def download(self):
        next = True
        count = 1
        while next:
            try:
                try:
                    self.browser.find_element_by_id('btnPrintSave').click()
                except:
                    time.sleep(3)
                    self.download()
                time.sleep(2)
                pages = self.browser.find_elements_by_class_name('thumbImage2')
                for i in pages:
                    file = os.path.join(self.name,i.get_attribute('src')[-10:]).replace('png','pdf')
                    i.click()
                    count+=1
                    self.order.append(file)
                    time.sleep(1)
                time.sleep(2)
                self.browser.find_element_by_id('printSavePanel').send_keys(Keys.ESCAPE)
                time.sleep(2)
                self.browser.find_element_by_id('btn-next').click()
            except:
                next = False


    def merge(self):
        name = self.name+' epaper.pdf'
        for i in self.order:
            self.merger.append(i)

        self.merger.write(name)
        self.merger.close()
        print(name)


try:
    deccan = EPaper()
    deccan.edition()
    time.sleep(3)
    deccan.download()
    deccan.merge()
finally:
    deccan.browser.quit()
    shutil.rmtree(deccan.name)
    os.remove('geckodriver.log')
