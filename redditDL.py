import os
import sys
import datetime
import urllib.request
from urllib.error import URLError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException\

'note: the urllib save call is a separate instance'
now = datetime.datetime.now()

class SubredditDownloader:
    def __init__(self, driver, subreddit, limit, sort_period):
        self.prefix = "https://old.reddit.com/r/"
        self.top_url = "/top/?t="
        self.subreddit = subreddit
        self.limit = limit
        self.sort_period = sort_period
        self.driver = driver

    def get_sort_url(self):
        return self.prefix + self.subreddit + self.top_url + self.sort_period

    def get_dated_folder_name(self):
        cwd = os.getcwd()
        rel_path = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + self.sort_period + "-" + self.subreddit + "-" + str(self.limit)
        full_folder_path = os.path.join(cwd, rel_path)
        if not os.path.isdir(full_folder_path):
            os.makedirs(full_folder_path)
        return rel_path

    def unblock(self):
        if "reddit.com: over 18?" in self.driver.title:
            yes_button = self.driver.find_elements_by_xpath("//div[@class='buttons']/button")[1]
            yes_button.click()
            return 0
        else:
            return 1

    def save_media(self, media_url, folder_path, name):
        save_path = os.path.join(folder_path, name)
        try:
            urllib.request.urlretrieve(media_url, save_path)
        except URLError:
            print("urlOpen error for " + media_url)
        return 0

    def next_page(self):
        try:
            next_button = self.driver.find_element_by_xpath("//span[@class='next-button']/a")
            next_button.click()
            return 0
        except NoSuchElementException:
            return -1

    def get_things_in_page(self):
        things_path = "//div[contains(@class,\"sitetable\")]/div[contains(@class,\"thing\")]"
        try:
            things_list = self.driver.find_elements_by_xpath(things_path)
            print(len(things_list))
            return things_list
        except NoSuchElementException:
            return -1

    def save_media_in_page(self, max_count, cur_count, folder_path):
        things = self.get_things_in_page()
        count = 0
        print(len(things))
        for thingObj in things:
            if max_count < 1:
                return count
            thing = Thing(self.driver, thingObj, "")
            src = thing.get_data_url()
            print(src)

            name = thing.get_savefile_name(str(count), "")
            if name == -1:
                continue

            self.save_media(src, folder_path, name)
            # no error handling yet
            count += 1
            cur_count += 1
            max_count -= 1
        return count

    def download(self):
        full_url = self.get_sort_url()
        driver = self.driver
        count = self.limit
        folder_name = self.get_dated_folder_name()

        driver.get(full_url)
        cur_count = 1

        while count > 0:
            unblock_result = self.unblock()
            print("unblock_result:" + str(unblock_result))
            downloaded_count = self.save_media_in_page(count, cur_count, folder_name)
            print("downloaded_count:" + str(downloaded_count))
            if downloaded_count == -1:
                return -1  # error while saving from previews
            count -= downloaded_count
            cur_count += downloaded_count

            next_page_result = self.next_page()
            print("next_page_result:" + str(next_page_result))
            if next_page_result == -1:
                return -2  # no more pages
        return 0


class Thing:
    def get_thing_details(self):
        thing = self.dom
        is_link = 0
        site = ""
        title = "error: no title found"
        data_url = ""

        if "link" in thing.get_attribute("class"):
            src = thing.get_attribute("data-url")
            if src is None:
                print("no data-url found in link Thing")
                src = ""
            is_link = 1
        else:
            src = ""

        reddit_link_signatures = ["redd.it", "reddit.c"]
        if any(signature in src for signature in reddit_link_signatures):
            site = "reddit"
        imgur_link_signatures = ["imgur.c"]
        if any(signature in src for signature in imgur_link_signatures):
            site = "imgur"

        permalink_name = thing.get_attribute("data-permalink").rstrip("/").split("/")[-1]

        data_url = thing.get_attribute("data-url")

        return {"is_link": is_link, "site": site, "src": src, "permalink_name": permalink_name,
                "data_url": data_url, "title": title}

    def __init__(self, driver, dom_object, prefix):
        self.driver = driver
        self.dom = dom_object
        self.prefix = prefix

        init_details = self.get_thing_details()
        self.src = init_details["src"]
        self.site = init_details["site"]
        self.is_link = init_details["is_link"]
        self.data_url = init_details["data_url"]
        # TODO: handle text title
        self.title = init_details["title"]
        self.permalink_name = init_details["permalink_name"]

    def get_printable_name(self, prefix, suffix):
        if len(self.permalink_name) > 75:
            return str(prefix) + '-' + self.permalink_name[:75] + str(suffix)
        else:
            return str(prefix) + '-' + self.permalink_name + str(suffix)

    def get_savefile_name(self, prefix, suffix):
        extension = self.data_url.split(".")[-1]
        if len(extension) > 3:
            print("extension error! \n extension: " + extension + "\n src: " + self.data_url)
            extension = ""
            return -1
        name = self.get_printable_name(prefix, suffix) + "." + extension
        return name

    def is_link_thing(self):
        return self.is_link
    
    def get_site(self):
        return self.site

    def get_reddit_page(self):
        prefix = self.prefix
        address = prefix + self.dom.get_attribute("data-permalink")
        return address

    def get_data_url(self):
        return self.data_url


def clear_preview_url(url):
    url = url.replace("preview", "i")
    url = url.split("?")[0]
    return url


def open_previews(driver):
    preview_buttons = driver.find_elements_by_class_name("expando")
    for button in preview_buttons:
        button.click()
    return 0
# thumbnails = driver.find_elements_by_xpath("//div[contains(@sitetable,\"entry\")]
#   /div[contains(@class,\"thing\")]/a[contains(@class,\"thumbnail\")]")
# preview_buttons = driver.find_element_by_xpath("//div[@class='entry']/div[@class='expando']")


def main():
    # usage: python redditDL.py subreddit_name max_media_download_count
    # folder needs to be within cwd
    args = sys.argv

    subreddit = args[1]
    max_count = int(args[2])
    sort_period = args[3]

    folder_path = args[1] + args[2]
    cwd = os.getcwd()
    full_folder_path = os.path.join(cwd, folder_path)
    if not os.path.isdir(full_folder_path):
        os.makedirs(full_folder_path)

    driver = webdriver.Firefox()
    download_daemon = SubredditDownloader(driver, subreddit, max_count, sort_period)
    download_result = download_daemon.download()

    if download_result < 0:
        driver.close()
        print("HUMAN EXE ERROR")
        return download_result

    driver.close()
    return 0


if __name__ == "__main__":
    main()