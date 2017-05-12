# -*- coding: utf-8 -*-
from flask import session,request,jsonify
from flask_login import  login_required 
from app import app,db,models
#from forms import LoginForm,RegistrationForm,InfoForm,EstablishForm,JoinForm,IndexForm
from models import User,Group
#from datetime import datetime
import json
from WXBizDataCrypt import WXBizDataCrypt
import requests
import datetime


def getuserInfo(id):
    getUser=User.query.filter_by(id=id).first()
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
    return allgroupInfo


appId = 'wxe5c697071cafbf44'
appSecret ='e5315816666a005346c0c16aff14b168'

currentId=''

@app.route('/v1.0/login', methods=['POST'])
def login():
    global currentId
    print "------------------"
    print request.json
    
    encryptedData=request.json['encryptedData']
    iv=request.json['iv']
    code=request.json['code']

    #step1:code -> sessionKey
    keyURL= 'https://api.weixin.qq.com/sns/jscode2session?appid='+appId+'&secret='+appSecret+'&js_code='+code+'&grant_type=authorization_code'
    r = requests.post(keyURL)
    print r.json()
    sessionKey=r.json()["session_key"]

    pc = WXBizDataCrypt(appId, sessionKey)
    info= pc.decrypt(encryptedData, iv)
    print info
    print type(info)
    #get info 
    openId= info['openId']
    gender= info['gender']
    nickname=info['nickName']
    avatarUrl=info['avatarUrl']
    print "OK----------------"
    print openId,gender,nickname,avatarUrl
    currentId=openId
    users=User.query.filter_by(id=openId).first()

    if users:
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
    allgroupInfo=getuserInfo(id)
    return json.dumps(allgroupInfo)


@app.route('/v1.0/location', methods=['POST'])
def loaction():
    print "getlocation"
    global currentId
    currentUser=User.query.filter_by(id=currentId).first()
    latitude=request.json['latitude']
    longitude=request.json['longitude']
    if latitude==None or longitude==None:
        return json.dumps(0)
    else:
        currentUser.latitude=latitude
        currentUser.longitude=longitude
        db.session.add(currentUser)
        db.session.commit()
        userInfo={"id":currentUser.id,"nickname":currentUser.nickname,"state":currentUser.state,"gender":currentUser.gender,"avatarUrl":currentUser.avatarUrl,"tel":currentUser.tel,"latitude":currentUser.latitude,"longitude":currentUser.longitude}
        return json.dumps(userInfo)


@app.route('/v1.0/addgroup', methods=['POST'])
def add():
    name=request.json['name']
    id=request.json['userId']
    group=Group(name=name,createTime=datetime.date.today())
    db.session.add(group)
    db.session.commit()
    user=User.query.filter_by(id=id).first()
    user.group.append(group)
    db.session.add(user)
    db.session.commit()
    allgroupInfo=getuserInfo(id)
    return json.dumps(allgroupInfo)


@app.route('/v1.0/joingroup', methods=['POST'])
def join():
    groupId=request.json['gruopId']
    userId=request.json['userId']
    getuser=User.query.filter_by(id=userId).first()
    getgroup=Group.query.filter_by(id=groupId).first()
    getuser.group.append(getgroup)
    db.session.add(getuser)
    db.session.commit()
    allgroupInfo=getuserInfo(userId)
    return json.dumps(allgroupInfo)


@app.route('/v1.0/abortgroup', methods=['POST'])
def abort():
    groupId=request.json['gruopId']
    userId=request.json['userId']
    getuser=User.query.filter_by(id=userId).first()
    getgroup=Group.query.filter_by(id=groupId).first()
    getuser.group.remove(getgroup)
    db.session.add(getuser)
    db.session.commit()
    allgroupInfo=getuserInfo(userId)
    return json.dumps(allgroupInfo)

@app.route('/v1.0/updateuser', methods=['POST'])
def personal():
    id= info['id']
    gender= info['gender']
    nickname=info['nickName']
    avatarUrl=info['avatarUrl']
    tel= info['tel']
    latitude= info['latitude']
    longitude= info['longitude']
    state= info['state']
    getuser=User.query.filter_by(id=id).first()
    user=getuser(gender=gender,nickname=nickname,avatarUrl=avatarUrl,tel=tel,latitude=latitude,longitude=longitude,state=state)
    db.session.add(user)
    db.session.commit()
    userInfo={"id":getuser.id,"nickname":getuser.nickname,"state":getuser.state,"gender":getuser.gender,"avatarUrl":getuser.avatarUrl,"tel":getuser.tel,"latitude":getuser.latitude,"longitude":getuser.longitude}
    return json.dumps(userInfo)



# @app.before_request
# def before_request():
#     g.user = current_user
#     print "=========================="
#     #print current_user.nickname

    # user=User.query.filter_by(nickname=nickname).first()
    # if user:
    #     return jsonify({'nickname':user.nickname})
    # else:
    #     user = User(nickname=nickname)
    #     db.session.add(user)
    #     db.session.commit()
    #     return jsonify({'nickname':user.nickname})
    


"""
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login(): 
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm() 
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user is not None and user.password==form.password.data:
            login_user(user, form.remember_me.data)
            return redirect(url_for('index'))  
        flash(u'密码或用户名错误!')
return render_template('login.html', form=form)
"""
"""
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    role_list=[]
    ren_lenth=0
    form = IndexForm()
    zu = Group.query.filter_by(groupname=form.name.data).first()
    if form.validate_on_submit():
        if zu is None :
            flash(u'此群未建立！')
        else:
             ren_list=zu.user.all()
             ren_lenth=len(ren_list)
             if g.user in ren_list:
                for rens in ren_list:
                    role_list.append(rens.role[0])   
             else:
                flash(u'你不属于该群成员！')
                return redirect(url_for('index'))   
    group_list= g.user.group.all()
    position_list=[]
    name_list=[]
    tel_list=[]
    for role in role_list:
        position_list.append(role.position)
        name_list.append(role.name)
        tel_list.append(role.tel)
    return render_template('index.html',
                           title='Home',
                           form=form,
                           position_list=position_list,name_list=name_list,tel_list=tel_list,role_list=role_list,group_list=group_list,zu=zu,ren_lenth=ren_lenth)

    
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.nickname.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(u'注册成功，请登录！')
        return redirect(url_for('login'))
    if User.query.filter_by(nickname=form.nickname.data).first():
        flash(u'用户名已注册')
    return render_template('register.html', form=form)
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = InfoForm()
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.name.data).first()
        user_role=g.user.role.all()
        if user_role==[]:
            roles= Role(position=form.position.data,name=form.name.data,tel=form.tel.data,author=g.user)
            db.session.add(roles)
            db.session.commit()
            flash(u'信息添加成功！')
        else:
            if role is not None:
                if  g.user.role[0].name==role.name:
                    role.position=form.position.data
                    role.tel=form.tel.data
                    db.session.add(role)
                    db.session.commit()
                    flash(u'信息修改成功！')
                    
                else:
                    flash(u'真实姓名不符，无法修改！') 

            else:
                flash(u'真实姓名不符，无法修改！')

    role_list= models.Role.query.all()
    position_list=[]
    name_list=[]
    tel_list=[]
    positions=[]
    names=[]
    tels=[]
    for role in role_list:
        position_list.append(role.position)
        name_list.append(role.name)
        tel_list.append(role.tel)
    return render_template('edit.html',
                           title='Home',
                           form=form,
                           position_list=position_list,name_list=name_list,tel_list=tel_list,role_list=role_list)


@app.route('/group', methods=['GET', 'POST'])
@login_required
def group():
    form = EstablishForm()
    if form.validate_on_submit():
        l = Group.query.filter_by(groupname=form.name.data).first()
        user_role=g.user.role.all()
        if l is None:
            if user_role==[]:
                 flash(u'请编辑你的信息再创建群组！')
                 return redirect(url_for('group'))
            else:
                group = Group(groupname=form.name.data)
                db.session.add(group)
                db.session.commit()
                g.user.group.append(group)
                db.session.add(g.user)
                db.session.commit()
                flash(u'创建成功,你已是该群成员！') 
        else:
            flash(u'该名称已被占用！')
    return render_template('group.html', form=form)

@app.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    form = JoinForm()
    if form.validate_on_submit():
        s = Group.query.filter_by(groupname=form.name.data).first()
        user_role=g.user.role.all()
        if s is None:
            flash(u'此群未建立')
        else:
            ren_list=s.user.all()
            for ren in ren_list:
                if ren==g.user:
                    flash(u'你在该组群，不需重新加入！')
                    return redirect(url_for('join'))
            else:
                if user_role==[]:
                    flash(u'请先编辑你的信息，再加入群组！')
                    return redirect(url_for('join'))
                else:
                    g.user.group.append(s)
                    db.session.add(g.user)
                    db.session.commit()
                    flash(u'加入成功！')					      
    return render_template('join.html', form=form)

@app.route('/groupinfo', methods=['GET', 'POST'])
@login_required
def groupinfo():
    group_list=g.user.group.all() 
    group_lenth=len(group_list)                                                                                                          
    return render_template('groupinfo.html',group_list=group_list,group_lenth=group_lenth)
	

@app.route('/dele', methods=['GET', 'POST'])
@login_required
def dele():
      form = JoinForm()
      role_list=[]
      zu = Group.query.filter_by(groupname=form.name.data).first()
      if form.validate_on_submit():
          if zu is not None:
                 ren_list=zu.user.all()
                 if g.user in ren_list:
                    for rens in ren_list:
                        role_list.append(rens.role[0])
                    role_list.remove(g.user.role[0])
                    g.user.group.remove(zu)
                    db.session.add(g.user)
                    db.session.commit()
                    flash(u'你已从该群移出！')      
                 else:
                    flash(u'操作无效，你不是该群成员！')
                    return redirect(url_for('dele'))
          else:
            flash(u'请正确输入群名！')
            return redirect(url_for('dele')) 
      return render_template('delete.html',
                           title='Home',
                           form=form,
                           zu=zu)

"""

