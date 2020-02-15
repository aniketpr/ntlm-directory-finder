import concurrent.futures
import requests
from requests_ntlm import HttpNtlmAuth
from getpass import getpass
import threading
import optparse
import time
import sys, traceback

print('''
███╗   ██╗████████╗██╗     ███╗   ███╗      ██████╗ ██╗██████╗ ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
████╗  ██║╚══██╔══╝██║     ████╗ ████║      ██╔══██╗██║██╔══██╗██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
██╔██╗ ██║   ██║   ██║     ██╔████╔██║█████╗██║  ██║██║██████╔╝█████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██║╚██╗██║   ██║   ██║     ██║╚██╔╝██║╚════╝██║  ██║██║██╔══██╗██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚████║   ██║   ███████╗██║ ╚═╝ ██║      ██████╔╝██║██║  ██║██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝     ╚═╝      ╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝                                                                                                          
''')

def get_argument():
	parser=optparse.OptionParser()
	parser.add_option("-w","--wordlist",dest="wordlist",help="Add Wordlist")
	parser.add_option("-u","--username",dest="username",help="Add Username")
	parser.add_option("-t","--target",dest="target",help="Add Target")
	parser.add_option("-d","--domain",dest="domain",help="Add Domain")
	# parser.add_option("-r","--recursive",dest="recursive",help="For Recursive Search")
	parser.add_option("-c","--thread",dest="thread",help="Add Thread")
	parser.add_option("-o","--output",dest="output",help="Output Path")
	(options,arguments) = parser.parse_args()
	if not options.wordlist:
		parser.error("[-] Specify an wordlist Or --help for more details")
	elif not options.username:
		parser.error("[-] Specify an username Or --help for more details ")
	elif not options.target:
		parser.error("[-] Specify an target Or --help for more details ")
	elif not options.domain:
		parser.error("[-] Specify an domain Or --help for more details ")	
	return options

options = get_argument()

password = getpass()

def checkpassword():
	response = requests.get(options.target,auth=HttpNtlmAuth('{}\\{}'.format(options.domain,options.username),password))
	if response.status_code == 401:
		print("401 - Unauthorized: Access is denied due to invalid credentials.")
		exit()

checkpassword()

words = []
with open(options.wordlist, 'r',encoding="utf8") as file:
	a = file.readlines()
	for i in a:
		words.append(i.strip())

threads = []

def scan(word):
	url = options.target+'/'+word
	session = requests.Session()
	session.auth = HttpNtlmAuth('{}\\{}'.format(options.domain,options.username),password)
	response = session.get(url)
	if response.status_code == 200:
		print(url)
		if options.output:
			with open("{}".format(options.output), 'a') as f:
				f.write(url+"\n")
		# if options.recursive:
		# 	scan(url)
	else:
		print('/'+word,end="\r")

if options.thread:
	thread_count = int(options.thread)
else:
	thread_count = 10

try:
	with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
	    executor.map(scan, words)
except KeyboardInterrupt:
	print("Shutting down..........................")
