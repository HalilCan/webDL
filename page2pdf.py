import os
import sys
import datetime
import pdfkit

now = datetime.datetime.now()


def main():
    print("BY GAWD")
    print(sys.argv)
    print(now)
    # usage: python pageDL.py url save_format
    # folder needs to be within cwd
    args = sys.argv

    url = args[1]
    save_format = args[2]

    pdfkit.from_url(url, 'trp1.pdf')
    # NOTE: wkhtohtml or whatever that pdfkit calls has been modified with the correct executable path
    print(now)


if __name__ == '__main__':
    main()