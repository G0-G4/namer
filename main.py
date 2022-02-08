import requests
import json
import time
import os
import argparse
import re


API = 'https://audiotag.info/api'

def recognizeSong(file, apikey):
    start_time = time.time()
    payload ={
        'action': 'identify',
        'apikey': apikey,
        'start_time':40,
        'time_len':15
        }
    result = requests.post(API,data=payload,
        files={'file': open(file, 'rb')})
    result_object = json.loads(result.text)
    print(result_object)
    if result_object['success']==True and result_object['job_status']=='wait':
        token = result_object['token']
        n=1
        job_status = 'wait'
        while n < 100 and job_status=='wait':
            time.sleep(0.5) 
            print('request:%d'%(n))
            n+=1
            payload = {'action': 'get_result', 'token':token, 'apikey': apikey}
            result = requests.post(API,data=payload)
            result_object = json.loads(result.text)
            print(result_object)
            if 'success' in result_object and result_object['success']==True:
                job_status = result_object['result']

    print(time.time() - start_time)
    if (result_object['success']   and 
        not result_object['error'] and
        result_object['result'] == 'found'):
        return '-'.join(result_object['data'][0]['tracks'][0][:-2])
    return ''

# def recognizeSong(file, apikey):
#     return "Name"

def checkMask(mask, file):
    return re.match(mask, file)

def getFileNameAndExtension(file_with_ext):
    dot = file_with_ext.rfind('.')
    return file_with_ext[:dot if dot != -1 else len(file_with_ext)], file_with_ext[dot:]

def getSongName(music_dir, file_name, ext, apikey):
    file = os.path.join(music_dir, file_name + ext)
    file_wav = os.path.join(music_dir, file_name + ".wav")
    os.system(f'ffmpeg -ss 40 -t 16 -i "{file}" -ar 8000 -ac 1 -vn "{file_wav}"')
    song_name = ''
    if os.path.exists(file_wav):
        os.remove(file_wav)
        song_name = recognizeSong(file_wav, apikey) 
    if song_name:
        song_name = song_name.translate({ord(c): None for c in '+=[]:;«,./?\:*?«<>|'})
        return song_name
    return ''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    'rename audio files to song names using https://audiotag.info/ API')
    parser.add_argument('key', help='audiotag.info API key')
    parser.add_argument('-d', help='music directory', required=True, metavar='DIRECTORY')
    parser.add_argument('-m', help='mask to identify which files should be renamed',
        required=True, metavar='MASK')
    args = parser.parse_args()
    apikey = args.key
    music_dir = os.path.abspath(args.d)
    mask = args.m
    print('files to be renamed:')
    print('----------------')
    i = 0
    renamed = 0
    for file in os.listdir(music_dir):
        if checkMask(mask, file):
            old_file_name, ext = getFileNameAndExtension(file)
            if new_file_name := getSongName(music_dir, old_file_name, ext, apikey):
                old_file = os.path.join(music_dir, file)
                new_file = os.path.join(music_dir, new_file_name + ext)
                if os.path.exists(new_file):
                    os.rename(old_file, os.path.join(music_dir, new_file_name +
                    str(renamed) + ext))
                else:
                    os.rename(old_file, new_file)
                renamed += 1
            i += 1
    print('----------------')
    print(f'renamed: {renamed}/{i}')