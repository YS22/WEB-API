# -*- coding: utf-8 -*-
from flask import session,request
# from flask_login import  login_required 
from app import app,db,models
from models import User,Group,Inspect
import datetime
import json
from WXBizDataCrypt import WXBizDataCrypt
import requests
import threading
# import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


appId = 'wxe5c697071cafbf44'
appSecret ='e5315816666a005346c0c16aff14b168'
currentId=''

@app.route('/v1.0/login', methods=['POST'])
def login():
	global currentId
	# print "------------------"
	# print request.json
	
	encryptedData=request.json['encryptedData']
	iv=request.json['iv']
	code=request.json['code']

	#step1:code -> sessionKey
	keyURL= 'https://api.weixin.qq.com/sns/jscode2session?appid='+appId+'&secret='+appSecret+'&js_code='+code+'&grant_type=authorization_code'
	r = requests.post(keyURL)
	sessionKey=r.json()["session_key"]

	pc = WXBizDataCrypt(appId, sessionKey)
	info= pc.decrypt(encryptedData, iv)
	openId= info['openId']
	gender= info['gender']
	nickname=info['nickName']
	avatarUrl=info['avatarUrl']
	print " login OK----------------"
	print  threading.current_thread().getName
	print openId,nickname
	currentId=openId
	# print currentId
	users=User.query.filter_by(id=openId).first()
	if users:
		users.nickname=nickname
		users.avatarUrl=avatarUrl
		# user=users(nickname=nickname,avatarUrl=avatarUrl)
		db.session.add(users)
		db.session.commit()
		userInfo={"id":users.id,"nickname":users.nickname,"state":users.state,"gender":users.gender,"avatarUrl":users.avatarUrl,"tel":users.tel,"latitude":users.latitude,"longitude":users.longitude}
		return json.dumps(userInfo)
	else:
		user=User(id=openId,gender=gender,nickname=nickname,avatarUrl=avatarUrl)
		db.session.add(user)
		db.session.commit()
		userInfo={"id":users.id,"nickname":users.nickname,"state":users.state,"gender":users.gender,"avatarUrl":users.avatarUrl,"tel":users.tel,"latitude":users.latitude,"longitude":users.longitude}
		return json.dumps(userInfo)

@app.route('/v1.0/groups/<id>', methods=['GET'])
#@login_required
def group(id):
	getUser=User.query.filter_by(id=id).first()
	print "get groups ====================="
	print  threading.current_thread().getName
	print getUser.nickname 
	if getUser:
		groupList=getUser.group.all()
		allgroupInfo=[]
		for groups  in groupList:
			groupsAlluser=groups.user.all()
			users=[]
			for userInfo in groupsAlluser:
				getuserInfo={}
				getuserInfo={"id":userInfo.id,"nickname":userInfo.nickname,"state":userInfo.state,"gender":userInfo.gender,"avatarUrl":userInfo.avatarUrl,"tel":userInfo.tel,"latitude":userInfo.latitude,"longitude":userInfo.longitude}
				users.append(getuserInfo)
			groupsInfo={}
			groupsInfo={"id":groups.id,"name":groups.name,"createTime":str(groups.createTime),"users":users}
			allgroupInfo.append(groupsInfo)
		return json.dumps(allgroupInfo)
	else:
		return json.dumps("没有找到该用户")

@app.route('/v1.0/location', methods=['POST'])
def loaction():
	#global currentId
	id=request.json['id']
	currentUser=User.query.filter_by(id=id).first()
	print "location user ========================"
	print currentUser.nickname
	latitude=request.json['latitude']
	longitude=request.json['longitude']
	if latitude==None or longitude==None:
		return json.dumps("没有定位该用户")
	else:
		currentUser.latitude=latitude
		currentUser.longitude=longitude
		db.session.add(currentUser)
		db.session.commit()
		# userInfo={"id":currentUser.id,"nickname":currentUser.nickname,"state":currentUser.state,"gender":currentUser.gender,"avatarUrl":currentUser.avatarUrl,"tel":currentUser.tel,"latitude":currentUser.latitude,"longitude":currentUser.longitude}
		# return json.dumps(userInfo)
		return json.dumps("")


@app.route('/v1.0/addgroup', methods=['POST'])
def add():
	name=request.json['name']
	createrid=request.json['userId']
	group=Group(name=name,createTime=datetime.datetime.now(),createrId=createrid)
	db.session.add(group)
	db.session.commit()
	user=User.query.filter_by(id=createrid).first()
	user.group.append(group)
	db.session.add(user)
	db.session.commit()
	return json.dumps("创建成功，你已成为群主")

@app.route('/v1.0/abortgroup', methods=['POST'])
def abort():
	groupId=request.json['groupId']
	userId=request.json['userId']
	getuser=User.query.filter_by(id=userId).first()
	getgroup=Group.query.filter_by(id=groupId).first()
	if userId==getgroup.createrId:
		userlist=getgroup.user.all()
		if len(userlist)>1:
			return json.dumps("用户大于一个时，创建者不能退群")
		else:
			getuser.group.remove(getgroup)
			db.session.add(getuser)
			db.session.commit()
			Group.query.filter_by(id=groupId).delete()
			db.session.commit()
			return json.dumps("退出通讯群成功！")

	else:
		getuser.group.remove(getgroup)
		db.session.add(getuser)
		db.session.commit()
		return json.dumps("退出通讯群成功！")

@app.route('/v1.0/updateuser', methods=['POST'])
def personal():
	id= request.json['id'] 
	tel=request.json['tel']
	state= request.json['state']
	print "+++++++++++++++"
	print "tel:",tel
	print "state:",state
	if id:
		getuser=User.query.filter_by(id=id).first()
		print getuser.nickname
		# nickname=request.json['nickname']
		# avatarUrl=request.json['avatarUrl']
		# latitude= request.json['latitude']
		# longitude= request.json['longitude']
		if getuser:
			getuser.tel=tel
			getuser.state=state
			db.session.add(getuser)
			db.session.commit()
			# userInfo={"id":getuser.id,"nickname":getuser.nickname,"state":getuser.state,"gender":getuser.gender,"avatarUrl":getuser.avatarUrl,"tel":getuser.tel,"latitude":getuser.latitude,"longitude":getuser.longitude}
			# return json.dumps(userInfo)
			return json.dumps("修改成功")
		else:
			return json.dumps("没有找到该用户")
	else:
		return json.dumps("")

@app.route('/v1.0/addrequest', methods=['POST'])
def apply():
	"""
	加入群组申请：
	接受请求者id和请求者要加入群组id，首先判断该群是否存在，若存在，再判断该请求者是否已经在
	该群，若不在，再判断该用户之前有无加入该群申请记录，若没有则创建申请，反之更新申请时间
	"""
	groupId= request.json['groupId']
	userId= request.json['userId']
	
	# groupId= request.json['groupId']
	# userId= request.json['userId']
	# print "==========+======="
	# print groupId 
	groups=Group.query.filter_by(id=groupId).first()
	if groups:
		user=User.query.filter_by(id=userId).first()
		usergroup=user.group.all()
		if groups not in usergroup:
			creater=User.query.filter_by(id=groups.createrId).first()
			inspect=Inspect.query.filter_by(groupid=groupId,userid=userId).first()
			if not inspect:
				inspect=Inspect(groupid=groupId,userid=userId,time=datetime.datetime.now(),createrid=groups.createrId)
				db.session.add(inspect)
				db.session.commit()
				return json.dumps("申请成功")
			else:
				return json.dumps("已提交申请")
		else:
			return json.dumps("你已经是该通讯群成员")
	else:
		return json.dumps("未找到该通讯群")

@app.route('/v1.0/request/<id>', methods=['GET'])
def query(id):
	"""
	个人信息及群组申请展示：
	接受用户id，判断该用户所创群组有无申请者请求记录
	若有返回 inspectsInfo，若无返回0
	"""
	inspectCheck=Inspect.query.filter_by(createrid=id).all() #as check
	inspectApply=Inspect.query.filter_by(userid=id).all() #as apply

	if inspectCheck or inspectApply:

		inspectCheckInfo=[]
		for inspects in inspectCheck:
			groupname=Group.query.filter_by(id=inspects.groupid).first().name
			requester= User.query.filter_by(id=inspects.userid).first()
			CheckInfo={'id':inspects.id,'groupid':inspects.groupid,'groupName':groupname,'nickname':requester.nickname,'avatarUrl':requester.avatarUrl}
			inspectCheckInfo.append(CheckInfo)

		inspectApplyInfo=[]
		for inspects in inspectApply:
			groupname=Group.query.filter_by(id=inspects.groupid).first().name
			creater= User.query.filter_by(id=inspects.createrid).first()
			ApplyInfo={'id':inspects.id,'groupid':inspects.groupid,'groupName':groupname,'nickname':creater.nickname,'avatarUrl':creater.avatarUrl}
			inspectApplyInfo.append(ApplyInfo)

		allInfo={"check":inspectCheckInfo,"apply":inspectApplyInfo}
		return json.dumps(allInfo)
	else:
		return json.dumps("")

@app.route('/v1.0/joingroup', methods=['POST']) 
def join():
	"""
	加入群组：
	接受inspect的id和agree通过一些判断后再决定
	对请求者的请求做处理
	"""
	id=request.json['requestId'] 
	agree=request.json['agree']
	inspect=Inspect.query.filter_by(id=id).first()   
	if inspect:
		if agree==1:
			getuser=User.query.filter_by(id=inspect.userid).first()
			getgroup=Group.query.filter_by(id=inspect.groupid).first()
			getuser.group.append(getgroup)
			db.session.add(getuser)
			db.session.commit()
			Inspect.query.filter_by(id=id).delete()
			db.session.commit()
			return json.dumps("已同意加入")
		else:
			Inspect.query.filter_by(id=id).delete()
			db.session.commit()
			return json.dumps("已拒绝加入")
	else:
		return json.dumps("")


@app.route('/v1.0/nineusers/<id>', methods=['GET']) 
def nineuser(id):
	"""
	搜索群组信息：服务器接受groupid，判断有无该群组，有则返回前9人部分信息，
	否则返回未找到该群组
	"""
	group=Group.query.filter_by(id=id).first()
	
	if group:
		nineuser=group.user.all()[0:9]
		nineuserInfo=[]
		for user in nineuser:
			userInfo={'nickname':user.nickname,'avatarUrl':user.avatarUrl}
			nineuserInfo.append(userInfo)
		return json.dumps(nineuserInfo)
	else:
		return json.dumps("")
