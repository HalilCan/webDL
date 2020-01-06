import os
import sys
import argparse
import time
import sys
import cv2
import os
import datetime

'note: the urllib save call is a separate instance'
now = datetime.datetime.now()


def get_dhash(image, hash_size=8):
    # resize the input image, adding a single column (width) so we
    # can compute the horizontal gradient
    resized = cv2.resize(image, (hash_size + 1, hash_size))

    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def are_aspect_ratios_similar(images, ratio_difference_limit=.05):
    # read image
    # img = cv2.imread('/home/img/python.png', cv2.IMREAD_UNCHANGED)
    # height, width, number of channels in image
    #    height = img.shape[0]
    #    width = img.shape[1]
    ratio_one = images[0].shape[0]/images[0].shape[1]
    ratio_two = images[1].shape[0]/images[1].shape[1]
    if abs(ratio_one - ratio_two) < ratio_difference_limit:
        return 1
    else:
        return 0


def are_identical(images, dhash_difference_limit=7):
    if not are_aspect_ratios_similar(images):
        return 0
    if abs(get_dhash(images[0]) - get_dhash(images[1])) < dhash_difference_limit:
        return 1
    else:
        return 0


def clear_duplicates_in_directory(directory_string):
    removed_count = 0
    comparison_count = 0
    extensions_list: ["", ".png", ".jpg", ".jpeg", ".bmp"]
    directory = os.fsencode(directory_string)
    cwd = os.getcwd()
    directory_abs = os.path.join(cwd, directory)
    print("directory: ", directory, "cwd: ", cwd, "directory_abs: ", directory_abs)
    for file in os.listdir(directory):
        filename = os.fsencode(file)
        fullfn_1 = os.path.join(directory_abs, filename)
        img_1 = cv2.imread(fullfn_1)
        if any(filename.endswith(extension) for extension in extensions_list):
            for file2 in os.listdir(directory):
                filename2 = os.fsencode(file2)
                comparison_count += 1
                if any(filename2.endswith(extension) for extension in extensions_list):
                    fullfn_2 = os.path.join(directory_abs, filename2)
                    img_2 = cv2.imread(fullfn_2)
                    if are_identical([img_1, img_2]):
                        os.remove(fullfn_2)
                        removed_count += 1
    return {"comparison_count": comparison_count, "removed_count": removed_count}


def main():
    # usage: python imgManips.py operation relative_directory
    # folder needs to be within cwd
    args = sys.argv
    operation = args[1]
    relative_directory = args[2]

    if operation == "clean":
        op_result = clear_duplicates_in_directory(relative_directory)
        return op_result

    return 0


if __name__ == "__main__":
    main()