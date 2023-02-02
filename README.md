# Google Photos - Flickr Sync script

Based heavily on https://github.com/alexis-mignon/python-flickr-api/wiki/API-reference
and https://towardsdatascience.com/how-to-download-images-from-google-photos-using-python-and-photos-library-api-6f9c1e60a3f3

### authentication
Location to store Google photos credentials:
.google-photos-api/credentials/client_secret.json
See the readme in the google-photos-api folder for more details on how to setup Google Photos API access.
Trick to load Google photos full res and with metadata: 
https://developers.google.com/photos/library/guides/access-media-items#image-base-urls

Location to store Flickr Credentials: flickr-api/credentials. The result after authenticating is saved in a authentication_file.txt.

Both the Google Photos and Flickr maps have ipynb notebooks that were just to tinker this script together. The final functionality is found in script.py along with a GooglePhotosAPI.py helper script.

### Running the script:
python transfer_photos.py

### Warnings
Movies are currently not properly loaded.

