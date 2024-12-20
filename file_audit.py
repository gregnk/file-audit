'''
(c) 2023-2024 Gregory Karastergios

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
import traceback
from secure_delete import secure_delete
from selenium import webdriver
import pygetwindow as gw
import ctypes
from screeninfo import get_monitors

VIEWER_HTML_FILE = "viewer.html"
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

def get_destinations_file_path():
    if (len(sys.argv) >= 3):
        return sys.argv[2]
    
    return "destinations.txt"

DESTINATIONS_FILE_PATH = get_destinations_file_path()

def get_destinations():

    f = open(DESTINATIONS_FILE_PATH, "r")

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
    viewer_read = open(VIEWER_HTML_FILE, "r")

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
    viewer_write = open(VIEWER_HTML_FILE, "w")
    viewer_write.write(viewer_str_out)
    viewer_write.close()

def kb_interrupt_handler(signum, frame):

    # Since Ctrl-C sends 2 args
    print("\n\nQuitting...")
    reset_viewer()

def get_os_dir_slash():
        if os.name == 'nt':
            return "\\"
            
        elif os.name == 'posix':
            return "/"
            
        elif os.name == 'java':
            return "/"
            
        else:
            raise Exception("Unsupported OS")
        
def main():
    # Update the window title
    WINDOW_TITLE = "file-audit"
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(WINDOW_TITLE)
        except:
            dummy = 0
    if os.name == 'posix':
        try:
            print("\x1b]2;{}\x07".format(WINDOW_TITLE))
        except:
            dummy = 0

    secure_delete.secure_random_seed_init()

    last_file_name_html = VIEWER_DEFAULT_FILE_NAME_HTML
    last_media_html = VIEWER_DEFAULT_MEDIA_HTML

    # Reset the file upon exit
    atexit.register(reset_viewer)
    signal.signal(signal.SIGINT, kb_interrupt_handler)

    destinations = get_destinations()

    # Get a list of files in the dir
    FOLDER_PATH = sys.argv[1] if (sys.argv[1][-1] == get_os_dir_slash()) else sys.argv[1] + get_os_dir_slash()
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


    # Open the viewer (right now it's just an HTML file lmao)
    #os.system("viewer.html")
    i = 0
    file_list_len = len(file_list) - len(get_exemptions())
    #print(file_list)

    if len(file_list) > 0:

        # Start the browser

        VIEWER_FULL_PATH =  os.path.abspath(VIEWER_HTML_FILE)

        # Start the viewer
        options = webdriver.ChromeOptions()
        options.add_argument("--app=file:///" + VIEWER_FULL_PATH)
        options.add_argument('log-level=3')
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        driver = webdriver.Chrome(options=options)

        terminal_window =  gw.getWindowsWithTitle(WINDOW_TITLE)[0]
        terminal_window.activate()

        for m in get_monitors():
            print(str(m))

        monitor = get_monitors()[0]

        print(monitor)
        terminal_window.moveTo(monitor.width - 1200, monitor.height - 800)

        input_msg = "Ready"
        for file_path in file_list:
            
            # Skip exempt files
            if file_path in get_exemptions():
                continue
            
            next_item = False
            update_viewer = True

            while next_item == False:

                file_name = os.path.basename(file_path)

                # Update the viewer file
                ################################
                if update_viewer:
                    viewer_read = open(VIEWER_HTML_FILE, "r")

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
                    viewer_write = open(VIEWER_HTML_FILE, "w")
                    viewer_write.write(viewer_str_out.encode('ascii', 'xmlcharrefreplace').decode()) # Escape unicode chars
                    viewer_write.close()

                    # Refresh viewer
                    driver.refresh()

                    update_viewer = False

                clear_screen()
                print(input_msg)
                print("=========================================")
                print(file_name + "\n")

                folder_index = 0
                for folder in destinations:
                    print("{} \t- Move to {}".format(folder_index + 1, folder))
                    folder_index += 1

                print("+ (\\) \t- Move to new folder")
                #print("+9 (\\) \t- Move to new folder (overwrite)")

                print("\n` ()\t- Rename file")

                print("")

                print("0 \t- Keep")
                print("00 \t- Defer")
                print("9000 \t- Delete")
                print("9009 \t- Secure Delete")
                print("Ctrl-C \t- Quit")

                print("> ", end='')
                user_input_str = input()

                user_input = 0

                NEW_FOLDER_REGEX = r"\+\-? .*"
                RENAME_FILE_REGEX = r"\`\-? .*"

                # Check if the input is an int
                if not (re.match(NEW_FOLDER_REGEX, user_input_str) or re.match(RENAME_FILE_REGEX, user_input_str)):
                    try:
                        user_input = int(user_input_str)

                    except:
                        input_msg = "Invalid entry"
                        continue

                # print(type(user_input))
                # print(user_input == 0)
                #print(user_input > 0 and user_input < len(DESTINATIONS))
                
                FILE_DIR_PATH = os.path.dirname(file_path)
                FILE_NAME = os.path.basename(file_path)
                FILE_EXT = os.path.splitext(FILE_NAME)[1]
                FILE_NAME_NO_EXT = os.path.splitext(FILE_NAME)[0]
                FILE_EXISTS = os.path.isfile(destinations[user_input - 1] + get_os_dir_slash() + FILE_NAME) if (user_input != 0 and user_input < len(destinations)) else False

                # Move
                if (user_input > 0 and user_input < len(destinations) + 1):
                    # print("Move")
                    
                    renamed = False
                    # Rename the file if it already exists
                    if (FILE_EXISTS):
                        #print("FILE EXISTS")
                        #print(FILE_NAME)
                        #input()
                        renamed = False
                        count = 1
                        while (renamed == False):

                            try:
                                NEW_NAME = f"{FILE_DIR_PATH}{get_os_dir_slash()}{FILE_NAME_NO_EXT}-{count}{FILE_EXT}"
                                os.rename(file_path, NEW_NAME)
                                file_path = NEW_NAME

                            except (FileExistsError, OSError):
                                count += 1

                            renamed = True

                    try:
                        shutil.move(file_path, destinations[user_input - 1])

                        next_item = True
                        input_msg = "File moved to {}".format(destinations[user_input - 1])

                        if (renamed):
                            input_msg += " (Duplicate)"

                    except (shutil.Error):
                        next_item = False
                        input_msg = "== ERROR: Could not move file to {}".format(destinations[user_input - 1])
                
                # Move to new folder
                elif (re.match(NEW_FOLDER_REGEX, user_input_str)):
                    NEW_FOLDER_PATH = user_input_str[2:] + get_os_dir_slash()
                    FOLDER_EXISTS = os.path.isdir(NEW_FOLDER_PATH + get_os_dir_slash())
                    OVERWRITE = (user_input_str[1] == "-")

                    # Check if the file doesn't already exist or if we are in overwrite mode
                    if (FILE_EXISTS == False or OVERWRITE):

                        create_folder_success = False

                        # Create the folder if it doesn't already
                        if (FOLDER_EXISTS == False):
                            try:
                                os.mkdir(NEW_FOLDER_PATH + get_os_dir_slash())
                                next_item = True
                                create_folder_success = True
                            except Exception as e:
                                input_msg = "== ERROR: Could not create folder {}: {}".format(NEW_FOLDER_PATH, type(e).__name__)
                                next_item = False
                                create_folder_success = False
                            
                        else:
                            create_folder_success = True
                        
                        if create_folder_success:
                            try:
                                # Move the file
                                shutil.move(file_path, NEW_FOLDER_PATH)

                                input_msg = "File moved to new folder {}".format(NEW_FOLDER_PATH)
                                next_item = True

                                # Add to the destinations list
                                with open(DESTINATIONS_FILE_PATH, 'a', encoding="utf-8") as file:
                                    file.write(NEW_FOLDER_PATH + "\n")

                                destinations.append(NEW_FOLDER_PATH)

                            except Exception as e:
                                input_msg = "== ERROR: Could not move the file to {}: {}".format(NEW_FOLDER_PATH, type(e).__name__)
                                next_item = False

                    else:
                        input_msg = "== ERROR: Could not move file to {}: Destination file already exists in folder".format(NEW_FOLDER_PATH)
                        next_item = False
                
                # Rename
                elif (re.match(RENAME_FILE_REGEX, user_input_str)):
                    next_item = False

                    try:
                        NEW_NAME = f"{user_input_str[2:]}{FILE_EXT}"
                        NEW_PATH = f"{FILE_DIR_PATH}{get_os_dir_slash()}{NEW_NAME}"
                        os.rename(file_path, NEW_PATH)

                    except OSError as error:
                        input_msg = "== ERROR: Could not rename file to {}".format(NEW_NAME)
                    
                    input_msg = "Renamed {} to {}".format(file_name, NEW_NAME)
                    file_path = NEW_PATH
                    last_file_name_html = file_name_html.encode('ascii', 'xmlcharrefreplace').decode()
                    last_media_html = media_html
                    update_viewer = True

                # Keep
                elif (user_input_str == "0"):
                    next_item = True
                    input_msg = "File exempted"

                    with open('exemptions.txt', 'a', encoding="utf-8") as file:
                        file_path += "\n"
                        file.write(file_path)

                # Defer
                elif (user_input_str == "00"):
                    next_item = True
                    input_msg = "File skipped"

                # Delete
                elif (user_input_str == "9000"):
                    next_item = True                    
                    input_msg = "File deleted"
                    send2trash(file_path)

                # Secure delete
                elif (user_input_str == "9009"):
                    next_item = True                    
                    input_msg = "File deleted securely"
                    secure_delete.secure_delete(file_path)

                # Invalid input
                else:
                    # print("Err")
                    input_msg = "Invalid entry"
                    next_item = False
                    update_viewer = False
                
                
                # input()


            # Update the last media html
            last_file_name_html = file_name_html.encode('ascii', 'xmlcharrefreplace').decode()
            last_media_html = media_html
            i += 1

        # Reset the viewer file
        ################################
        reset_viewer()
    

if __name__ == '__main__':
    try:
        main()
    except EOFError as e:
        pass
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        traceback.print_exc()