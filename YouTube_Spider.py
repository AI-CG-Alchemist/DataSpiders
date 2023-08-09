import requests
import json
import os
import re

my_api_key = 'AIzaSyBtbqWG742DzSL0iADOx_07OEkGqLMxwBk'
api_uri = 'https://www.googleapis.com/youtube/v3/'

sun_s = 0
videoKeywords = input('请输入视频关键字,以空格区分(或许英文搜索)：').split()
search = '+'.join(videoKeywords)
num = int(input('最少下载多少部视频：'))
count = 0

requests.packages.urllib3.disable_warnings()

headers = {
    'cookie': 'VISITOR_INFO1_LIVE=9qZVrzB27uI; PREF=f4=4000000&tz=Asia.Shanghai; _ga=GA1.2.621834420.1648121145; _gcl_au=1.1.1853038046.1648121145; NID=511=Zc1APdmEbCD-iqVNVgI_vD_0S3LVI3XSfl-wUZEvvMU2MLePFKsQCaKUlUtchHSg-kWEVMGOhWUbxpQMwHeIuLjhxaslwniMh1OsjVfmOeTfhpwcRYpMgqpZtNQ7qQApY21xEObCvIez6DCMbjRhRQ5P7siOD3X87QX0CFyUxmY; OTZ=6430350_24_24__24_; GPS=1; YSC=0E115KqM_-I; GOOGLE_ABUSE_EXEMPTION=ID=d02004902c3d0f4d:TM=1648620854:C=r:IP=47.57.243.77-:S=YmZXPW7dxbu83bDuauEpXpE; CONSISTENCY=AGDxDeNysJ2boEmzRP4v6cwgg4NsdN4-FYQKHCGhA0AeW1QjFIU1Ejq1j8l6lwAc6c-pYTJiSaQItZ1M6QeI1pQ3wictnWXTOZ6_y8EKlt0Y_JdakwW6srR39-NLuPgSgXrXwtS0XTUGXpdnt4k3JjQ',
    'referer': 'https://www.youtube.com/results?search_query=jk%E7%BE%8E%E5%A5%B3',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
}

def download_video(content, videoname):
    if os.path.exists('./youtube/{videoname}.mp4'):
        return False
    with open(f'./youtube/{videoname}.mp4', 'wb') as open_file:
        open_file.write(content)
    return True

def fecthData(url):
    res = requests.get(url, headers = headers, verify = False)
    return res

def quality(item):
    for i in item:
        # 有些item存储的是音频信息，没有qualitylabel字段，需要判断一下
        if 'qualityLabel' in i.keys():
            if i['qualityLabel'] == '480p':
                return i['url']
            else:
                continue
    for i in item:
        if 'qualityLabel' in i.keys():
            if i['qualityLabel'] == '720p':
                return i['url']
            else:
                continue
    for i in item:
        if 'qualityLabel' in i.keys():
            if i['qualityLabel'] == '1080p':
                return i['url']
            else:
                continue

if __name__ == '__main__':
    baseUrl = f'{api_uri}search?key={my_api_key}&maxResults={num}&part=id&type=video&q={search}'
    Info = json.loads(fecthData(baseUrl).text)
    if not os.path.exists('./youtube'):
        os.mkdir('./youtube')
    for item in Info['items']:
        # 利用youtube的api来获取视频的vid，每个youtube视频对应着一个vid
        vid = item['id']['videoId']
        
        # YouTube视频的地址
        down_url = f'https://www.youtube.com/watch?v={vid}'
        with open('./youtube/lists.txt', 'a') as f:
            f.write(down_url + '\n')


        # 获取视频和对应音频的下载地址
        down_res = requests.get(down_url)
        json_str = (re.findall('var ytInitialPlayerResponse = (.*?),"playerConfig":', down_res.text))[0] + '}'
        json_data = json.loads(json_str)
        video_url = quality(json_data['streamingData']['adaptiveFormats'])
        audio_url = json_data['streamingData']['adaptiveFormats'][-2]['url']
        
        # 获取视频标题并修改
        title = json_data['videoDetails']['title']
        title = title.replace(' ', '')
        title = re.sub(r'[\/:|?*"<>]', '', title)

        #下载视频，将视频拆分为2MB多次下载
        video = requests.get(video_url, stream=True)

        with open(f'./youtube/{title}.mp4', mode='wb') as f:
            for video_chunk in video.iter_content(1024*1024*2):
                f.write(video_chunk)


        
        # print(json.loads(down_res.text))
        # download_video(down_res.content, video_name)
        
    # print(Info)