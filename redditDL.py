import os
import sys
import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

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
        name = name
        save_path = os.path.join(folder_path, name)
        if os.path.isfile(save_path):
            print("file exists: ", save_path)
            return 1
        else:
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
            return things_list
        except NoSuchElementException:
            return -1

    def save_media_in_page(self, max_count, cur_count, folder_path):
        things = self.get_things_in_page()
        count = 0
        for thingObj in things:
            if max_count < 1:
                return count
            thing = Thing(self.driver, thingObj, "")
            src = thing.get_data_url()
            print(src)

            name = thing.get_savefile_name(str(cur_count), "")
            if name == -1:
                continue
            custom_extension = ""

            self.save_media(src, folder_path, name)
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
        if "gfycat" in thing.get_attribute("data-domain"):
            site = "gfycat"

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
        self.custom_extension = ""

    def get_printable_name(self, prefix, suffix):
        if len(self.permalink_name) > 75:
            return str(prefix) + '-' + self.permalink_name[:75] + str(suffix)
        else:
            return str(prefix) + '-' + self.permalink_name + str(suffix)

    def get_data_extension(self):
        if self.custom_extension == "":
            return self.get_data_url().split(".")[-1]
        else:
            return self.custom_extension

    def get_savefile_name(self, prefix, suffix):
        extension = self.get_data_extension()
        if len(extension) > 4:
            print("extension error! \n extension: " + extension + "\n src: " + self.data_url)
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
        if self.site == "reddit":
            if len(self.data_url.split(".")[-1]) > 4:
                if "v.red" in self.data_url:
                    self.custom_extension = "mp4"
                    reddit_dash_suffixes = ["1080", "720", "480", "360", "240", "192", "95"]
                    # open new window and switch to it using js
                    self.driver.execute_script("window.open()")
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    # load new window by trying DASH reddit DASH suffixes
                    success = 0
                    trial_link = ""
                    for suffix in reddit_dash_suffixes:
                        trial_link = self.data_url + "/DASH_" + suffix
                        if not is_v_reddit_error_page(trial_link):
                            success = 1
                            break
                    if success == 0:
                        print("reddit DASH blob url resolve error")
                        return -3
                    # close window using js
                    self.driver.execute_script("window.close()")
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    # return the found source
                    return trial_link
                else:
                    print("reddit data url resolve error")
                    return -2
            return self.data_url
        if self.site == "imgur":
            if self.data_url.split(".")[-1] == "gifv":
                self.data_url = self.data_url[:-4] + "mp4"
            return self.data_url
        if self.site == "gfycat":
            # open new window and switch to it using js
            self.driver.execute_script("window.open()")
            self.driver.switch_to.window(self.driver.window_handles[1])
            # load new window with the gfycat link
            self.driver.get(self.data_url)
            # source_elem = //video[class includes video and media]/source[type is "video/mp4" src includes fat.gfycat]
            source_elem_path = "//video[contains(@class,\"video\") and contains(@class,\"media\")]" \
                               "/source[contains(@type,\"video/mp4\")]"
            sources = self.driver.find_elements_by_xpath(source_elem_path)
            # return src of source_elem (maybe array into singleton into attribute)
            src = ""
            for source in sources:
                if "thumbs.g" not in source.get_attribute("src"):
                    src = source.get_attribute("src")
            # close window using js
            self.driver.execute_script("window.close()")
            self.driver.switch_to.window(self.driver.window_handles[0])
            # return the found source
            return src


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


def is_v_reddit_error_page(url):
    try:
        response = urllib.request.urlopen(url)
        if response.status == 403:
            return 1
        else:
            return 0
    except HTTPError:
        return 1


if __name__ == "__main__":
    main()