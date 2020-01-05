import urllib
import os
import sys
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
    urllib.urlretrieve(media_url, save_path)
    return 0


def unblock(driver):
    if "reddit.com: over 18?" in driver.title:
        yes_button = driver.find_element_by_name("continue")
        yes_button.click()
        return 0
    else:
        return 1


def open_previews(driver):
    preview_buttons = driver.find_elements_by_class_name("expando")
    for button in preview_buttons:
        button.click()
    return 0


def get_correct_name(src, count):
    extension = src.split(".")[-1]
    name = os.path.join(str(count), extension)
    return name


def convert_and_save_from_previews(driver, count, folder_path):
    preview_images = driver.find_elements_by_xpath("//div[@class='media-preview-content']/a")
    downloaded_count = 0
    for preview_image in preview_images:
        src = preview_image.get_attribute("href")
        if count > 0:
            name = get_correct_name(src, count)
            save_media(src, folder_path, name)
            count -= 1
            downloaded_count += 1
        else:
            break
    if count > 0:
        return -1
    else:
        return downloaded_count


def download_image_directly_from_expando_list(driver):
    preview_buttons = driver.find_elements_by_class_name("expando")
    for button in preview_buttons:
        'TODO if runtime improvement significant'


def next_page(driver):
    try:
        next_button = driver.find_element_by_xpath("//span[@class='next-button']/a")
        next_button.click()
    except NoSuchElementException:
        return -1


def download_top_media_in_subreddit(driver, subreddit, count, full_folder_path):
    prefix = "http://old.reddit.com/r/"
    fullUrl = prefix + subreddit

    driver.get(fullUrl)

    while count > 0:
        unblock_result = unblock(driver)
        open_previews_result = open_previews(driver)
        downloaded_count = convert_and_save_from_previews(driver, count, full_folder_path)
        if downloaded_count == -1:
            return -1  # error while saving from previews
        count = count - downloaded_count
        next_page_result = next_page(driver)
        if next_page_result == -1:
            return -2  # no more pages
    return 0


def main():
    # usage: python redditDL.py subreddit_name max_media_download_count folder_name
    # folder needs to be within cwd
    args = sys.argv

    subreddit = args[1]
    max_count = args[2]

    folder_path = args[3]
    cwd = os.getcwd()
    full_folder_path = os.path.join(cwd, folder_path)

    driver = webdriver.Firefox()
    download_result = download_top_media_in_subreddit(driver, subreddit, max_count, full_folder_path)

    if download_result < 0:
        driver.close()
        print("HUMAN EXE ERROR")
        return download_result
    driver.close()
    return 0


if __name__ == "__main__":
    main()