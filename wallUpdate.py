import os
import sys
import datetime
import shutil
import subprocess

now = datetime.datetime.now()


def call_downloader(sources, count_per, sort_period):
    # for each sr, download appropriately
    # usage: python redditDL.py subreddit_name max_media_download_count sort_period
    local_python_path = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
    print(local_python_path)
    for subreddit in sources:
        print(sources)
        reddit_dl_params = [local_python_path, 'redditDL.py', subreddit, str(count_per), sort_period, "-f"]
        # reddit_dl_params = subreddit + " " + str(count_per) + " " + sort_period + " -f"
        return_code = subprocess.call(reddit_dl_params)
    return 0


def rearrange_folders(full_folder_path, full_wallpaper_folder_path, cwd, count_per):
    # flatten downloads into rel_folder_path
    # in current impl. they are already flat in /[count_per]
    full_temp_path = os.path.join(cwd, str(count_per))

    # make wallpaper folder... somehow.
    # just get the wallpaper folder path and add to it before deleting the temp folder
    for file in full_folder_path:
        try:
            shutil.copy(os.path.join(full_temp_path, file), os.path.join(full_folder_path, file))
            shutil.move(os.path.join(full_temp_path, file), os.path.join(full_wallpaper_folder_path, file))
        except:
            print(full_wallpaper_folder_path, full_temp_path, full_temp_path)
    try:
        os.removedirs(full_temp_path)
    except:
        print("cannot remove: ", full_temp_path)
    return 0

def main():
    # usage: wallUpdate.py abs_or_rel_wallpaper_folder_path count_per_sr time_period subreddit_list
    args = sys.argv
    wallpaper_folder_path = args[1]
    count_per = args[2]
    sort_period = args[3]
    subreddit_list = args[4:]

    dated_folder = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + \
        sort_period + "-" + "wallpapers" + "-" + str(count_per)
    cwd = os.getcwd()
    full_folder_path = os.path.join(cwd, dated_folder)
    if os.path.isabs(wallpaper_folder_path):
        full_wallpaper_folder_path = wallpaper_folder_path
    else:
        full_wallpaper_folder_path = os.path.join(cwd, wallpaper_folder_path)

    download_done = call_downloader(subreddit_list, count_per, sort_period)
    folders_rearranged = rearrange_folders(full_folder_path, full_wallpaper_folder_path, cwd, count_per)
    return folders_rearranged


if __name__ == "__main__":
    main()
