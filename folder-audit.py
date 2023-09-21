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

# TODO: Clean this file, move the viewer code to a different file

import sys
import os
import pathlib
import atexit

MAX_ITERATION = 0 # For debugging
AUTOPLAY_VIDEOS = False

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

def check_file_ext(file_ext):
    ALLOWED_EXTS = IMG_EXTS + VID_EXTS

    for ext in ALLOWED_EXTS:
        if (file_ext == ext):
            return True
        
    return False

def get_file_ext(file):
    return pathlib.Path(file).suffix

def get_viewer_filename_html(file_path):
    return '<span id="filename">{}</span>'.format(file_path)

def get_viewer_content_html(input):
    return '<span id="content">' + input + '</span>'

def get_viewer_media_img_html(file_path):
    return get_viewer_content_html('<img src="{}">'.format(file_path))

def get_viewer_media_vid_html(file_path):
    return_str = ""
    file_ext = get_file_ext(file_path)

    # Add 
    match file_ext:
        case "mp4" | "webm":
            return_str = '<video controls><source src="{}" type="video/{}"></video>'.format(file_path, file_ext)

        case "ogv":
            '<video controls><source src="{}" type="video/ogg"></video>'.format(file_path)
        
        # Old video formats not supported by HTML5
        case "mov" | "webm":
            '<b>This file cannot be displayed</b>'

        case _:
            raise Exception("Invalid file ext")
    
    

    return get_viewer_content_html(return_str)

################################################
# !! WARNING: Do not change these consts !!
################################################
VIEWER_DEFAULT_FILE_NAME = "Reisen.Udongein.Inaba.600.2396749.jpg"
VIEWER_DEFAULT_FOLDER = "file:///C:/Users/Gregory/Downloads/"
VIEWER_DEFAULT_FILE_NAME_HTML = get_viewer_filename_html(VIEWER_DEFAULT_FILE_NAME)
VIEWER_DEFAULT_MEDIA_HTML = get_viewer_media_img_html(VIEWER_DEFAULT_FILE_NAME)
################################################

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

last_file_name_html = ""
last_media_html = ""

def reset_viewer():
    viewer_read = open("viewer-iframe.html", "r")

    viewer_str = viewer_read.read()
    viewer_read.close()

    # Update the file name
    viewer_str_out = viewer_str.replace(last_file_name_html, VIEWER_DEFAULT_FILE_NAME_HTML)

    # Update the media
    viewer_str_out = viewer_str_out.replace(last_media_html, VIEWER_DEFAULT_MEDIA_HTML)

    # Write the updated HTML
    viewer_write = open("viewer-iframe.html", "w")
    viewer_write.write(viewer_str_out)
    viewer_write.close()



def main():

    #atexit.register(reset_viewer)

    DESTINATIONS = get_destinations()

    # Get a list of files in the dir
    FOLDER_PATH = sys.argv[1]
    file_list_unfiltered = os.listdir(FOLDER_PATH)

    file_list = []

    # Filter non-media files (only images and videos)
    i = 0
    
    for file_name in file_list_unfiltered:
        file_ext = get_file_ext(file_name)[1:]

        print(file_ext, end=" - ")
        print(check_file_ext(file_ext))
        
        if check_file_ext(file_ext):
            file_list.append(FOLDER_PATH + file_name)

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
    #os.system("viewer.html")


    
    i = 0

    print(file_list)
    return 

    if len(file_list) > 0:
        for file_name in file_list:

            print("test")
            file_path = FOLDER_PATH + file_name

            # Update the viewer file
            ################################
            viewer_read = open("viewer.html", "r")

            viewer_str = viewer_read.read()
            viewer_read.close()

            # Update the file name
            viewer_str_out = viewer_str.replace(VIEWER_DEFAULT_FILE_NAME_HTML, get_viewer_filename_html(file_name))

            # Check the file ext
            file_ext = get_file_ext(file_path)
            media_html = ""

            if file_ext in IMG_EXTS:
                media_html = get_viewer_media_img_html(file_path)

            elif file_ext in VID_EXTS:
                media_html = get_viewer_media_vid_html(file_path)

            viewer_str_out = viewer_str_out.replace(VIEWER_DEFAULT_FILE_NAME_HTML, media_html)



            # Write the updated HTML
            viewer_write = open("..\\out\\index.html", "w")
            viewer_write.write(viewer_str_out)
            viewer_write.close()

            clear_screen()
            print(file_name)

            folder_index = 0
            for folder in DESTINATIONS:
                print("{} - Move to {}", folder_index + 1, folder)

            print("0 - Skip")
            print("000 - Delete")

            # Update the last media html (used in the reset)
            last_file_name_html = file_name
            last_media_html = media_html
            i += 0

            if i > MAX_ITERATION and MAX_ITERATION > 0:
                break
        # Reset the viewer file
        ################################
        reset_viewer()
    

if __name__ == '__main__':
    main()