import urllib.request
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
    urllib.request.urlretrieve(media_url, save_path)
    return 0


def unblock(driver):
    if "reddit.com: over 18?" in driver.title:
        yes_button = driver.find_elements_by_xpath("//div[@class='buttons']/button")[1]
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
    name = str(count) + "." + extension
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


def download_images_in_page_directly_from_expando_list(driver, max_count, cur_count, folder_path):
    preview_buttons = driver.find_elements_by_xpath("//div[contains(@class,\"entry\")]/div[contains(@class,\"expando\")]")
    count = 0
    for button in preview_buttons:
        if max_count < 1:
            return count
        cached_html = button.get_attribute("data-cachedhtml")
        src = cached_html.split('a href=\"')[1].split('\"')[0]
        name = get_correct_name(src, cur_count)
        save_media(src, folder_path, name)
        # no error handling yet
        count += 1
        cur_count += 1
        max_count -= 1
    return count


def download_images_directly_from_expando_list(driver, subreddit, max_count, folder_path):
    prefix = "http://old.reddit.com/r/"
    full_url = prefix + subreddit
    driver.get(full_url)
    # missing pagination count management
    preview_buttons = driver.find_element_by_xpath("//div[@class='entry']/div[@class='expando']")
    count = 0
    for button in preview_buttons:
        if max_count < 1:
            return count
        cached_html = button.get_attribute("data-cachedhtml")
        src = cached_html.split('a href=\"')[1].split('\"')[0]
        name = get_correct_name(src, count)
        save_media(src, folder_path, name)
        # no error handling yet
        count += 1
        max_count -= 1
    return count


def next_page(driver):
    try:
        next_button = driver.find_element_by_xpath("//span[@class='next-button']/a")
        next_button.click()
    except NoSuchElementException:
        return -1


def download_top_media_in_subreddit(driver, subreddit, count, full_folder_path):
    prefix = "http://old.reddit.com/r/"
    suffix = "/top/?t=all"
    full_url = prefix + subreddit + suffix

    driver.get(full_url)

    cur_count = 1

    while count > 0:
        unblock_result = unblock(driver)
        print("unblock_result:" + str(unblock_result))
        # open_previews_result = open_previews(driver)
        # print("open_previews_result:" + str(open_previews_result))
        # downloaded_count = convert_and_save_from_previews(driver, count, full_folder_path)
        downloaded_count = download_images_in_page_directly_from_expando_list(driver, count, cur_count, full_folder_path)
        print("downloaded_count:" + str(downloaded_count))
        if downloaded_count == -1:
            return -1  # error while saving from previews
        count -= downloaded_count
        cur_count += downloaded_count

        next_page_result = next_page(driver)
        print("next_page_result:" + str(next_page_result))
        if next_page_result == -1:
            return -2  # no more pages
    return 0


def main():
    # usage: python redditDL.py subreddit_name max_media_download_count folder_name
    # folder needs to be within cwd
    args = sys.argv

    subreddit = args[1]
    max_count = int(args[2])

    folder_path = args[3]
    cwd = os.getcwd()
    full_folder_path = os.path.join(cwd, folder_path)
    if not os.path.isdir(full_folder_path):
        os.makedirs(full_folder_path)

    driver = webdriver.Firefox()
    download_result = download_top_media_in_subreddit(driver, subreddit, max_count, full_folder_path)
    # download_result = download_images_directly_from_expando_list(driver, subreddit, max_count, folder_path)

    if download_result < 0:
        driver.close()
        print("HUMAN EXE ERROR")
        return download_result
    driver.close()
    return 0


if __name__ == "__main__":
    main()