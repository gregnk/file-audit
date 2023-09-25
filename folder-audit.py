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
import signal
import re
import shutil
from send2trash import send2trash


MAX_ITERATION = 0       # For debugging
AUTOPLAY_VIDEOS = False # Doesn't actually do anything yet

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

def convert_backslashes(input):
    return input.replace("\\", "/")

def check_file_ext(file_ext):
    ALLOWED_EXTS = IMG_EXTS + VID_EXTS

    for ext in ALLOWED_EXTS:
        if (file_ext == ext):
            return True
        
    return False

def get_file_ext(file):
    return (pathlib.Path(file).suffix)[1:]

def get_viewer_filename_html(file_path):
    return '<span id="filename">{}</span>'.format(file_path)

def get_viewer_content_html(input):
    return '<div id="content">' + input + '</div>'

def get_viewer_media_img_html(file_path):
    return get_viewer_content_html('<img src="file:///{}">'.format(file_path))

def get_viewer_media_vid_html(file_path):
    return_str = ""
    file_ext = get_file_ext(file_path)

    print(file_ext)
    # Add 
    match file_ext:
        case "mp4" | "webm":
            return_str = '<video controls><source src="file:///{}" type="video/{}"></video>'.format(file_path, file_ext)

        case "ogv":
            return_str = '<video controls><source src="file:///{}" type="video/ogg"></video>'.format(file_path)
        
        # Old video formats not supported by HTML5
        case "mov" | "webm":
            return_str = '<b>This file cannot be displayed</b>'

        case _:
            raise Exception("Invalid file ext")
    
    

    return get_viewer_content_html(return_str)

################################################
# !! WARNING: Do not change these vars !!
################################################
VIEWER_DEFAULT_FILE_NAME = "Reisen.Udongein.Inaba.600.2396749.jpg"
VIEWER_DEFAULT_FILE_NAME_HTML = get_viewer_filename_html(VIEWER_DEFAULT_FILE_NAME)
VIEWER_DEFAULT_MEDIA_HTML = get_viewer_content_html('<img src="{}">'.format(VIEWER_DEFAULT_FILE_NAME))
VIEWER_DEFAULT_INDEX_HTML = "#/#"
VIEWER_DEFAULT_NOTICE = "*** DEFAULT PAGE ***"
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

    destinations_file_name = ""

    if (len(sys.argv) >= 3):
        destinations_file_name = sys.argv[2]

    else:
        destinations_file_name = "destinations.txt"

    f = open(destinations_file_name, "r")

    return_var = f.readlines()
    f.close()

    i = 0
    for str in return_var:
        if (str[-1:] == "\n"):
            return_var[i] = str[:-1]

        i += 1
    return return_var

def get_exemptions():

    EXEMPTIONS_FILE_NAME = "exemptions.txt"

    if (os.path.isfile(EXEMPTIONS_FILE_NAME) == False):
        with open(EXEMPTIONS_FILE_NAME, 'w') as f:
            f.write('')
            f.close()

    f = open(EXEMPTIONS_FILE_NAME, "r", encoding='utf-8', errors='ignore')

    return_var = f.readlines()
    f.close()

    i = 0
    for str in return_var:
        if (str[-1:] == "\n"):
            return_var[i] = str[:-1]

        i += 1
    return return_var

def reset_viewer():
    viewer_read = open("viewer-iframe.html", "r")

    viewer_str = viewer_read.read()
    viewer_read.close()

    # Reset the file name
    viewer_str_out = re.sub(get_viewer_filename_html(".*"), VIEWER_DEFAULT_FILE_NAME_HTML, viewer_str)

    # Reset the media
    viewer_str_out = re.sub('<div id="content">.*</div>', VIEWER_DEFAULT_MEDIA_HTML, viewer_str_out)

    # Reset the counter
    viewer_str_out = re.sub('<span id="index">.*</span> &ndash;', '<span id="index">' + VIEWER_DEFAULT_INDEX_HTML + '</span> &ndash;', viewer_str_out)

    # Re-add the default notice
    viewer_str_out = re.sub('<div id="default"></div>', '<div id="default">{}</div>'.format(VIEWER_DEFAULT_NOTICE), viewer_str_out)
    
    # Write the updated HTML
    viewer_write = open("viewer-iframe.html", "w")
    viewer_write.write(viewer_str_out)
    viewer_write.close()

def kb_interrupt_handler(signum, frame):

    # Since Ctrl-C sends 2 args
    reset_viewer()

def main():

    last_file_name_html = VIEWER_DEFAULT_FILE_NAME_HTML
    last_media_html = VIEWER_DEFAULT_MEDIA_HTML

    # Reset the file upon exit
    atexit.register(reset_viewer)
    signal.signal(signal.SIGINT, kb_interrupt_handler)

    DESTINATIONS = get_destinations()

    # Get a list of files in the dir
    FOLDER_PATH = sys.argv[1]
    file_list_unfiltered = os.listdir(FOLDER_PATH)

    file_list = []

    # Filter non-media files (only images and videos)
    i = 0
    
    for file_path in file_list_unfiltered:
        file_ext = get_file_ext(file_path)

        print(file_ext, end=" - ")
        print(check_file_ext(file_ext))
        
        if check_file_ext(file_ext):
            file_list.append(FOLDER_PATH + file_path)

        i += 1

        if i > MAX_ITERATION and MAX_ITERATION > 0:
            break

    # Open the viewer (right now it's just an HTML file lmao)
    #os.system("viewer.html")
    i = 0
    file_list_len = len(file_list) - len(get_exemptions())
    #print(file_list)

    if len(file_list) > 0:

        input_msg = "Ready"
        for file_path in file_list:
            
            # Skip exempt files
            if file_path in get_exemptions():
                continue

            file_name = os.path.basename(file_path)

            # Update the viewer file
            ################################
            viewer_read = open("viewer-iframe.html", "r")

            viewer_str = viewer_read.read()
            viewer_read.close()

            # Update the file name
            file_name_html = get_viewer_filename_html(file_name)
            viewer_str_out = viewer_str.replace(last_file_name_html, file_name_html)


            # Check the file ext
            file_path_converted = convert_backslashes(file_path)
            file_ext = get_file_ext(file_path_converted)
            media_html = ""

            if file_ext in IMG_EXTS:
                media_html = get_viewer_media_img_html(file_path_converted)

            elif file_ext in VID_EXTS:
                media_html = get_viewer_media_vid_html(file_path_converted)

            viewer_str_out = viewer_str_out.replace(last_media_html, media_html)

            viewer_str_out = re.sub('<span id="index">.*</span> &ndash;', '<span id="index">{}/{}</span> &ndash;'.format(i, file_list_len), viewer_str_out)

            viewer_str_out = viewer_str_out.replace(VIEWER_DEFAULT_NOTICE, "")

            # Write the updated HTML
            viewer_write = open("viewer-iframe.html", "w")
            viewer_write.write(viewer_str_out.encode('ascii', 'xmlcharrefreplace').decode()) # Escape unicode chars
            viewer_write.close()

            valid_input = False
            while valid_input == False:
                clear_screen()
                print(input_msg)
                print("=========================================")
                print(file_name + "\n")

                folder_index = 0
                for folder in DESTINATIONS:
                    print("{} \t- Move to {}".format(folder_index + 1, folder))
                    folder_index += 1

                print("")
                print("0 \t- Keep")
                print("00 \t- Defer")
                print("9000 \t- Delete")

                print("> ", end='')
                user_input_str = input()

                user_input = 0

                # Check if the input is an int
                try:
                    user_input = int(user_input_str)

                except:
                    input_msg = "Invalid entry"
                    continue

                # print(type(user_input))
                # print(user_input == 0)
                #print(user_input > 0 and user_input < len(DESTINATIONS))


                # Move
                if (user_input > 0 and user_input < len(DESTINATIONS) + 1):
                    # print("Move")
                    shutil.move(file_path, DESTINATIONS[user_input - 1])
                    valid_input = True
                    input_msg = "File moved to {}".format(DESTINATIONS[user_input - 1])

                # Keep
                elif (user_input_str == "0"):
                    # print("Skip")
                    valid_input = True
                    input_msg = "File exempted"

                    with open('exemptions.txt', 'a', encoding="utf-8") as file:
                        file_path += "\n"
                        file.write(file_path)

                # Defer
                elif (user_input_str == "00"):
                    # print("Skip")
                    valid_input = True
                    input_msg = "File skipped"

                # Delete
                elif (user_input_str == "9000"):
                    # print("Del")
                    valid_input = True                    
                    input_msg = "File deleted"
                    send2trash(file_path)

                # Invalid input
                else:
                    # print("Err")
                    input_msg = "Invalid entry"
                    valid_input = False
                
                
                # input()


            # Update the last media html
            last_file_name_html = file_name_html.encode('ascii', 'xmlcharrefreplace').decode()
            last_media_html = media_html
            i += 1

            if i > MAX_ITERATION and MAX_ITERATION > 0:
                break

        # Reset the viewer file
        ################################
        reset_viewer()
    

if __name__ == '__main__':
    main()