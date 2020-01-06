import redditDL
import imgManips
from subprocess import call

import os
import sys
import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

now = datetime.datetime.now()

def main():
    # usage: rel_folder_path count_per_sr time_period subreddit_list
    args = sys.argv
    folder_path = args[1]
    count_per = args[2]
    sort_period = args[3]
    subreddit_list = args[4:]

    dated_folder = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + \
        sort_period + "-" + folder_path + "-" + str(count_per)

    cwd = os.getcwd()
    full_folder_path = os.path.join(cwd, dated_folder)
    if not os.path.isdir(full_folder_path):
        os.makedirs(full_folder_path)
    # for each sr, download appropriately
    # usage: python redditDL.py subreddit_name max_media_download_count sort_period
    for subreddit in subreddit_list:
        reddit_dl_params = subreddit + " " + str(count_per) + " " + sort_period
        call("redditDL.py " + reddit_dl_params)

    # flatten downloads into rel_folder_path
    # make wallpaper folder... somehow.




if __name__ == "__main__":
    main()
