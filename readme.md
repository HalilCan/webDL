# WebDL
## 1. What
WebDL is a project aiming to make periodical collection and consumption of online media easy. It is not meant to be a replacement for technologies such as RSS, but rather an end-to-end framework using whatever is appropriate to extract and deliver what matters to the user.
### 1.a. Current State
There are three Python scripts in the project: 
- `redditDL` downloads linked media or content of `self` posts from a specific subreddit using `Selenium` and `urllib`. Content is sorted by vote rank in a user-specified time period.
- `imgManips` can detect and delete duplicate images in a directory using downscaled difference hashing.
- `wallUpdate` creates or updates a wallpaper folder using multiple web sources (currently subreddits). It uses `redditDL` functionality.
### 1.b. Goals
- `redditDL` is a good working prototype to quickly collect data for consumption or archival storage, albeit from a single website. I would like to generalize its approach so that more sources (and website structures) are easily supported.
- Like `wallUpdate`, there are other tasks related to structured data collection that I'd like to automate. Other singleton scripts or a generalized `Task` approach are possible avenues to follow. 
- Text media should also have smart* text-to-speech functionality to further increase accessibility while screen access is limited. *Smart as in: Read only what matters without me having to tell you.
  
---

## 2. Why
`Fully automated luxury space organized ranked media consumption, baby!`

In boring terms, I want to reduce search and discovery costs for appropriate periodical tasks. These include aggregating ranking news and research articles (by date or topic), collecting wallpapers, figuring out what matters in a given article (a search cost within the object), etc.

---

## 3. How
### 3.a. Requirements
- General:
  - Python 3.8
  - Pip
- redditDL:
  - Selenium - Needed for the headless browser webscraping. Run `pip install selenium` in the redditDL.py directory or install it globally using the `-U` flag.
  - Some webdriver, e.g. [Firefox webdriver](https://github.com/mozilla/geckodriver/releases) - Place in virtual environment directory
- wallUpdate:
  - shutil - install with `pip`
  - subprocess - install with `pip` 
- imgManips
  - opencv - cv2 install with `pip` with its dependencies
### 3.b. Usage
- redditDL: `python_path redditDL.py subreddit_name max_media_download_count sort_period OPTIONAL_flags`
  - flags: 
    - `-f` for flat folder structure when using multiple download sources 

- wallUpdate: `python_path wallUpdate.py abs_or_rel_wallpaper_folder_path count_per_sr time_period subreddit_list`

- imgManips: `python_path imgManips.py operation relative_directory`
  - operations:
    - `cleanup` for deleting duplicate images
- **Automation**:
    For scheduled usage like periodically updating a wallpaper folder with online images, you can automate the scripts by with the same commands using `cron` (UNIX) or the `Task Scheduler` (Windows).
