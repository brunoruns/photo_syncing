import GooglePhotosAPI as gpAPI
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import os
import json
import flickr_api

# initialize photos api and create service
google_photos_api = gpAPI.GooglePhotosApi()
creds = google_photos_api.run_local_server()

# getting data for a a specific date up to now

# Images should only be downloaded if they are not already available in downloads
# Herefor the following code snippet, creates a list with all filenames in the /downloads/ folder
files_list = os.listdir(r'./google-photos-api/downloads')
files_list_df = pd.DataFrame(files_list)
files_list_df = files_list_df.rename(columns={0: "filename"})
#print(files_list_df.head(2))

# create a list with all dates between start date and today
sdate = date(2023,1,7)   # start date
edate = date.today()

#take the logged end date
if (os.path.isfile("./last_run.txt")):
    stringDate = ""
    with open('last_run.txt', 'r') as f:
        stringDate = f.read()
    sdate = date(int(stringDate[0:4]),int(stringDate[5:7]), int(stringDate[8:10]))
    print("Previous run at " + stringDate + ", continuing from here on.")

date_list = pd.date_range(sdate,edate-timedelta(days=1),freq='d')
print(date_list)

#search the correct album
album_id = google_photos_api.getAlbum("Sync Flickr")
media_items_df = pd.DataFrame()

for date in date_list:
    
    # get a list with all media items for specified date (year, month, day)
    items_df, media_items_df = google_photos_api.list_of_media_items(year = date.year, month = date.month, day = date.day, album_id=album_id,  media_items_df = media_items_df)

    if len(items_df) > 0:
        # full outer join of items_df and files_list_df, the result is a list of items of the given 
        #day that have not been downloaded yet
        if len(files_list_df) > 0:
            items_not_yet_downloaded_df = pd.merge(items_df, files_list_df,on='filename',how='left')
            items_not_yet_downloaded_df.head(2)
        else:
            items_not_yet_downloaded_df = items_df

        # download all items in items_not_yet_downloaded
        for index, item in items_not_yet_downloaded_df.iterrows():
            url = item.baseUrl + "=d" #the =d is for downloading using all metadata
            response = requests.get(url)

            file_name = item.filename
            destination_folder = './google-photos-api/downloads/'

            with open(os.path.join(destination_folder, file_name), 'wb') as f:
                f.write(response.content)
                f.close()
                
        print(f'Downloaded items for date: {date.year} / {date.month} / {date.day}')
    else:
        print(f'No media items found for date: {date.year} / {date.month} / {date.day}')
            
#save a list of all media items to a csv file
current_datetime = str(datetime.now())
filename = f'item-list-{current_datetime}.csv'

#save a list with all items in specified time frame
media_items_df.to_csv(f'./google-photos-api/media_items_list/{filename}', index=True)

print("Data loading from Google finished.")
print("Starting upload to Flickr...")

#reading credentials
def js_r(filename):
   with open(filename) as f_in:
       return(json.load(f_in))

cred_file = "./flickr-api/credentials/client_secret.json"
cred_data = js_r(cred_file)

flickr_api.set_keys(api_key = cred_data["api_key"], api_secret = cred_data["api_secret"]) # not this line if you store these details in flickr_keys.py
flickr_api.set_auth_handler("./flickr-api/authentication_file.txt") # or whatever you save your auth file as

#getting the album
user = flickr_api.Person.findByUserName('brunoruns')
photosets = user.getPhotosets()
required_index = 0;
for i in range(0, len(photosets)):
    #print(photosets[i].title)
    if (photosets[i].title == "sync google photos sara"):
        print("required index: " + str(i))
        required_index = i
auto_album = photosets[required_index]

#loading everything in the album
### script to load everything in the map
source_folder = "./google-photos-api/downloads/"
files_list = os.listdir(source_folder)

for file_name in files_list:
    a_photo = flickr_api.upload(photo_file = os.path.join(source_folder, file_name), title = file_name, is_public="0")
    auto_album.addPhoto(photo = a_photo)
    print("Photo " + file_name + " succesfully added." )

print("All files uploaded to Flickr.")
print("Cleaning up...")

#TODO writing latest known date of sync
edate = date.today()
with open('last_run.txt', 'w') as f:
    f.write(str(edate))
    

#cleaning up files
import os, shutil
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))