import os
import subprocess
import sys
import time
import threading
import download_video
import yt_dlp
import tkinter as tk

FROM_EXT = ""
TO_EXT = ""
CONST = "0"
TITLE = ""

def download():
    header_label.config(text="DOWNLOADER\nPlease enter the link below")
    return 0
def convert():
    header_label.config(text="CONVERTER\nPlease enter the file path below")
    return 0

def trim(text,char_limit=50):
    return text[:char_limit]

def alert_box(message):
    alert = tk.Tk()
    alert.title("Alert!")
    alert.geometry("300x200")
    
    # Create a Text widget for multiline text
    message_text = tk.Text(alert, wrap=tk.WORD, height=5, width=35)
    message_text.insert(tk.END, message)
    message_text.config(state=tk.DISABLED)  # Make it read-only
    message_text.pack(pady=10)
    
    message_ok = tk.Button(alert, text="OK", command=alert.destroy)
    message_ok.pack(pady=5)
    
    alert.mainloop()

def output_message(message):
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "> - " + message + '\n')
    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)

def main_download():
    global CONST
    global TITLE
    global FROM_EXT
    global TO_EXT
    if(CONST >= "1"):
        if(FROM_EXT == "" or TO_EXT == ""):
            alert_box("Please Enter Valid extensions")
            return
        CONST="0"
        print(FROM_EXT + " and " + TO_EXT)
        if(FROM_EXT=="video"):
            if(TO_EXT=="video"):
                #download youtube video as video
                download_video.download_youtube_video(entry.get())
            elif(TO_EXT=="audio"):
                #download youtube video as music
                download_video.download_youtube_music(entry.get())
            output_message("Downloaded as " + TITLE + ".mp4")
        elif(FROM_EXT=="audio"):
            download_video.download_youtube_music(entry.get())
            output_message("Downloaded as " + TITLE + ".webm")
        download_button.config(text="Search")
        entry.config(state=tk.NORMAL)
        alert_box("Downloaded!")
    else:
        try:
            link=entry.get()
            ydl_opts ={'quiet':False,'force-generic-extractor':True,'extract_flat':True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link,download=False)
            TITLE = info['title']
            CONST="1"
            if(link.find("music")==-1):
                FROM_EXT="video"
                from_options.append("video")
                from_options.remove("Select")
                to_options.remove("Select")
                update_extensions()
            else:
                FROM_EXT="audio"
                from_options.append("audio")
                to_options.remove("video")
                from_options.remove("Select")
                to_options.remove("Select")
                update_extensions()
        except Exception as e:
            output_message(f"ERROR: {e}")
            print(f"ERROR: {e}")
            return
        download_button.config(text="Download")
        entry.config(state=tk.DISABLED)
        output_message("To be downloaded: "+info['title'])
        alert_box("To be downloaded: "+info['title'])

def paste():
    try:
        clipboard_content = root.clipboard_get()
        entry.delete(0, tk.END)
        entry.insert(0, clipboard_content)
        clipboard_content_trimmed = clipboard_content  
        if(len(clipboard_content) >= 50):
            clipboard_content_trimmed = trim(clipboard_content,50)
        output_message(f"Pasted: `{clipboard_content_trimmed}`...")
        if (clipboard_content.find("youtu") == -1):
            #Not Found
            entry.delete(0,tk.END)
            output_message(f"Link is Bad, Deleted entry `{clipboard_content_trimmed}`...")
            alert_box("Provided link is not supported\n(Hint- Use official Youtube/Music links)")
    except tk.TclError:
        entry.delete(0, tk.END)
        output_message("Clipboard is Empty")

def update_extensions():
    global from_dropdown
    global to_dropdown
    global convert_label_2
    convert_label_1.pack_forget()
    from_dropdown.pack_forget()
    convert_label_2.pack_forget()
    to_dropdown.pack_forget()

    convert_label_1.pack(side=tk.LEFT)
    from_dropdown = tk.OptionMenu(convert_frame,selected_from_options, *from_options, command = update_selection_from)
    from_dropdown.pack(side=tk.LEFT)
    convert_label_2.pack(side=tk.LEFT)
    to_dropdown = tk.OptionMenu(convert_frame,selected_to_options, *to_options, command = update_selection_to)
    to_dropdown.pack(side=tk.LEFT)

def update_selection_from(value):
    global FROM_EXT
    FROM_EXT=value
    output_message(f"Selected source: {value}")

def update_selection_to(value):
    global TO_EXT
    TO_EXT=value
    output_message(f"Selected destination: {value}")

root = tk.Tk()
root.title("Youtube-Downloader GUI")
root.geometry("600x400")

menu_bar = tk.Menu(root)
menu_sub_items = tk.Menu(menu_bar, tearoff=0)
menu_sub_items.add_command(label="Download", command=download)
menu_sub_items.add_command(label="Convert", command=convert)
menu_sub_items.add_separator()
menu_sub_items.add_command(label="Exit", command=root.destroy)
menu_bar.add_cascade(label="Actions", menu=menu_sub_items)
root.config(menu=menu_bar)

#HEADER
header_frame = tk.Frame(root)
header_frame.pack(fill=tk.X)
header_label = tk.Label(header_frame, text="Welcome To Youtube Downloader\n Made with ❤️")
header_label.pack(side=tk.TOP)

#PASTE AND GO FRAME
main_frame = tk.Frame(root)
main_frame.pack(pady=20)
entry_label = tk.Label(main_frame, text="Link: ")
entry_label.pack(side=tk.LEFT)
entry = tk.Entry(main_frame,width=30)
entry.pack(side=tk.LEFT, padx=5)
paste_button = tk.Button(main_frame,text="Paste", command=paste)
paste_button.pack(side=tk.LEFT, padx=5)

download_button = tk.Button(main_frame, text="Search", command=main_download)
download_button.pack(side=tk.RIGHT, padx=5)

#Convert from "" to "" FRAME
convert_frame = tk.Frame(root)
convert_frame.pack(pady=0)

#from
convert_label_1 = tk.Label(convert_frame, text="From ")
convert_label_1.pack(side=tk.LEFT)
from_options = ["Select"]
selected_from_options = tk.StringVar(value=from_options[0])
from_dropdown = tk.OptionMenu(convert_frame,selected_from_options, *from_options, command = update_selection_from)
from_dropdown.pack(side=tk.LEFT)

#to
convert_label_2 = tk.Label(convert_frame, text=" To ")
convert_label_2.pack(side=tk.LEFT)
to_options = ["Select", "video", "audio"]
selected_to_options = tk.StringVar(value=to_options[0])
to_dropdown = tk.OptionMenu(convert_frame, selected_to_options, *to_options, command = update_selection_to)
to_dropdown.pack(side=tk.LEFT)

#FOOTER
footer_frame = tk.Frame(root)
footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

output_text = tk.Text(footer_frame)
output_text.config(state=tk.DISABLED)
output_text.pack(pady=10,padx=10)

root.mainloop()