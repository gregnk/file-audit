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

def get_destinations():
    f = open("destinations.txt", "r")

    return_var = f.readlines()
    f.close()

    return return_var

def check_file_ext(file_ext):
    ALLOWED_EXTS = IMG_EXTS + VID_EXTS

    for ext in ALLOWED_EXTS:
        if (file_ext == ext):
            return True
        
    return False

def get_file_ext(file):
    return os.path.splitext(file)

def main():

    DESTINATIONS = get_destinations()

    # Get a list of files in the dir
    FOLDER_PATH = sys.argv[1]
    file_list_unfiltered = os.listdir(FOLDER_PATH)

    file_list = []

    # Filter non-media files (only images and videos)
    i = 0
    
    for file in file_list_unfiltered:
        file_ext = get_file_ext(file)

        if check_file_ext(file_ext):
            file_list.append(FOLDER_PATH + file)

        i += 1

        if i > MAX_ITERATION and MAX_ITERATION > 0:
            break

    '''
    OPTIONS:
        move to dir 1
        move to dir 2
        move to dir 3
        
        delete
        
        skip

        whitelist (add later)
    '''

    # Open the viewer (right now it's just an HTML file lmao)
    os.system("viewer.html")

    for file in file_list:
        CURRENT_FILE_PATH = FOLDER_PATH + file
        clear_screen()
        print(file)

        folder_index = 0
        for folder in DESTINATIONS:
            print("{} - Move to {}", folder_index + 1, folder)

        print("0 - Skip")
        print("000 - Delete")

        # Update the viewer file
        viewer_read = open("viewer.html", "r")

        viewer_str = viewer_read.read()
        viewer_read.close()

        # Check the file ext
        viewer_str_out = viewer_str.replace(r'<span id="filename">.*</span>', '<span id="filename">' + CURRENT_FILE_PATH + '</script>')
        viewer_str_out = viewer_str_out.replace('<div id="content">', '<script src=' + file_name + '.js></script>')

if __name__ == '__main__':
    main()