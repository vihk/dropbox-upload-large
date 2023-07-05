import dropbox
import os
import requests

file_path = "/Users/user/Desktop/refreshtoken .png"
destination_path = "/"+file_path.rsplit('/', 1)[-1]
#for some reason it really wants us to specify the file name, so I used rsplit to grab the file name
#this saves into the root folder of our dropbox app folder
#refresh_token = "zymDZJlJ2A0AAAAAAAAAASF_1t9epUl584kwCRkJcM2vmRs0zJJ1QmqmWICWxfuI"

refresh_token = "<REFRESHTOKEN>"
app_key = "<APPKEY>"
app_secret = "<APPSECRET>"

# Set the request parameters
url = "https://api.dropboxapi.com/oauth2/token"
data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_id": app_key,
    "client_secret": app_secret 
}
# post request
response = requests.post(url, data=data)

# grab access token from  response
access_token = response.json()["access_token"]

dbx = dropbox.Dropbox(access_token, app_key="ysjomxjte2951w9",timeout=1100)

f = open(file_path,'rb')
#open file in binary mode to r/w using bytes (required).
file_size = os.path.getsize(file_path)

CHUNK_SIZE = 4 * 1024 * 1024 #4 megabytes

if file_size <= CHUNK_SIZE:
    dbx.files_upload(f.read(), destination_path)
else:
    upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE)) #read 4mb of the file, start session
    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,offset=f.tell())
    # UploadSessorCursor contains the upload session ID and the offset.
    # I'm guessing they're setting the initial offset to 0mb (right?) through f.tell()
    # f.tell(): returns an integer giving the file object’s current position in the file represented as number of bytes from the beginning of the file.

    commit = dropbox.files.CommitInfo(path=destination_path)
    #Contains the path and other optional modifiers for the future upload commit.

    while f.tell() < file_size:
        if ((file_size - f.tell()) <= CHUNK_SIZE):
            #if remaining filesize is less than 4mb
            print(dbx.files_upload_session_finish(f.read(CHUNK_SIZE),cursor,commit))
            print('\n\n\ncomplete')
            #Finish the upload session and save the uploaded data to the given file path.
        else:
            dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE),cursor)
            #append more data to an upload session
            cursor.offset = f.tell()
            #offset updated to new byte position in file
            b_left = round(((file_size-f.tell())/file_size),2)*100
            b_left = str(b_left)+"%" if b_left < 1000 else 0
            print("\r       {} remaining....".format(b_left), end="")
            #fun percentage remaining printing thing
            