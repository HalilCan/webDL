import urllib
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

'note: the urllib save call is a separate instance'


def clear_preview_url(url):
    url = url.replace("preview", "i")
    url = url.split("?")[0]
    return url


def save_media(media_url, folder_path, name):
    save_path = os.path.join(folder_path, name)
    urllib.urlretrieve(media_url, savePath)
    return 0


def unblock(driver):
    if "reddit.com: over 18?" in driver.title:
        yes_button = driver.find_element_by_name("continue")
        yes_button.click()
        return 0
    else:
        return 1


def openPreviews(driver):
    previewButtons = driver.find_elements_by_class_name("expando")
    for button in previewButtons:
        button.click()
    return 0


def getCorrectName(src, count):
    extension = src.split(".")[-1]
    name = os.path.join(str(count), extension)
    return name


def convert_and_save_from_previews(driver, count, folderPath):
    previewImages = driver.find_elements_by_xpath("//div[@class='media-preview-content']/a")
    downloadedCount = 0
    for previewImage in previewImages:
        src = previewImage.get_attribute("href")
        if count > 0:
            name = getCorrectName(src, count)
            save_media(src, folderPath, name)
            count -= 1
            downloadedCount += 1
        else:
            break
    if count > 0:
        return -1
    else:
        return downloadedCount


def downloadImageDirectlyFromExpandoList(driver):
    previewButtons = driver.find_elements_by_class_name("expando")
    for button in previewButtons:
        'TODO if time improvement significant'


def nextPage(driver):
    try:
        nextButton = driver.find_element_by_xpath("//span[@class='next-button']/a")
        nextButton.click()
    except NoSuchElementException:
        return -1


def downloadTopMediaInSubreddit(driver, address, count, fullFolderPath):
    while count > 0:
        unblockResult = unblock(driver)
        openPreviewsResult = openPreviews(driver)
        downloadedCount = convert_and_save_from_previews(driver, count, fullFolderPath)
        if downloadedCount == -1:
            return -1  # error while saving from previews
        count = count - downloadedCount
        nextPageResult = nextPage(driver)
        if nextPageResult == -1:
            return -2  # no more pages
    return 0


def main(argv):
    address = argv[1]
    maxCount = argv[2]

    folderPath = argv[3]
    cwd = os.getcwd()
    fullFolderPath = os.path.join(cwd, folderPath)

    driver = webdriver.Firefox()
    driver.get(address)
    downloadResult = downloadTopMediaInSubreddit(driver, address, maxCount, fullFolderPath)

    if downloadResult < 0:
        driver.close()
        return "HUMAN EXE ERROR"
    driver.close()