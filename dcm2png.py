#!/usr/bin/python
#!coding:utf-8
import http.client, json, requests, os
from urllib3 import encode_multipart_formdata
import random, string, time, copy

baseFilePath = 'C:\\Users\\zhaochengxian\\Downloads\\1.2.826.0.1.3680043.2.461.13363721.2266906692\\1.3.12.2.1107.5.1.4.66125.30000022111200052599300075079'

reqheaders = {
	'authority': 'api.products.aspose.app',
	'accept': '*/*' ,
	'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7' ,
	'access-control-request-method': 'POST' ,
	'origin': 'https ://products.aspose.app' ,
	'referer': 'https:products.aspose.app/' ,
	'sec-fetch-dest': 'empty' ,
	'sec-fetch-mode': 'cors' ,
	'sec-fetch-site': 'same-site' ,
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

def preUpload():
	conn=http.client.HTTPSConnection('api.products.aspose.app')	
	conn.request('OPTIONS','/imaging/common/api/Common/UploadFile', '', reqheaders)
	res=conn.getresponse()
	print(res.status)
	print(res.msg)
	print(res.read())

def upload(filePath, fileName, reqId):
	data = {}
	data['file'] = (fileName, open(filePath+'\\'+fileName, 'rb').read())
	data['idUpload'] = reqId
	encode_data = encode_multipart_formdata(data)
	data = encode_data[0]
	header = copy.deepcopy(reqheaders)
	header['Content-Type'] = encode_data[1]
	r = requests.post('https://api.products.aspose.app/imaging/common/api/Common/UploadFile', headers=header, data=data)
	res = r.json();
	print('upload result', res)
	
	return res['IsSuccess']

def getPreviewId(reqId, fileName):
	reqData = {}
	reqData['idMain'] = reqId
	reqData['FileName'] = fileName
	reqData['Application'] = 'Viewer'
	reqData['CurrentPage'] = 1
	reqData['PrevAppName'] = ''
	while True:
		print("req reqData", reqData, reqheaders)
		r = requests.post('https://api.products.aspose.app/imaging/common/api/GetImagePreview', headers=reqheaders, data=reqData)
		if r.text != '':
			print("response:", r.text)
			responseId = json.loads(r.text)['Payload']
			return responseId
		print('retry ... ', r.text)
		time.sleep(3)


def getImgUrl(responseId):
	while True:
		r = requests.get('https://api.products.aspose.app/imaging/common/api/Common/GetStatus?id='+responseId)
		print('getImgUrl response:', r.text)
		if r.text != '':
			res = json.loads(r.text)
			if res['State'] == 'Completed':
				imgUrl = res['Payload']['Pages'][0]['SharedURL']
				print(imgUrl)
				return imgUrl
		print('retry getImgUrl ...')
		time.sleep(3)

def dowloadImg(imgUrl, filePath, fileName):
	response = requests.get(imgUrl, stream = True)
	with open(filePath+'/output/'+fileName+'.png', 'wb') as file:
		for data in response.iter_content(1024):
			file.write(data)
	print('download image success')

def random_str(randomlength=8):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomlength])

# main logic
for dirpath,dirnames,filenames in os.walk(baseFilePath):
	for file in filenames:
		fullpath=os.path.join(dirpath,file)
		print('begin convert:'+fullpath)
		print("preUpload ...")
		preUpload()
		time.sleep(3)
		reqId= 'dc046e0f-2a0a-458a-8018-'+random_str()+str(random.randint(1000, 9999))
		print("upload begin, reqId", reqId)
		upload(dirpath, file, reqId)
		time.sleep(3)
		print('getPreviewId begin ...')
		responseId = getPreviewId(reqId, file)
		time.sleep(3)
		print("getImgUrl ...")
		imgUrl = getImgUrl(responseId)
		time.sleep(3)
		print('dowloadImg ...')
		dowloadImg(imgUrl, baseFilePath, file)
		time.sleep(3)