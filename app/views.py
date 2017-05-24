# -*- coding: utf-8 -*-
from flask import session,request
# from flask_login import  login_required 
from app import app,db,models
from models import User,Group,Inspect
import datetime
import json
from WXBizDataCrypt import WXBizDataCrypt
import requests
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
    # print openId,gender,nickname,avatarUrl
    currentId=openId
    print currentId
    users=User.query.filter_by(id=openId).first()
    print "==============="
    print nickname
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
    print id 
    getUser=User.query.filter_by(id=id).first()
    # print getUser.nickname 
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
    global currentId
    currentUser=User.query.filter_by(id=currentId).first()
    latitude=request.json['latitude']
    longitude=request.json['longitude']
    if latitude==None or longitude==None:
        return json.dumps("没有定位该用户")
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
            return json.dumps("群主不能退群")
        else:
            getuser.group.remove(getgroup)
            db.session.add(getuser)
            db.session.commit()
            Group.query.filter_by(id=groupId).delete()
            db.session.commit()
            return json.dumps("退群成功")

    else:
        getuser.group.remove(getgroup)
        db.session.add(getuser)
        db.session.commit()
        return json.dumps("退群成功")

@app.route('/v1.0/updateuser', methods=['POST'])
def personal():
    id= request.json['id']   
    # nickname=request.json['nickname']
    # avatarUrl=request.json['avatarUrl']
    # latitude= request.json['latitude']
    # longitude= request.json['longitude']
    tel=request.json['tel']
    state= request.json['state']
    print "+++++++++++++++"
    print "tel:",tel
    print "state:",state
    getuser=User.query.filter_by(id=id).first()
    if getuser:
        getuser.tel=tel
        getuser.state=state
        # user=getuser(tel=tel,state=state)
        db.session.add(getuser)
        db.session.commit()
        userInfo={"id":getuser.id,"nickname":getuser.nickname,"state":getuser.state,"gender":getuser.gender,"avatarUrl":getuser.avatarUrl,"tel":getuser.tel,"latitude":getuser.latitude,"longitude":getuser.longitude}
        return json.dumps(userInfo)
    else:
        return json.dumps("没有找到该用户")

@app.route('/v1.0/addrequest', methods=['POST'])
def apply():
    """
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
                return json.dumps(creater.nickname)
            else:
                # inspect.time=time.strptime('%Y-%m-%d',time.localtime(time.time()))
                # db.session.add(inspect)
                # db.session.commit()
                # return json.dumps(creater.nickname)
                return json.dumps("您的请求等待确认")
        else:
            return json.dumps("操作无效，你已经是该群成员")
    else:
        return json.dumps("未找到该群组")

@app.route('/v1.0/request/<id>', methods=['GET'])
def query(id):
    """
    接受用户id，判断该用户所创群组有无申请者请求记录
    若有返回 inspectsInfo，若无返回0
    """
    inspect=Inspect.query.filter_by(createrid=id).all()
    if inspect: 
        inspectInfo=[]
        for inspects in inspect:
            requester= User.query.filter_by(id=inspects.userid).first()
            inspectsInfo={'id':inspects.id,'groupid':inspects.groupid,'nickname':requester.nickname,'avatarUrl':requester.avatarUrl}
            inspectInfo.append(inspectsInfo)
        return json.dumps(inspectInfo)
    else:
        return json.dumps("")

@app.route('/v1.0/joingroup', methods=['POST']) 
def join():
    """
    接受inspect的id和agree通过一些判断后再决定
    对请求者的请求做处理
    """
    id=request.json['requestId'] 
    agree=request.json['agree']
    # print type(agree)
    # print "------------"
    # print id
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

