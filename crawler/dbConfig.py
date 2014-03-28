import psycopg2
import sys
import time

con = None

def start_DB():
	global con

	try:
		con = psycopg2.connect(database='github', user='github_dev', password='github_dev_pass')

	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)


def stop_DB(con):
	if con:
		con.close()

def get_user_names():
	global con 

	if (not con):
		start_DB()

	cur = con.cursor()

	for i in range(8):
		num = 10**i
		start = time.time()
		get_users = "SELECT username FROM repository GROUP BY username LIMIT " + str(num) + ";"
		cur.execute(get_users)
		userlist = cur.fetchall()
		end = time.time()
		print "i: ", i, " delta: ", end-start


get_user_names()