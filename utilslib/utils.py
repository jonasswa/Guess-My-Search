import os

def get_google_API_key():
    path_to_txt_key = r'./misc/googleAPI.txt'
    key = ''

    with open(path_to_txt_key) as APIfile:
        for line in APIfile:
            key = line

    return key
