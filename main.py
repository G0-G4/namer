import requests
import json
import time
import os


def getSongName(filename):
    start_time = time.time()
    apikey = '' # generate and place here your unique API access key, the key

    payload = {'action': 'identify', 'apikey': apikey, 'start_time':40, 'time_len':15}
    result = requests.post('https://audiotag.info/api',data=payload, files={'file': open(filename, 'rb')})
    print(result.text)
    result_object = json.loads(result.text)
    print(result_object)
    if result_object['success']==True and result_object['job_status']=='wait' :
        token = result_object['token']
        n=1
        job_status = 'wait'
        while n < 100 and job_status=='wait':
            time.sleep(0.5) 
            print('request:%d'%(n))
            n+=1
            payload = {'action': 'get_result', 'token':token, 'apikey': apikey}
            result = requests.post('https://audiotag.info/api',data=payload)
            print(result.text)
            result_object = json.loads(result.text)
            print(result_object)
            if 'success' in result_object and result_object['success']==True:
                job_status = result_object['result']

    print(time.time() - start_time)
    if (result_object['success']    and 
        not result_object['error'] and
        result_object['result'] == 'found'):
        return '-'.join(result_object['data'][0]['tracks'][0][:-2])
        
    return ''



music_dir = 'rock_album'
i = 0
for file in os.listdir(music_dir):
    if 'Unknown' in file:
        file_name = file[:-4]
        os.system(f"ffmpeg -ss 40 -t 16 -i {os.path.join(music_dir, file)} -ar 8000 -ac 1 -vn {os.path.join(music_dir, file_name + '.wav')}")
        if song := getSongName(music_dir + '/' + file_name + '.wav'):
            song_name = ''
            for s in song:
                if s not in '+=[]:;«,./?\:*?«<>|':
                    song_name += s
            try:
                os.rename(music_dir + '/' + file, music_dir + '/' + song_name + '.mp3')
            except FileExistsError:
                os.rename(music_dir + '/' + file, music_dir + '/' + song_name + str(i) + '.mp3')
                i += 1

            os.remove(music_dir + '/' + file_name + '.wav')
        else:
            continue


    # file_name = file[:-4]
    # os.rename(music_dir + '/' + file, music_dir + '/' + file.replace(' ', '_'))