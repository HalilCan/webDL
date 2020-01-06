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


def are_aspect_ratios_similar(images, ratio_difference_limit=.005):
    # read image
    # img = cv2.imread('/home/img/python.png', cv2.IMREAD_UNCHANGED)
    # height, width, number of channels in image
    #    height = img.shape[0]
    #    width = img.shape[1]
    ratio_one = get_aspect_ratio(images[0])
    ratio_two = get_aspect_ratio(images[1])
    if abs(ratio_one - ratio_two) < ratio_difference_limit:
        return 1
    else:
        return 0


def get_aspect_ratio(image):
    return image.shape[0]/image.shape[1]


def are_identical(images, dhash_difference_limit=7):
    if not are_aspect_ratios_similar(images):
        return 0
    if abs(get_dhash(images[0]) - get_dhash(images[1])) < dhash_difference_limit:
        print("images are identical!")
        return 1
    else:
        return 0


def bag_image(fullfn, ratio, bag_of_holding, adjustment_scalar=1000):
    adjusted_ratio = int(ratio*adjustment_scalar) - int(ratio * adjustment_scalar) % 10
    if adjusted_ratio in bag_of_holding:
        bag_of_holding[adjusted_ratio].append(fullfn)
    else:
        bag_of_holding[adjusted_ratio] = [fullfn]
    return adjusted_ratio


def clear_duplicates_in_bag(fn_array):
    removed_count = 0
    comparison_count = 0
    extensions_list = ["", ".png", ".jpg", ".jpeg", ".bmp"]
    for file in fn_array:
        try:
            img_1 = cv2.imread(file)
            if any(file.endswith(extension) for extension in extensions_list):
                for file2 in fn_array:
                    if file == file2:
                        continue
                    comparison_count += 1
                    if any(file2.endswith(extension) for extension in extensions_list):
                        img_2 = cv2.imread(file2)
                        if are_identical([img_1, img_2]):
                            os.remove(file2)
                            removed_count += 1
                            print("REMOVED ", file2)
        except AttributeError:
            continue
    return {"comparison_count": comparison_count, "removed_count": removed_count}


def clear_duplicates(directory_string):
    # generate ratio dictionary
    # traverse within each "bag" in the dictionary
    removed_count = 0
    comparison_count = 0
    cwd = os.getcwd()
    directory_abs = os.path.join(cwd, directory_string)
    img_dict = {}
    for file in os.listdir(directory_string):
        fullfn_1 = os.path.join(directory_abs, file)
        image = cv2.imread(fullfn_1)
        ratio = get_aspect_ratio(image)
        bag_result = bag_image(fullfn_1, ratio, img_dict)
    for ratio, ratio_bag in img_dict.items():
        op_result = clear_duplicates_in_bag(ratio_bag)
        removed_count += op_result["removed_count"]
        comparison_count += op_result["comparison_count"]
    return {"comparison_count": comparison_count, "removed_count": removed_count}


def deprecated_clear_duplicates_in_directory(directory_string):
    removed_count = 0
    comparison_count = 0
    extensions_list = ["", ".png", ".jpg", ".jpeg", ".bmp"]
    cwd = os.getcwd()
    directory_abs = os.path.join(cwd, directory_string)
    print("directory: ", directory_string, "cwd: ", cwd, "directory_abs: ", directory_abs)
    for file in os.listdir(directory_string):
        try:
            fullfn_1 = os.path.join(directory_abs, file)
            img_1 = cv2.imread(fullfn_1)
            if any(file.endswith(extension) for extension in extensions_list):
                for file2 in os.listdir(directory_string):
                    if file == file2:
                        continue
                    comparison_count += 1
                    if any(file2.endswith(extension) for extension in extensions_list):
                        fullfn_2 = os.path.join(directory_abs, file2)
                        img_2 = cv2.imread(fullfn_2)
                        if are_identical([img_1, img_2]):
                            os.remove(fullfn_2)
                            removed_count += 1
                            print("REMOVED ", file2)
        except AttributeError:
            continue
    return {"comparison_count": comparison_count, "removed_count": removed_count}


def main():
    # usage: python imgManips.py operation relative_directory
    args = sys.argv
    operation = args[1]
    relative_directory = args[2]
    print(args)

    if operation == "cleanup":
        op_result = clear_duplicates(relative_directory)
        print(op_result)
        return op_result
    print("error")
    return 0


if __name__ == "__main__":
    main()