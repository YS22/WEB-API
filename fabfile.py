from fabric.api import *
env.hosts =['120.24.156.188']
env.user = 'root'
env.password ='112358Ys'

def deploy ():
	with cd('/srv/WEB-API'):
		run('git pull')
		#run('../bin/supervisorctl restart mate')
		#run('../bin/supervisorctl status')