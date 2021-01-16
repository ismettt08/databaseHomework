#DATABASE_URL=postgres://postgres:123456@taha:5432/eczanem python3 server.py 
from datetime import datetime
from hashlib import sha256, md5
import random
import string
from flask import render_template, request, make_response, redirect
import os
import psycopg2 as dbapi2
import json

url = os.getenv("DATABASE_URL")
connection = dbapi2.connect(url)


def getRandomCookie():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(60))
    return result_str

def getUserRole():
    cursor = connection.cursor() 
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT user_role FROM users INNER JOIN sessions ON sessions.user_id = users.user_id WHERE sessions.session_id = '{0}'".format((kurabiye)))
        curUserRole = cursor.fetchall()
        if(cursor.rowcount != 0):
            return int(curUserRole[0][0])
    return -1

def home_page():
    role = getUserRole()
    resp = make_response(render_template("main.html", userRole = role))
    return resp

def employee_page():
    role = getUserRole()

    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT user_role FROM users INNER JOIN sessions ON sessions.user_id = users.user_id WHERE sessions.session_id = '{0}'".format((kurabiye)))
        curUserRole = cursor.fetchall()

        if(role == -1):
            print("Please fIrst Login")
            return redirect('/')

        if role == 1:
            return redirect("/")
    return render_template("employee.html")
    
    
    #return redirect('/employee')

#methods = ['POST']
def login_api():
    cursor = connection.cursor()
    username = request.form['username']
    passwd = request.form['password']
    print("Username is " + username + " and password is " + passwd)
    hashed = sha256(passwd.encode('utf-8'))
    print("Hashed passwd is " + hashed.hexdigest())
    
    cursor.execute("SELECT password FROM users WHERE user_name = '{}'".format(username))
    userPasswd = cursor.fetchall()
    cursor.execute("SELECT user_id FROM users WHERE user_name = '{}'".format(username))
    userID = cursor.fetchall()
    if(cursor.rowcount == 0):
        print("Wrong usernamE or password")
        return redirect('/')
    print("password passwd is " + userPasswd[0][0])
    
    if(userPasswd[0][0] != hashed.hexdigest()):
        print("Wrong username or passworD")
        return redirect('/')

    print("Session id'i user'a ekle")
    kurabiye = getRandomCookie()
    resp = make_response(redirect('/'))
    resp.set_cookie('session_id', kurabiye)
    cursor.execute("INSERT INTO sessions (session_id, user_id) VALUES ('{a}', {b})".format(a=kurabiye, b=userID[0][0]))
    connection.commit() #Database değiştirmek için
    return resp #temp




#methods = ['POST']
def register_api():
    cursor = connection.cursor()
    name = request.form['employeename']
    passwd = request.form['employeepassword']
    print("Username is " + name + " and password is " + passwd)
    hashed = sha256(passwd.encode('utf-8'))
    print("Hashed passwd is " + hashed.hexdigest())
    
    cursor.execute("SELECT user_name FROM users WHERE user_name = '{}'".format(name))
    cursor.fetchall()
    
    if(cursor.rowcount != 0):
        print("There is already a user named this") #TODO hata vermesini sağla
        return redirect('/employee')
    print("password passwd is " + hashed.hexdigest())
    
    cursor.execute("INSERT INTO users (user_name, user_role, password) VALUES ('{a}', false, '{b}')".format(a=name, b=hashed.hexdigest()))
    connection.commit() #Database değiştirmek için
            #TODO başarılı oldu yazısı dön
    return redirect('/employee')

def logout_page():
    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = {}".format(kurabiye))
        cursor.fetchall() #Clear cursor
        if(cursor.rowcount != 0):        
            cursor.execute("DELETE FROM sessions WHERE session_id = {0}".format((kurabiye)))
            connection.commit()
    return redirect('/')



def sell_page():
    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")

    cursor.execute("SELECT to_json(patient_name) FROM patients")
    allPatinets = cursor.fetchall()
    patientsName = "{"
    for i in range(cursor.rowcount):
        patientsName = patientsName + "\""+allPatinets[i][0] + "\"" + ": null,"
    patientsName = patientsName + "}"
    print(patientsName)

    cursor.execute("SELECT to_json(patient_surname) FROM patients")
    allPatinets = cursor.fetchall()
    patientsSurname = "{"
    for i in range(cursor.rowcount):
        patientsSurname = patientsSurname + "\""+allPatinets[i][0] + "\"" + ": null,"
    patientsSurname = patientsSurname + "}"
    print(patientsSurname)

    if kurabiye is not None:
        curUserRole = getUserRole()
        if(cursor.rowcount == 0):
            return redirect("/")

        basketID = getBasketID()
        cursor.execute("SELECT med_name, price, med_detail, quantity, basket_entry_id FROM medicines INNER JOIN basket_entries ON basket_entries.medicine_id = medicines.medicine_id WHERE basket_entries.basket_id = {} order by basket_entry_id".format(basketID))
        medAttributes = cursor.fetchall()

        return render_template("sell.html", userRole = curUserRole[0][0], medList = medAttributes, patientsNameJSON = patientsName, patientsSurnameJSON = patientsSurname)
    #TODO yok ise anasayfaya yönlendir
    return redirect("/")

def update_medicine():
    basket_entry_id = request.args.get("basket_entry_id")
    amount =  request.args.get("amount")
    cursor = connection.cursor()
    if amount == "0":
        cursor.execute(f"delete from basket_entries where basket_entry_id = {basket_entry_id}")
    else:
        cursor.execute(f"update basket_entries set quantity = quantity + {amount} where basket_entry_id = {basket_entry_id}")
    connection.commit()
    return redirect("/sell")

#methods = ['POST']
def addmed_api():
    cursor = connection.cursor()
    basketID = getBasketID()

    if request.form["submit"] == "send_barcode":
        barcode = request.form['thebarcode']

        cursor.execute("SELECT basket_id FROM baskets WHERE basket_id = {}".format(basketID))
        cursor.fetchall()
        if(cursor.rowcount != 0):
            cursor.execute("SELECT medicine_id FROM medicines WHERE med_barcode = '{}'".format(barcode))
            medID = cursor.fetchall()
            if(cursor.rowcount != 0):
                cursor.execute("SELECT quantity FROM basket_entries WHERE medicine_id = {a} AND basket_id = {b}".format(a=medID[0][0], b=basketID))
                quantity = cursor.fetchall()
                if(cursor.rowcount > 0):
                    cursor.execute("UPDATE basket_entries SET quantity = {a} WHERE medicine_id = {b}".format(a=quantity[0][0]+1, b=medID[0][0]))
                else:
                    cursor.execute("INSERT INTO basket_entries (medicine_id, quantity, basket_id) VALUES ({a}, 1, {b})".format(a=medID[0][0], b=basketID))
                connection.commit()     
    elif  request.form["submit"] == "send_basket":
        cursor.execute("SELECT medicine_id FROM basket_entries WHERE basket_id = {}".format(basketID))
        cursor.fetchall()
        if(cursor.rowcount != 0):
            cursor.execute("SELECT basket_id FROM baskets WHERE basket_id = {}".format(basketID))
            cursor.fetchall()
            if(cursor.rowcount != 0):
                cursor.execute("UPDATE baskets SET basket_state = true WHERE basket_id = {}".format(basketID))
                connection.commit()
    else:
        cursor.execute("DELETE FROM basket_entries WHERE basket_id = {}".format(basketID))
        connection.commit()
    return redirect("/sell")

def getBasketID():
    cursor = connection.cursor()
    cursor.execute("SELECT basket_id FROM baskets WHERE basket_state = false")
    basketID = cursor.fetchall()
    if(cursor.rowcount == 0):
        cursor.execute("INSERT INTO baskets (basket_state) VALUES (false)")
        connection.commit()
        cursor.execute("SELECT basket_id FROM baskets WHERE basket_state = false")
        basketID = cursor.fetchall()
    print(basketID[0][0])
    return basketID[0][0]

def patient_table():

    return render_template("patient_table.html", userRole = curUserRole[0][0])