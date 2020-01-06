#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 17:34:13 2019

@author: cuiwenzhe
"""
import requests
from hashlib import sha1
import hmac
import xmltodict
import urllib
import numpy as np
import time
from shutil import copyfile
LINE_END = '\n'

iteration_history = 0


def randomArr():
    arr =  np.hstack((np.random.rand(3), #0-2 color
                      2*np.pi*np.random.rand(1), #3 color_dominance:hue
                      (2-0.1)*np.random.rand(1),#4 oil_painting:brush_radius_multiplier
                      (2-0.1)*np.random.rand(1), #5 oil_painting:blur_radius_multiplier
                      np.array(np.random.randint(2)), #6 pointilism
                      100*np.random.rand(1), #7 split_toning:balance
                      360*np.random.rand(1), #8 split_toning:shadow_hue
                      360*np.random.rand(1), #9 split_toning:highlight_hue
                      100*np.random.rand(1), #10 split_toning:shadow_saturation
                      100*np.random.rand(1), #11 split_toning:highlight_saturation
                      20*np.random.rand(1), #12 channel_shift:horizontal_offset
                      20*np.random.rand(1))) #13 channel_shift:vertical_offset
    newArr = []
    
    for i in arr:
        newArr.append(round(i,1))
    return newArr
    
def generateMethodItem(method_order, name, params):
    itemStr = '<method order="' + str(method_order) + '">\n'
    itemStr += '<name>' + name + '</name>\n'
    itemStr += '<params>'
    for i in params:
        itemStr += i + '=' + str(params[i]) + ';'
        
    itemStr += '</params>\n'
    itemStr += '</method>\n'
    return itemStr

arr = [0, 0, 0, 1.2, 34, 23, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
def generateMethodList(bArr):
    method_order = 1
    methodList = ""
    
    name = 'color_dominance'
    params = {'hue': bArr[3],
              'fixed_saturation':0.6}
    methodList += generateMethodItem(method_order, name, params)
    method_order += 1
    
    name = 'oil_painting'
    params = {'brush_radius_multiplier': bArr[4], 'blur_radius_multiplier': bArr[5],}
    methodList += generateMethodItem(method_order, name, params)
    method_order += 1
    
    if(bArr[6] == 1):
        name = 'pointilism'
        params = {}
        methodList += generateMethodItem(method_order, name, params)
        method_order += 1
    
    name = 'split_toning'
    params = {'desaturate':0,
              'balance': bArr[7], 
              'shadow_hue': bArr[8],
              'highlight_hue': bArr[9],
              'shadow_saturation': bArr[10],
              'highlight_saturation': bArr[11]}
    methodList += generateMethodItem(method_order, name, params)
    method_order += 1

    name = 'channel_shift'
    params = {'horizontal_offset': bArr[12], 
              'vertical_offset': bArr[13]}
    methodList += generateMethodItem(method_order, name, params)
    
    return methodList
def generateXML(arr, picUrl):
    #arr = [0, 0, 0, 1.2, 0.3, 1, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
    itemListStr = generateMethodList(arr)
    #print(picUrl)
    xml = '<image_process_call>' + LINE_END + \
        '<image_url>' + picUrl + '</image_url>' + LINE_END + \
        '<methods_list>' + LINE_END + \
        itemListStr + \
        '</methods_list>' + LINE_END + \
        '<result_format>png</result_format>' + LINE_END + \
        '<result_size>600</result_size>' + LINE_END + \
        '</image_process_call>' + LINE_END 
    
    return xml

def sign_request(skey, sraw):
    key = skey.encode()
    raw = sraw.encode()
    encode = hmac.new(key, raw, sha1).hexdigest()

    return encode
 
def sendRequest(imageUrl, arr):
    request_url = 'http://opeapi.ws.pho.to/addtask'
    
    #xml = generateXML("",'http://developers.pho.to/img/girl.jpg')
    #arr = [0, 0, 0, 1.2, 34, 23, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
    xml = generateXML(arr,imageUrl)
    #print(xml)
    key = '3094bb2eb5e165571d67113d77604819' #key Lucas
    app_id = '9483a8a6e99da624fb91726441c64d91' #key Lucas
    
    mParams = {
            'app_id': app_id,
            'key': key,
            'data': xml,
            'sign_data': sign_request(key, xml)
            }
    
 
    head={"Content-Type":"text/xml; charset=UTF-8", 'Connection': 'close'}
   
    r = requests.post(request_url, params = mParams, headers=head)
    
    responsedata=r.text
    #print(responsedata)
    #print("get the status: ",r.status_code)
    return responsedata, r.status_code;
 
def getResultUrl(requestID):
    
    response_url = "http://opeapi.ws.pho.to/getresult?request_id=" + requestID
    key = '3094bb2eb5e165571d67113d77604819'
    app_id = '9483a8a6e99da624fb91726441c64d91'
    mParams = {
            'app_id': app_id,
            'key': key,
            }
    
 
    head={"Content-Type":"text/xml; charset=UTF-8", 'Connection': 'close'}
    

        
    count = 0
    while(count<40):
        r = requests.get(response_url, params = mParams, headers=head)
        responsedata=r.text
        #print(responsedata)
        #print("get the status: ",r.status_code)
    
        resultDict = xmltodict.parse(responsedata)['image_process_response']
        if 'result_url' in resultDict:
            return resultDict['result_url']
        else:
            print('wait',count)
            time.sleep(0.5)
        count += 1
    return ""


def sendImage(url, arr):
    global iteration_history
    xml, code = sendRequest(url, arr)
    if code == 200:
        print('success')
    else:
        print('fail')
        return ""
    d = xmltodict.parse(xml)
    requestID = d['image_process_response']['request_id']

    #print(requestID)
    print("data: http://opeapi.ws.pho.to/getresult?request_id=" + requestID)
    responseUrl = getResultUrl(requestID)
    #print(responseUrl)
    if responseUrl != "":
        urllib.request.urlretrieve(responseUrl, "current.jpg")
        if(iteration_history%2 != 0):
            copyfile("current.jpg", str(iteration_history)+".jpg")
        iteration_history += 1

    else:
        print('fail to get image in 20 seconds')
    return responseUrl
#%%


#%%
'''
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#arr = [0, 0, 0, 7.2, 1, 0.3, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
arr = [0, 0, 0, 1.2, 0.3, 1, 0, 66, 23, 43, 12, 23, 12, 12 ,11]
arr = randomArr()
print(arr)
sendImage(picUrl, arr)

img=mpimg.imread('current.jpg')
imgplot = plt.imshow(img)
plt.show()
'''    








