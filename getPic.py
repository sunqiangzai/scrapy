# -*- coding: utf-8 -*-
"""
Spyder Editor

chingswy

python 爬取cc98指定版块的帖子图片
"""
import requests
import hashlib
import re
import os
import time

IM_RE = re.compile(r'http://file.cc98.org/uploadfile(.+?)\[/upload\]')
TOPIC_RE = re.compile(r'href="dispbbs.asp\?(.+?)&page=')

def login(url='http://www.cc98.org/sign.asp',user = 'chingswy',passwd = '*********'):
    '''
    使用用户名和密码进行登陆
    '''
    #对密码进行md5加密    
    passmd = hashlib.md5(passwd.encode()).hexdigest()
    #登陆提交的数据
    DATA = {'a':"i",'u':user,'p':passmd,'userhidden':"1"}
    #实例化一个session对象    
    s = requests.session()
    #post 登录的地址，提交数据
    res = s.post('http://www.cc98.org/sign.asp',data=DATA)
    if res.text == '9898':
        print('登陆成功')
        #这里没有判断登陆不成功的状态
        #其他返回值比如密码错误等的状态也没有判断
    return s
        
def getTopic(session,boardid = 146,pages = 5):
    '''
    获取板块中前pages页的帖子地址
    '''
    topicUrl = []
    for pagenum in range(1,pages+1):
        print('正在获取第%d页的帖子列表'%pagenum)
        #构造URL参数
        DATA = {'boardid':str(boardid),'page':str(pagenum),'action':''}
        #获取页面
        page = session.get('http://www.cc98.org/list.asp',params = DATA)
        #寻找帖子链接
        topicList = list(map(lambda x:\
        'http://www.cc98.org/dispbbs.asp?'+x,TOPIC_RE.findall(page.text)))
        # 扩充到列表中
        topicUrl.extend(topicList)
    return topicUrl
        
def getImg(session,topic):
    '''
    获取指定帖子里的图片列表
    '''
    r = session.get(topic);
    print('正在获取帖子%s的图片列表'%topic)
    # 将图片去重
    fileList = list(set(IM_RE.findall(r.text)))
    # 拼接出完整的图片地址
    return [r'http://file.cc98.org/uploadfile'+i for i in fileList]

def saveImg(img):
    '''
    下载图片
    '''
    print('正在下载图片',img)
    ir = requests.get(img)
    if ir.status_code == 200:# 如果成功返回
        filename = img[-13:] # 切片生成图片名字
        with open(filename,'wb') as f:
            f.write(ir.content)
            #保存图片
    # 网络异常情况没有处理

def readSet(logName):
    '''
    读取保存的日志文件
    返回文件中内容的集合
    '''
    try:
        print('正在读取日志文件',logName)
        with open(logName,'r') as f:
            topic = f.read()
            topicSetHis = set(topic.split('\n'))
        
    except:
        print('正在生成日志文件',logName)
        with open(logName,'a') as f:
            pass
        topicSetHis = set()
    finally:
        return topicSetHis

def saveSet(topicAdd,logName = 'topicHis.log'):
    # 保存日志
    with open(logName,'a') as f:
        for topic in topicAdd:
            f.write(topic)
            f.write('\n')
            
if __name__ == '__main__':
    PATH = 'img'
    url='http://www.cc98.org/sign.asp'
    user = input('输入用户名：')
    passwd = input('输入密码:')
    try:
        os.mkdir(PATH)
    except:
        pass
    os.chdir(PATH)
    session = login(url,user,passwd)
    
    imgSet = readSet('imgDownloaded.log')
    imgList = readSet('imgList.log')
    if len(imgSet) >= len(imgList):
        print('更新图片列表中')
        imgList = []
        ####################################
        # get topic
        topicSet = readSet('topicHis.log')
        currentTopic = getTopic(session,boardid=146,pages=200)
        topicUndetected = set(currentTopic) - topicSet
        topicDetected = []
        try:
            for topic in topicUndetected:
                imgList.extend(getImg(session,topic))
                topicDetected.append(topic)
        finally:
            saveSet(topicUndetected)
    imgUndown = set(imgList) - imgSet
    imgDown = []
    try:
        for img in imgUndown:
            try:
                saveImg(img)
                time.sleep(0.1)
                imgDown.append(img)
            finally:
                pass
    finally:
        saveSet(set(imgList)|imgSet,'imgList.log')
        saveSet(imgDown,'imgDownloaded.log')
