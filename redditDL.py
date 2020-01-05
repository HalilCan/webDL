import urllib
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

'note: the urllib save call is a separate instance'

def clearPreviewUrl(url):
    url = url.replace("preview", "i")
    url = url.split("?")[0]
    return url

def saveMedia(mediaUrl, folderPath, name):

    savePath = os.path.join(folderPath,)

def downloadTopImagesInSubreddit(driver, address, maxCount, fullFolderPath):

def unblock(driver):
    if "reddit.com: over 18?" in driver.title:
        yesButton = driver.find_element_by_name("continue")
        yesButton.click()
    else:
        return

def openPreviews(driver):


def convertAndSavePreviews(driver, previewImgArray):

def main(argv):
    address = argv[1]
    maxCount = argv[2]

    folderPath = argv[3]
    cwd = os.getcwd()
    fullFolderPath = os.path.join(cwd, folderPath)

    downloadTopImagesInSubreddit(driver, address, maxCount, fullFolderPath)



    driver = webdriver.Firefox()
    driver.get('http://www.google.com/recaptcha/demo/recaptcha')

    # get the image source
    img = driver.find_element_by_xpath('//div[@id="recaptcha_image"]/img')
    src = img.get_attribute('src')

    # download the image
    urllib.urlretrieve(src, "captcha.png")

    fullfilename = os.path.join(myPath, filename)
    urllib.urlretrieve(url, fullfilename)

    driver.close()