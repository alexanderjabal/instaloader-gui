import os
import sys
from time import sleep
import configparser
import requests
import urllib
from urllib.request import urlretrieve
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

config = configparser.ConfigParser(interpolation=None) # https://stackoverflow.com/a/62592195
config.read("settings.ini")
default_output_path = os.getenv("USERPROFILE") + "\\Downloads\\"

def create_settings():
   if not os.path.isfile("settings.ini"):
      config["MAIN"] = {"output_path": default_output_path, "session_id": ""}
      with open("settings.ini", "w") as configfile:
         config.write(configfile)

create_settings()

def browse():
   chosen_dir = filedialog.askdirectory() # Open directory browser
   output_folder_entry.delete(0, "end") # Clear the widget of any text
   output_folder_entry.insert(0, chosen_dir) # Insert the chosen dir into the widget

   # change folder in ini file to the last used folder so program remembers last folder
   # config.read("settings.ini")
   session_id = config["MAIN"]["session_id"]
   config["MAIN"] = {"output_path": chosen_dir.replace("\\", "\\\\"), "session_id": session_id}
   with open("settings.ini", "w") as configfile:
      config.write(configfile)

def go_back():
   """
   Revert back to what the window looks like on startup
   """

   # Revert to original download button and label
   global download_button
   download_button.destroy()
   download_button = tk.Button(root, text="Download", font="Arial 14 bold", width=11, command= lambda: request(session_id=session_id, post_url=post_url_entry.get())) # https://stackoverflow.com/a/6921225
   download_button.grid(row=3, column=0, padx=10, pady=10, sticky="W")
   # download_label = tk.Label(root, font="Arial 11", text="Instaloader GUI v1.0")
   # download_label.grid(row=4, column=1, columnspan=2, pady=10, sticky="W") # Put the label in place next to the download button

   # Destroy multiple video mode widgets
   video_choice_label.destroy()
   video_choice_slider.destroy()
   back_button.destroy()

   # Clear filename entry widget of text and add post URL field back in
   # post_url_entry.delete(0, "end")
   global post_url_label
   global post_url_entry
   post_url_label = tk.Label(root, font="Arial 12 bold", text="Post URL", padx=10, pady=5)
   post_url_label.grid(row=0, column=0, sticky="W", pady=(15,0))
   post_url_entry = tk.Entry(root, font="Arial 12", width=36)
   post_url_entry.grid(row=0, column=1, sticky="W", pady=(15,0))
   output_filename_entry.delete(0, "end")

# lambda set_url : video_urls[video_choice_slider.get() - 1]

def write_url(url):
   """
   Write URL to ini file because I can't fucking get it to work

   I tried to generate usable URLs from the scale events using lambda functions but couldn't get it to work
   So just write the url to the file and pass it to the download function from there I guess
   """
   config["URL"] = {"url":url}
   with open("settings.ini", "w") as configfile:
      config.write(configfile)

def request(session_id, post_url=""):
   # get the source code, check if multiple urls, if so: show the slider and change the download button functionality to the download func
   # if not, download the video from the url right away

   global video_choice_label # For changing it in the download function and deleting in go_back function
   global video_choice_slider # For deleting in go_back function
   global back_button # For deleting in go_back function
   global download_label # Global so it can access the default download label
   global download_button  # Global so it can access the default download button



   if not post_url: # If no post URL specified replace download label with error message
      download_label.destroy() # Destroy the default download label and replace it with error message
      download_label = tk.Label(root, font="Arial 11", text="No post URL specified", fg="red")
      download_label.grid(row=4, column=1, columnspan=2, pady=10, sticky="W") # Put the label in place next to the download button
      return

   elif "https://instagram.com/" not in post_url: # If a non-Instagram URL is entered
      download_label = tk.Label(root, font="Arial 11", text="Please specify an Instagram URL", fg="red")
      download_label.grid(row=4, column=1, columnspan=2, pady=10, sticky="W") # Put the label in place next to the download button
      return

   cookies = {"sessionid": session_id}
   video_urls = []

   r = requests.get(post_url, cookies=cookies)
   for line in r.text.splitlines(): 
      if "video_url" in line: # Find the line with "video_url" strings
         for item in line.split(","): # Split line into list for indexing video urls
            if item.startswith('"video_url":'): # Loop through all items and find all video urls
               video_urls.append(item.replace('"video_url":"', '').replace("\\", "/").replace("/u0026", "&")) # Format urls

   # print(video_urls)
   if len(video_urls) > 1: # More than 1 video in post
      download_label.destroy()
      post_url_entry.grid_forget()
      post_url_label.grid_forget()
      write_url(video_urls[0]) # Write the 1st url on start, because the lambda function only gets called when you adjust the slider, so the first url is not written
      slider_val = tk.IntVar()


      video_choice_label = tk.Label(root, font="Arial 11", text="Choose a video to download")
      video_choice_label.grid(row=3, column=1, pady=(20,0), sticky="N")
      video_choice_slider = tk.Scale(root, from_=1, to=len(video_urls), orient="horizontal", length=320, variable=slider_val, command=lambda x: write_url(video_urls[slider_val.get() - 1]))
      video_choice_slider.grid(row=4, column=1)
      back_button = tk.Button(root, text="Back", font="Arial 12", width=10, command=go_back)
      back_button.grid(row=4, column=2, sticky="W")


   
      download_button.destroy()
      # print(video_urls)
      # Define variables to pass into the download function
      
      
      # url = video_urls[video_choice_slider.get() - 1]
      # url = video_urls[slider_val.get() - 1]
      
      # print(slider_val.get() - 1)
      # url = config["URL"]["url"] # This doesn't work because it saves the first downloaded link only, call the function by reading directly from the file

      # output = output_folder_entry.get().replace("/", "\\") + "\\" # Replace forward slashes with backslashes and add trailing backslash so filename can be appended

      # filename = output_filename_entry.get() # Same goes for this as for the URL
      # if ".mp4" in filename: # Filename sanitation
      #    filename.replace(".mp4", "")

      # Replace with a download button with the download function
      download_button = tk.Button(root, text="Download", font="Arial 14 bold", width=11, command= lambda: download(url=config["URL"]["url"], output=config["MAIN"]["output_path"], filename=output_filename_entry.get().replace(".mp4", ""))) 
      download_button.grid(row=4, column=0, padx=10, pady=10, sticky="W")
         
         
            
         # download(url, output, filename)
   else: # Only 1 video
      url = video_urls[0]
      download(url=url, output=output_folder_entry.get(), filename=output_filename_entry.get())
      

   # print(video_urls)
   # download_label.destroy() # Destroy the default message or the error message
   # download_label = tk.Label(root, font="Arial 11", text=post_url)
   # download_label.grid(row=3, column=1, columnspan=2, pady=10, sticky="W") # Put the label in place next to the download button

def download(url, output, filename=""):
   global video_choice_label
   global download_label
   end = url.find(".mp4") + 4

   # Make sure the paths always end with their corresponding slash
   if "/" in output and output[-1] != "/":
      output += "/"
   elif "\\" in output and output[-1] != "\\":
      output += "\\"

   if not filename: # No filename specified, use default filename
      urlretrieve(url, output + url[55:end]) 
      try: # Multiple videos mode
         video_choice_label.destroy()
         video_choice_label = tk.Label(root, font="Arial 11", text=f"Saved {url[55:end]} to {output}", wraplength=320)
         video_choice_label.grid(row=3, column=1, pady=(20,0), sticky="N")
      except: # Single video mode
         download_label.destroy()
         # print(f"Saved {url[55:end]} to {output}")
         download_label = tk.Label(root, font="Arial 11", text=f"Saved {url[55:end]} to {output}", wraplength=350)
         download_label.grid(row=4, column=1, columnspan=2, sticky="W")

   else: # Save video to specified filename
      urlretrieve(url, output + filename + ".mp4") 
      try: # Multiple videos mode
         video_choice_label.destroy()
         video_choice_label = tk.Label(root, font="Arial 11", text=f"Saved {filename}.mp4 to {output}", wraplength=320)
         video_choice_label.grid(row=3, column=1, pady=(20,0), sticky="N")
      except: # Single video mode
         download_label.destroy()
         print(f"Saved {filename}.mp4 to {output}")
         download_label = tk.Label(root, font="Arial 11", text=f"Saved {filename}.mp4 to {output}", wraplength=320)
         download_label.grid(row=4, column=1, columnspan=2, sticky="W")


def resource_path(relative_path): # https://stackoverflow.com/a/43073526, https://stackoverflow.com/a/69373831
   try:       
       base_path = sys._MEIPASS
   except Exception:
       base_path = os.path.abspath(".")
   
   return os.path.join(base_path, relative_path)


# Configure root window
root = tk.Tk()
root.title("Instaloader GUI")
try:
   base_path = sys._MEIPASS
   root.iconbitmap(default=resource_path("insta.ico"))
except: 
   pass
root.minsize(600,190)
root.maxsize(600,250)
root.columnconfigure((0,1,2), weight=1) # Configure the 3 columns

# Post URL
post_url_label = tk.Label(root, font="Arial 12 bold", text="Post URL", padx=10, pady=5)
post_url_label.grid(row=0, column=0, sticky="W", pady=(15,0))
post_url_entry = tk.Entry(root, font="Arial 12", width=36)
post_url_entry.grid(row=0, column=1, sticky="W", pady=(15,0))

# Output folder
tk.Label(root, font="Arial 12 bold", text="Output folder", padx=10, pady=5).grid(row=1, column=0, sticky="W")
ini_output_folder = config["MAIN"]["output_path"]
output_folder_entry = tk.Entry(root, font="Arial 12", width=36)
output_folder_entry.insert(0, ini_output_folder)
output_folder_entry.grid(row=1, column=1, sticky="W")
folder_select_button = tk.Button(root, text="Select folder", font="Arial 12", width=10, command=browse)
folder_select_button.grid(row=1, column=2, sticky="W")

# Output filename
tk.Label(root, font="Arial 12 bold", text="Output filename", padx=10, pady=5).grid(row=2, column=0, sticky="W")
output_filename_entry = tk.Entry(root, font="Arial 12", width=36)
output_filename_entry.grid(row=2, column=1, sticky="W")
tk.Label(root, font="Arial 12 bold", text=".mp4",).grid(row=2, column=2, sticky="W")
# tk.Label(root, font="Arial 11", text="Succesfully saved {filename} to {output_folder}", wraplength=500).grid(row=3, column=1, columnspan=2, pady=10, sticky="W") # This needs to go at the end of the download function

# Download button and label
session_id = config["MAIN"]["session_id"] # Session ID to pass to the request function
download_button = tk.Button(root, text="Download", font="Arial 14 bold", width=11, command= lambda: request(session_id=session_id, post_url=post_url_entry.get())) # https://stackoverflow.com/a/6921225
download_button.grid(row=4, column=0, padx=10, pady=10, sticky="W")
download_label = tk.Label(root, font="Arial 11", text="Instaloader GUI v1.0")
download_label.grid(row=4, column=1, columnspan=2, pady=10, sticky="W") # Put the label in place next to the download button

# download_label.destroy()
# download_label = tk.Label(root, font="Arial 11", text="Saved test.mp4 to test", wraplength=320)
# download_label.grid(row=4, column=1, columnspan=2, pady=10, sticky="W")





# directory_dialog.grid(row=5, column=1)
root.mainloop()

