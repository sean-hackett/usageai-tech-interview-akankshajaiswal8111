import sys
import boto3
import mysql.connector
import os
import hashlib, uuid
import streamlit as st
import requests
import json


ENDPOINT="usageai-users.cna5xveywog4.us-east-1.rds.amazonaws.com"
PORT="3306"
USR="admin"
REGION="us-east-1"
DBNAME="usageai_db"
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

client = boto3.client('rds', region_name=REGION)


conn =  mysql.connector.connect(host=ENDPOINT, user=USR, passwd="admin123", port=PORT, database=DBNAME)
cur = conn.cursor()


def add_user_to_db(new_user):

	cur.execute('INSERT INTO userstable(email,password,dob,firstName,lastName) VALUES (%s,%s, %s, %s, %s)',(new_user['email'],make_hashes(new_user['password']),new_user['dob'],new_user['firstName'],new_user['lastName']))
	conn.commit()
    

def get_test_user():
    response = requests.get('https://randomuser.me/api/?seed=usageai')
    #response = requests.get('http://api.randomuser.me/?format=json&?nat=gb')
    print(response)
    results = json.loads(response.text)

    results = results['results'][0]
    name = results['name']
    first = name['first']
    last = name['last']
    email = results['email']
    dob = results['dob']['date']
    login = results['login']
    password = login['password']

    new_user = {"firstName":first,"lastName":last,"email":email,"password":password,"dob":dob}
    print(new_user)

    return new_user


def add_number_of_users(number_of_users=1):
    for i in range(number_of_users):
        new_user = get_test_user()
        add_user_to_db(new_user)
        print(i)


def make_hashes(password):
	salt = uuid.uuid4().hex
	return hashlib.sha256(str.encode(password+salt)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False


def login_user(email,password):

	cur.execute('SELECT * FROM userstable WHERE email =%s AND password = %s',(email,password))
	data = cur.fetchall()
	return data


def main():
	"""Simple Login App"""

	#add_number_of_users()

	st.title("Login App")

	menu = ["Login"]
	choice = st.sidebar.selectbox("Menu",menu)


	if choice == "Login":
		st.subheader("Login Section")

		email = st.sidebar.text_input("EMAIL")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.button("Login"):
			hashed_pswd = make_hashes(password)
			result = login_user(email,check_hashes(password,hashed_pswd))
			print(result)
			if result:

				st.success("Welcome {} {} {}".format(result[0][3], result[0][4], result[0][2]))

			else:
				st.warning("Incorrect Username/Password")




if __name__ == '__main__':
	main()

