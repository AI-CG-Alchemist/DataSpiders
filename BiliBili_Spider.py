import os
import json
import subprocess
from lxml import etree
from bs4 import BeautifulSoup
import requests
import time
import random


# 关闭非https报错
requests.packages.urllib3.disable_warnings()

# 搜索关键词/此次视频爬取存储目录/爬取文件数量
prompt = ''
destFolder = ''
num = 0

# 反防爬取
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
    'Referer': 'https://search.bilibili.com',
    # 需要去首页寻找填一下
    'Cookie': "buvid3=C7BB5835-3168-999D-D869-00DD2070B75310927infoc; b_nut=1690463110; _uuid=E38292410-BC93-7D6A-10BA8-CD98E610A6A6310147infoc; buvid4=70A5848B-AAC5-290C-B20F-4536AE00247118866-023072721-hMsvJD35An8mLG1L9vVCPw%3D%3D; CURRENT_FNVAL=4048; i-wanna-go-back=-1; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; nostalgia_conf=-1; rpdid=|(u)YRJ)JJ|k0J'uYm|~~Jk~l; buvid_fp_plain=undefined; fingerprint=e9a753c5f26689a80d2fbe61f16e87b4; PVID=1; buvid_fp=e9a753c5f26689a80d2fbe61f16e87b4; DedeUserID=479496467; DedeUserID__ckMd5=08b57da3bdbc65d8; b_ut=5; SESSDATA=5980aa37%2C1707457625%2C350e8%2A82OpbT7oqOzMjiSiO7sJkdG62VPtXuP3tZp8SiOQ59Hy6cw3NtkAMb_Jw3sWT9wlzbMBUGGQAAQwA; bili_jct=e288bfe06dd29bbe0e1141646b2dd5da; bili_ticket=eyJhbGciOiJFUzM4NCIsImtpZCI6ImVjMDIiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE2OTIxNjQ4MzUsImlhdCI6MTY5MTkwNTYzNSwicGx0IjotMX0.LzaBwfZFsKLM_1rI5WmCB7IGty-n4L-a_41QM7jA3wz1hgQQDViFmSBZCkdKElIBioY3Kebe-CbEQ79wQo_94rRVjtIOtCj0ts46pyjBRsEdBkyKLD9lCr0fzBil7Au2; bili_ticket_expires=1692164835; sid=8fx6aod6; b_lsid=43BA91D7_189EDCC74BC; bp_video_offset_479496467=829244806335037457; CURRENT_QUALITY=80; innersign=0; home_feed_column=4; browser_resolution=718-659"
}


def solve():
    # 首先获取共搜寻视频数量
    baseURL = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&duration=1&keyword='+prompt
    data = fetchData(baseURL)["data"]
    page_num = data['numPages']
    video_num = data['numResults']

    if page_num <= 0:
        print("未找到任何相关信息")
        return
    else:
        print("此次搜索共搜寻到"+str(video_num)+"条视频数据")

    page = 0
    index = 0
    # 逐页下载视频
    while page < page_num:
        page += 1
        url = baseURL+"&page="+str(page)
        data = fetchData(url)["data"]
        video_list = data["result"]
        for v in video_list:
            index += 1
            link = v['arcurl']
            bv = v['bvid']
            print("视频访问地址:"+link)  # debug
            print("视频bv号:"+bv)  # debug
            getBiliBiliVideo(link, bv, index)
            if index >= min(num, video_num):
                return
        # 当爬取视频数量很多时开启防止频繁请求封ip
        # secs = random.normalvariate(1, 0.4)
        # if(secs <= 0):
        #     secs = 1
        # time.sleep(secs)


''' 封装请求函数'''


def fetchData(url):
    data = requests.get(url=url, headers=headers, verify=False).json()
    return data


''' 根据bv号获取某一个视频'''


def getBiliBiliVideo(link, bv, index):
    session = requests.session()
    headers.update({'Referer': 'https://www.bilibili.com/'})
    res = session.get(url=link, headers=headers, verify=False)
    _element = etree.HTML(res.content)

    videoPlayInfo = str(_element.xpath(
        '//head/script[3]/text()')[0].encode('utf-8').decode('utf-8'))[20:]

    videoJson = json.loads(videoPlayInfo)
    try:
        flag = 0
    except Exception:
        # videoURL = videoURL = videoJson['data']['durl'][0]['url']
        print("早期视频暂时不提供下载！")
        return

    dirName = destFolder.encode("utf-8").decode("utf-8")
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        # print("存储点创建成功") #debug

    print("正在下载第"+str(index)+"个视频："+bv+"....")
    if flag == 0:
        videoURL = videoJson['data']['dash']['video'][0]['baseUrl']
        print("视频下载地址:"+videoURL)  # debug
        videoPath = dirName + "/"+"TMP_"+str(index)+"-"+bv+"_Video.mp4"
        fileDownload(link=link, url=videoURL,
                     path=videoPath, session=session)
        audioURL = videoJson['data']['dash']['audio'][0]['baseUrl']
        print("音频下载地址:"+audioURL)  # debug
        audioPath = dirName + "/"+str(index)+"-"+bv+"_Audio.mp3"
        fileDownload(link=link, url=audioURL, path=audioPath, session=session)
        outPath = dirName + "/"+str(index)+"-"+bv+"_Video.mp4"
        print("文件存储地址:"+outPath)  # debug
        combineVideoAudio(videoPath, audioPath, outPath)
    print("第"+str(index)+"个视频下载完成")


'''合并视频与音频'''


def combineVideoAudio(videoPath, audioPath, outPath):
    subprocess.call(("ffmpeg -i " + videoPath +
                    " -i " + audioPath + " -c copy " + outPath).encode("utf-8").decode("utf-8"), shell=True)
    os.remove(videoPath)
    os.remove(audioPath)


''' 分段下载视频更加稳定'''


def fileDownload(link, url, path, session=requests.session()):
    headers.update({'Referer': link, "Cookie": ""})
    session.options(url=link, headers=headers, verify=False)
    begin = 0
    end = 1025*512-1
    flag = 0
    while True:
        headers.update({'Range': 'bytes=' + str(begin) + '-' + str(end)})

        # 获取视频分片
        res = session.get(url=url, headers=headers, verify=False)
        if res.status_code != 416:
            # 响应码不为为416时有数据
            begin = end + 1
            end = end + 1024*512
        else:
            headers.update({'Range': str(end + 1) + '-'})
            res = session.get(url=url, headers=headers, verify=False)
            flag = 1
        with open(path.encode("utf-8").decode("utf-8"), 'ab') as fp:
            fp.write(res.content)
            fp.flush()
        if flag == 1:
            fp.close()
            break


if __name__ == '__main__':
    # 爬取时运行这个
    # destFolder = input("请输入视频集存储点(如result/dest):")
    # prompt = input("请输入搜索关键词:")
    # num = input("请输入下载文件数量:")

    # 测试用
    destFolder = "result"
    prompt = "马斯克采访"
    num = 5

    solve()
