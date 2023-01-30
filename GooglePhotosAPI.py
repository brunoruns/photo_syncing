import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import requests
import json
import pandas as pd

class GooglePhotosApi:
    def __init__(self,
                 api_name = 'photoslibrary',
                 client_secret_file= r'./google-photos-api/credentials/client_secret.json',
                 api_version = 'v1',
                 scopes = ['https://www.googleapis.com/auth/photoslibrary']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api

        Return:
            service:
        '''

        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./google-photos-api/credentials/token_{self.api_name}_{self.api_version}.pickle'

        self.cred = None

    def run_local_server(self):
        # is checking if there is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if there is no pickle file with stored credentials, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server()

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)
        
        return self.cred

#Listing all Albums:
    def getAlbum(self, album_name):
        creds = self.cred
        album_url = "https://photoslibrary.googleapis.com/v1/sharedAlbums"
        headers = {
                'content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(creds.token)
            }

        try:
            res = requests.request("GET",album_url, headers=headers)
        except:
            print('Request error')
        json_result = res.json()
        print(res.status_code)

        for i in range(0, len(json_result["sharedAlbums"])) :
            if json_result["sharedAlbums"][i]['title'] == album_name :
                return json_result["sharedAlbums"][i]['id']
        print("Album not found.")
        return None


    def get_response_from_medium_api(self, year, month, day, album_id=None):
        url = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
        creds = self.cred

        payload = {
                    "filters": {
                    "dateFilter": {
                        "dates": [
                        {
                            "day": day,
                            "month": month,
                            "year": year
                        }
                        ]
                    }
                    }
                }
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(creds.token)
        }
        
        try:
            res = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        except:
            print('Request error') 
        
        return(res)

    def list_of_media_items(self, year, month, day, album_id, media_items_df):
        '''
        Args:
            year, month, day, album_id: day for the filter of the API call 
            media_items_df: existing data frame with all find media items so far
        Return:
            media_items_df: media items data frame extended by the articles found for the specified tag
            items_df: media items uploaded on specified date
        '''

        items_list_df = pd.DataFrame()
        
        # create request for specified date
        response = self.get_response_from_medium_api(year, month, day, album_id)

        try:
            for item in response.json()['mediaItems']:
                items_df = pd.DataFrame(item)
                items_df = items_df.rename(columns={"mediaMetadata": "creationTime"})
                items_df.set_index('creationTime')
                items_df = items_df[items_df.index == 'creationTime']

                #append the existing media_items data frame
                items_list_df = pd.concat([items_list_df, items_df])
                media_items_df = pd.concat([media_items_df, items_df])
        
        except:
            print(response.text)

        return(items_list_df, media_items_df)

#testcode
#media_items_df = pd.DataFrame()
#list_of_media_items(2023, 1, 28, album_id, media_items_df)