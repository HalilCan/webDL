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


class PageDownloader:
    def __init__(self, driver, url, save_format):
        self.url = url
        self.domain = self.get_domain()
        self.format = save_format
        self.driver = driver
        self.is_flat = 0

    def get_domain(self):
        url = self.url
        split_url = url.split(".")
        domain = "."
        while len(split_url) > 0:
            if "/" in (split_url[0]):
                split_url.pop(0)
        domain = domain.join(split_url)
        return domain

    def get_sort_url2(self):
        return self.prefix + self.subreddit + self.top_url + self.sort_period

    def get_dated_folder_name(self):
        cwd = os.getcwd()
        rel_path = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + self.domain
        full_folder_path = os.path.join(cwd, rel_path)

        if not os.path.isdir(full_folder_path):
            os.makedirs(full_folder_path)
        return rel_path

    def unblock(self):
        if "reddit.com: over 18?" in self.driver.title or "quarantined" in self.driver.title:
            print(self.driver.title)
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

    def get_things_in_page(self):
        things_path = "//div[contains(@class,\"sitetable\")]/div[contains(@class,\"thing\")]"
        try:
            things_list = self.driver.find_elements_by_xpath(things_path)
            return things_list
        except NoSuchElementException:
            return -1

    def save_self_post(self, thing, folder_path, rank_prefix):
        content = thing.get_self_post_content_and_comments()
        title = content['title']
        post_content = content['post']
        comments = content['comments']

        post_object = TextPost(title, post_content, comments, rank_prefix)
        cwd = os.getcwd()
        full_folder_path = os.path.join(cwd, folder_path)
        print(full_folder_path)
        save_result = post_object.save(full_folder_path)
        return save_result

    def save_media_in_page(self, max_count, cur_count, folder_path):
        things = self.get_things_in_page()
        count = 0
        for thingObj in things:
            if max_count < 1:
                return count
            thing = Thing(self.driver, thingObj, self.self_post_prefix)
            if thing.is_link:
                src = thing.get_data_url()
                if not src:
                    continue
                if isinstance(src, int):
                    continue
                print(src)
                name = thing.get_savefile_name(str(cur_count) + "-" + self.subreddit, "")
                if name == -1:
                    continue
                self.save_media(src, folder_path, name)
            else:
                self.save_self_post(thing, folder_path, str(cur_count))
            count += 1
            cur_count += 1
            max_count -= 1
        return count

    def download(self):
        full_url = self.get_sort_url()
        driver = self.driver
        count = self.limit
        folder_name = self.get_dated_folder_name()
        try:
            self.driver.get(full_url)
        except TimeoutException:
            self.driver.execute_script("window.stop()")
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
        site = ""
        title = "error: no title found"

        if "self" not in thing.get_attribute("class"):
            is_link = 1
        else:
            is_link = 0

        src = thing.get_attribute("data-url")
        if src is None:
            print("no data-url found in link Thing")
            src = ""
        author = thing.get_attribute("data-author")
        vote_count = thing.get_attribute("data-score")
        comment_count = thing.get_attribute("data-comments-count")
        subreddit = thing.get_attribute("data-subreddit")

        reddit_link_signatures = ["redd.it", "reddit.c"]
        imgur_link_signatures = ["imgur.c"]
        if any(signature in src for signature in reddit_link_signatures):
            site = "reddit"
        elif any(signature in src for signature in imgur_link_signatures):
            site = "imgur"
        elif "gfycat" in thing.get_attribute("data-domain"):
            site = "gfycat"
        elif "artstation." in thing.get_attribute("data-url"):
            site = "artstation"
            src = thing.get_attribute("data-url").split("?")[0]
        else:
            site = "other"
            src = thing.get_attribute("data-url")

        permalink_name = thing.get_attribute("data-permalink").rstrip("/").split("/")[-1]

        data_url = src

        return {"is_link": is_link, "site": site, "src": src, "permalink_name": permalink_name,
                "data_url": data_url, "title": title, "author": author, "subreddit": subreddit,
                "vote_count": vote_count, "comment_count": comment_count, }

    def __init__(self, driver, dom_object, prefix):
        self.driver = driver
        self.dom = dom_object
        self.prefix = prefix

        init_details = self.get_thing_details()
        self.src = init_details["src"]
        self.site = init_details["site"]
        self.is_link = init_details["is_link"]
        self.data_url = init_details["data_url"]
        self.author = init_details["author"]
        self.vote_count = init_details["vote_count"]
        self.comment_count = init_details["comment_count"]
        self.subreddit = init_details["subreddit"]
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
            src = self.get_data_url()
            if isinstance(src, int):
                return -1
            print(src)
            return src.split(".")[-1]
        else:
            return self.custom_extension

    def get_savefile_name(self, prefix, suffix):
        extension = self.get_data_extension()
        if isinstance(extension, int):
            return -1
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


class TextPost:
    def __init__(self, title, post_content, comments, rank_prefix):
        self.title = title
        self.post_content = post_content
        self.comments = comments
        self.rank_prefix = rank_prefix

    def save(self, path_to_folder):
        abs_path = os.path.join(path_to_folder, self.rank_prefix + "-" + self.title[:100] + ".html")
        html_doc = open(abs_path, 'w', encoding='utf-8')
        print(abs_path)

        html_header = "<html>"
        header = "<head><title>" + self.title + "</title></head>"
        body = "<body><div class = 'content'>" + self.post_content + "</div>" + \
               "<div class = 'comment-table'>" + self.comments + "</div></body>"
        html_footer = "</html>"
        html_content = html_header + header + body + html_footer

        print(header)

        print(html_doc.write(html_content))
        html_doc.close()

        return 0


# thumbnails = driver.find_elements_by_xpath("//div[contains(@sitetable,\"entry\")]
#   /div[contains(@class,\"thing\")]/a[contains(@class,\"thumbnail\")]")
# preview_buttons = driver.find_element_by_xpath("//div[@class='entry']/div[@class='expando']")


def main():
    # usage: python pageDL.py url save_format
    # folder needs to be within cwd
    args = sys.argv
    print(args)

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
    #chrome_options.add_argument("--headless")
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

    yield browser

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