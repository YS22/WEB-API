from fabric.api import *
env.hosts =['47.93.103.136']
env.user = 'root'
env.password ='1234pttK'

def deploy ():
	with cd('/srv/WEB-API'):
		run('git pull')
		sudo('supervisorctl restart webapi')
		sudo('supervisorctl status')