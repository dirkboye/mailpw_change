#!/usr/bin/env python2.7
import cgi
import cgitb; cgitb.enable()
import pwd, sys, os, cdb, subprocess
from subprocess import check_output,Popen,PIPE

home_dir="/home/XXXUSERXXX"

def check_form(formvars, form):
	for varname in formvars:
	    if varname not in form.keys():
	        return 'All fields have to filled.'
	    else:
        	if type(form[varname].value) is not type(''):
	            return 'Invalid data type.'
	return ''

def check_oldpw(accountname, oldpw):
	passwd_dbfile=os.path.abspath(home_dir+"/passwd.cdb");
	try:
		db=cdb.init(passwd_dbfile)
	except:
		return 'No user database found.'
	try:
		cdb_user_data=db[accountname]
	except:
		return 'User not found.'
	passhash=cdb_user_data[6:40]
	# Hash algorithm is given between first two $ of passhash (here only md5 based BSD password is used)
	hashtype='1'
	# Salt is given between next two $
	salt=passhash[3:11]
	opensslargs = ['openssl', 'passwd', '-'+hashtype, '-salt', salt, oldpass];
	newhash = check_output(opensslargs).strip();
	if newhash == passhash:
		return ''
	return 'Wrong password'

formvars = ['accountname', 'oldpass', 'newpass', 'newpass2']
form = cgi.FieldStorage()
if check_form(formvars, form) == '':
	accountname = form['accountname'].value
	oldpass = form['oldpass'].value
	newpass = form['newpass'].value
	newpass2 = form['newpass2'].value
	if newpass == newpass2:
		if check_oldpw(accountname, oldpass) == '':
			vpasswdargs = ['vpasswd', accountname]
			# Environmental variable HOME is needed for vpasswd to work
			os.environ['HOME'] = home_dir	
			p = Popen(vpasswdargs, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)	
			p.stdin.write(newpass+'\n')
			p.stdin.write(newpass2+'\n')
			p.stdin.close()
			if p.wait() == 0:
				message = 'Password changed'
			else:
				message = 'Error changing password: ' + p.stdout.read()
		else:
			message = check_oldpw(accountname, oldpass)
	else:
		message = 'New passwords not matching!'
else:
	message = check_form(formvars, form)

print """\
Content-Type: text/html\n
<html><body>
%s
</body></html>
""" % message
