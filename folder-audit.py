'''
(c) 2023 Gregory Karastergios

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
'''

import sys
import os
import json
import shlex
import subprocess

MAX_ITERATION = 5 # For debugging

IMG_EXTS = [
    "png",
    "jpeg",
    "jpg",
    "gif",
    "bmp",
    "webp",
]

VID_EXTS = [
    "webp",
    "mp4",
    "webm",
    "mov",
    "wmv",
    "ogv"
]

def clear_screen():
        print("\033[H\033[J")

def escape_slashes(input):
    return input.replace("\"", "\\\"")

def get_files_in_dir_toplevel(dir):
    
    list = []
    for f in os.listdir(dir):
        if (os.isfile(f)):
            list.append(f)


    return list

def check_file_ext(file_ext):
    ALLOWED_EXTS = IMG_EXTS + VID_EXTS

    for ext in ALLOWED_EXTS:
        if (file_ext == ext):
            return True
        
    return False

def main():

    # Get a list of files in the dir
    FOLDER_PATH = sys.argv[1]
    file_list_unfiltered = os.listdir(FOLDER_PATH)

    file_list = []

    # Filter non-media files (only images and videos)
    i = 0
    
    for file in file_list_unfiltered:
        file_ext = os.path.splitext(file)

        if check_file_ext(file_ext):
            file_list.append(FOLDER_PATH + file)

        i += 1

        if i > MAX_ITERATION and MAX_ITERATION > 0:
            break

    os.system("viewer.html")

    '''
    OPTIONS:
        move to dir 1
        move to dir 2
        move to dir 3
        
        delete
        
        skip

        whitelist (add later)
    '''
    for file in file_list:
        print(file)

    # Open the viewer (right now it's just an HTML file lmao)

if __name__ == '__main__':
    main()