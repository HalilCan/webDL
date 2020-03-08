import os
import sys
import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import DesiredCapabilities

'note: the urllib save call is a separate instance'
now = datetime.datetime.now()


def main():
    print("BY GAWD")
    print(sys.argv)
    print(sys.path)
    # usage: python pageDL.py url save_format
    # folder needs to be within cwd
    args = sys.argv

    url = args[1]
    print(url)
    save_format = args[2]
    print(save_format)
    chrome_driver_path = os.getcwd() + "\chromedriver.exe"
    print(chrome_driver_path)

    is_flat = 0
    if len(args) > 3:
        flags = args[2:]
        if "-f" in flags:
            is_flat = 1

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--print-to-pdf")
    chrome_options.add_argument("--disable-extensions")

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True

    browser = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)

    browser.get(url)
    browser.save_screenshot("someFile.pdf")
    browser.save_screenshot("someFile.jpg")

    #download_daemon = pageDownloader(driver, url, save_format)
    #download_result = download_daemon.download()

    #if download_result < 0:
    #    driver.close()
    #    print("HUMAN EXE ERROR")
    #    return download_result

    browser.close()
    return 0


def is_403_error_page(url):
    try:
        response = urllib.request.urlopen(url)
        if response.status == 403:
            return 1
        else:
            return 0
    except HTTPError:
        return 1
    except URLError:
        print("url error in is_403_error_page(" + url + ")")
        return 1


if __name__ == "__main__":
    main()