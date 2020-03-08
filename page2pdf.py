import os
import sys
import datetime
import json
import pdfkit
import urllib.request
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import DesiredCapabilities

print("Hello")
print("__name__ value: ", __name__)
now = datetime.datetime.now()


def main():
    print("BY GAWD")
    print(sys.argv)
    print(now)
    # usage: python pageDL.py url save_format
    # folder needs to be within cwd
    args = sys.argv

    url = args[1]
    save_format = args[2]
    chrome_driver_path = os.getcwd() + "\chromedriver.exe"
    chrome81_path = "C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe"
    print(chrome_driver_path)

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--print-to-pdf")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-notifications')

    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}

    chrome_options.binary_location = chrome81_path
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True

    pdfkit.from_url('https://www.google.com/search?client=firefox-b-1-d&q=Error%3A+Failed+to+load+about%3Ablank%2C+with+network+status+code+301+and+http+status+code+0+-+Protocol+%22about%22+is+unknown', 'page.pdf')

    browser = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities,
                               executable_path=chrome_driver_path)

    browser.get(url)
    browser.save_screenshot("someFile.jpg")
    browser.execute_script("window.print();")

    browser.quit()

if __name__ == '__main__':
    main()