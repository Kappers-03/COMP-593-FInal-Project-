
#   LAB X PYTHON 
#   -----------------------------------------------------------------
#   -----------------------------------------------------------------
#   PROGRAM DESCRIPTION: This lab is designed to create a desktop
#   background from the NASA API and gather infomation from the  
#   photo of the day from NASA using it's APOD API.     
#   -----------------------------------------------------------------
#   -----------------------------------------------------------------
#   USAGE: python A9L-NolanKapshey.py
#
#   -----------------------------------------------------------------
#   -----------------------------------------------------------------
#
#   DUE DATE: MONDAY APRIL 29TH, 2022
#
#   -----------------------------------------------------------------
#   -----------------------------------------------------------------
#   HISTORY:
#       DATE        AUTHOR      Description
#       2022-04-16  N.KAPSHEY   Initial Creation
#
#   _________________________________________________________________


#   Insert Imports 
import ctypes
import json
from mimetypes import common_types
import sqlite3
from urllib import response
import requests
import time
import hashlib
import os
from sys import argv, exit
from datetime import datetime, date
from hashlib import sha256
from os import path

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
   
    # Download today's APOD
    image_url = apod_info_dict ['url']
    image_msg = download_apod_image(image_url)  
    image_sha256 = hashlib.sha256(image_msg).hexdigest()
    image_size = len(image_sha256)
    image_path = get_image_path(image_url, image_dir_path)

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg, image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
   #    Determine the Images Directory From AGRV and Varify if it is a Directory
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    print() # Used for line spacing 
    return apod_date

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    #   Join the directory path and image name to create a image path
    print ("Getting Image Path...", end =' ')
    time.sleep(2)
    img_url = image_url
    img_url = img_url.split('/')[-1]
    img_path = os.path.join(dir_path, img_url)
    print ("IMAGE PATH SUCCESSFULLY RECIEVED")
    print () # Used for line spacing
    return img_path

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    #   Determine API Key, URL, & the parameters
    apiKey = str('4eqD5iTD7DnnzsPig8ZmTIoHeXmvG8LMa0cYQSXv')
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': apiKey,
        'date': date,
        'url': None        
    }
    #   Send GET requests to the URL and Params to create DICT
    apod_dict = requests.get(url, params=params)
    print ("Checking connection with API Dictionary...", end = ' ')
    time.sleep(2)
    if apod_dict.status_code == 200:
        print('Success!',"\n")
        return apod_dict.json()
    else:
        print('Action Failed. Response code:', apod_dict.status_code)             
    return
    
    
def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """   
    #   Print out all of the parameters of URL, PATH, SHA256, & SIZE
    print("Gathering information...")
    time.sleep(2)
    print() # Used for line spacing 
    print("LINK TO APOD PHOTO:", image_url)
    print("STORED IN THE PATH:", image_path) 
    print("SIZE OF THE IMAGE:", image_size, "BYTES") 
    print("SHA256 OF IMAGE:", image_sha256)
    print() # Used for Line spacing 
    
    return 


def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    #   Download the APOD image from the URL
    img_msg = requests.get(image_url)
    print ("Reciving the Image Url...", end = ' ')
    time.sleep(2)
    if img_msg.status_code == 200:
        print("Success!")
        print() # Used for line spacing 
        return img_msg.content
    else:
        print ('Action Failed. Response code:', img_msg.status_code)   
    return 


def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    #   Get the image_msg from main and save the image
    img_data = image_msg
    print(R"Saving the image...", end = ' ')
    with open (image_path, 'wb') as fp:
        fp.write(img_data)
        time.sleep(2)
        print ("Success!!")
        print() # Used for line spacing
        return
 
   
def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    #   Retrive the Connection object and cursor object
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    
    #   Create the APOD table
    create_Apod_Table = """ CREATE TABLE IF NOT EXISTS apod_image_database (
                            sha256 text PRIMARY KEY,
                            date_made text,
                            f_size text NOT NULL,
                            location_file text NOT NULL,
                            created_on datetime NOT NULL
                            );"""
  
    
    # Execute my cursor
    myCursor.execute(create_Apod_Table)
    myConnection.commit()
    myConnection.close()


def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    #   Add the variables to the database 
    date_stamp = datetime.now()
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    add_info ="""INSERT INTO apod_image_database(sha256,
    f_size,
    location_file,
    created_on   
    )
    VALUES (?,?,?,?);"""
    myImage = (image_sha256,
                image_size,
                image_path,
                date_stamp
    )
    #   Execute the cursor to commit all the variables added to db
    myCursor.execute(add_info, myImage)
    myConnection.commit()
    myConnection.close()
    return 


def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    #   Connect to the database and see if there is duplicate sha256 values
    myConnection = sqlite3.connect(db_path)
    myCursor = myConnection.cursor()
    print("Checking if image is in database...")
    time.sleep(2)
    myCursor.execute("SELECT * FROM apod_image_database WHERE sha256 = '" + image_sha256 + "'")
    sha_val = myCursor.fetchall()
    if len(sha_val) > 0:
        print ("IMAGE ALREADY IN DB")
        print () # Used for line spacing
        return True
    else:
        print ("IMAGE NOT IN DB")
        print () # Used for line spacing
        return False
    
def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    #   Place the image in the Desktop Background 
    print ("Setting Desktop Background....")
    time.sleep(2)
    try:
        print ("Program Successfully Completed!")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
    except:
        print("ERROR: Unable to set the desktop background.") 
main()