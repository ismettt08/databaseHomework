#DATABASE_URL=postgres://postgres:123456@taha:5432/eczanem python3 server.py 

#Medicine List
#Sales List
#Session extra attributes
#Delete Account
#User extra attributes
#Patinets extra attributes
#Reports
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
        cursor.execute("UPDATE sessions SET last_used = CURRENT_TIMESTAMP WHERE session_id = '{0}'".format((kurabiye)))
        connection.commit()
        if(cursor.rowcount != 0):
            return int(curUserRole[0][0])
    return -1
def getTheme():
    cursor = connection.cursor() 
    kurabiye = request.cookies.get("session_id")
    cursor.execute("SELECT theme FROM sessions WHERE session_id = '{}'".format(kurabiye))
    theme =cursor.fetchall()
    if(cursor.rowcount != 0):
        return theme[0][0]
    return 0

def home_page():
    role = getUserRole()
    cursor = connection.cursor() 
    theme = request.args.get("thecolor") #white = 0, dark = 1, blue = 2
    kurabiye = request.cookies.get("session_id")
    if theme:
        cursor.execute("UPDATE sessions SET theme = {a} WHERE session_id = '{b}'".format(a=theme, b=kurabiye))
        resp = make_response(render_template("main.html", userRole = role, theme = int(theme)))
    else:
        resp = make_response(render_template("main.html", userRole = role, theme = getTheme()))
    connection.commit()
    
    return resp

def employee_page():
    role = getUserRole()
    if(role != 1):
        print("You don't have the permission!")
        return redirect('/')
    return render_template("employee.html", userRole = role, theme = getTheme())

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
    cursor.execute("INSERT INTO sessions (session_id, user_id, last_used, created_at, user_agent, ip, theme) VALUES ('{a}', {b}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '{c}', '{d}', 0)".format(a=kurabiye, b=userID[0][0],c=request.user_agent, d=request.remote_addr))
    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = {}".format(userID[0][0]))
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
    
    cursor.execute("INSERT INTO users (user_name, user_role, password, created_at) VALUES ('{a}', 0, '{b}', CURRENT_TIMESTAMP)".format(a=name, b=hashed.hexdigest()))
    connection.commit() #Database değiştirmek için
    #TODO başarılı oldu yazısı dön
    return redirect('/employee')

def delete_account():
    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT user_id FROM sessions WHERE session_id = '{}'".format(kurabiye))
        userID = cursor.fetchall()
        if userID[0][0] == 0:   #Can not delete root user
            print("Can not delete root user")
            return redirect("/")
        if(cursor.rowcount != 0):
            #DELETE USER'S EVERY SESSIONS
            cursor.execute("DELETE FROM sessions WHERE user_id = {}".format(userID[0][0]))
            #DELETE USER
            cursor.execute("DELETE FROM users WHERE user_id = {}".format(userID[0][0]))
            connection.commit()
    return redirect("/")

def logout_page():
    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = '{}'".format(kurabiye))
        cursor.fetchall() #Clear cursor
        if(cursor.rowcount != 0):        
            cursor.execute("DELETE FROM sessions WHERE session_id = '{0}'".format((kurabiye)))
            connection.commit()
    return redirect('/')

def sell_page():
    curUserRole = getUserRole()
    if curUserRole == -1:
        return redirect("/")

    cursor = connection.cursor()
    cursor.execute("SELECT to_json(patient_id_number) FROM patients")
    allPatinets = cursor.fetchall()
    patientsCitizenship = "{"
    for i in range(cursor.rowcount):
        patientsCitizenship = patientsCitizenship + "\""+allPatinets[i][0] + "\"" + ": null,"
    patientsCitizenship = patientsCitizenship + "}"
    print(patientsCitizenship)

    basketID = getBasketID()
    cursor.execute("SELECT med_name, price, med_detail, quantity, basket_entry_id FROM medicines INNER JOIN basket_entries ON basket_entries.medicine_id = medicines.medicine_id WHERE basket_entries.basket_id = {} order by basket_entry_id".format(basketID))
    medAttributes = cursor.fetchall()
    totalPrice = 0
    for i in range(cursor.rowcount):
        totalPrice = totalPrice + medAttributes[i][1] * medAttributes[i][3]

    return render_template("sell.html", userRole = curUserRole, medList = medAttributes, citizenshipJSON = patientsCitizenship, theme = getTheme(), totalPrice = totalPrice)

#methods = ['POST']
def addstock_api():
    cursor = connection.cursor()
    if request.form["submit"]:
        barcode = request.form["thebarcode"]
        amount = request.form["theamount"]
    
        cursor.execute("SELECT medicine_id FROM medicines WHERE med_barcode = '{}'".format(barcode))
        cursor.fetchall()
        if(cursor.rowcount == 0): #If there is no citizen with that id
            return redirect("/med")

        if barcode and amount:
            cursor.execute("UPDATE medicines SET stock_quantity = stock_quantity + {a} WHERE med_barcode = '{b}'".format(a=int(amount), b=int(barcode[0][0])))
            connection.commit()
        else: #If at least one of them is empty
            return redirect("/med")
    return redirect("/med")

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
        isCredit = 0
        if "isCredit" in request.form.to_dict():
            isCredit = 1
        citizenshipNumber = request.form["thecustomer"]
        if citizenshipNumber == "": #If citizenship number is empty return
            return redirect("/sell")

        cursor.execute("SELECT patient_id FROM patients WHERE patient_id_number = '{}'".format(citizenshipNumber))
        cursor.fetchall()
        if(cursor.rowcount == 0): #If there is no patient with that citizenship_id
            return redirect("/sell")

        cursor.execute("SELECT medicine_id FROM basket_entries WHERE basket_id = {}".format(basketID))
        cursor.fetchall()
        if(cursor.rowcount != 0):
            cursor.execute("SELECT basket_id FROM baskets WHERE basket_id = {}".format(basketID))
            cursor.fetchall()
            if(cursor.rowcount != 0):
                cursor.execute("UPDATE baskets SET basket_state = true WHERE basket_id = {}".format(basketID))
                connection.commit()
                cursor.execute("SELECT patient_id FROM patients WHERE patient_id_number = '{}'".format(citizenshipNumber))
                patientID = cursor.fetchall()

                kurabiye = request.cookies.get("session_id")
                if kurabiye is not None:
                    cursor.execute("SELECT users.user_id FROM users INNER JOIN sessions ON sessions.user_id = users.user_id WHERE sessions.session_id = '{0}'".format((kurabiye)))
                    userID = cursor.fetchall()
                    
                    cursor.execute("SELECT price, quantity, basket_entries.medicine_id FROM medicines INNER JOIN basket_entries ON basket_entries.medicine_id = medicines.medicine_id WHERE basket_entries.basket_id = {} order by basket_entry_id".format(basketID))
                    basketAttr = cursor.fetchall()
                    #Stock -= sold quantity
                    for i in range(cursor.rowcount):
                        cursor.execute("UPDATE medicines SET stock_quantity = stock_quantity - {a} WHERE medicine_id = {b}".format(a=basketAttr[i][1], b=basketAttr[i][2]))
                    ###
                    ##TotalPrice Calculation
                    totalPrice = 0
                    for i in range(cursor.rowcount):
                        totalPrice = totalPrice + basketAttr[i][0] * basketAttr[i][1]
                    ###
                    cursor.execute("SELECT payment_method_id FROM payment_methods WHERE payment_type = {}".format(isCredit))
                    paymentType = cursor.fetchall()
                    print("INSERT INTO SALESSSS")
                    cursor.execute("INSERT INTO sales (basket_id, patient_id, payment_method_id, price, user_id) VALUES ({a}, {b}, {c}, {d}, {e})".format(a=basketID, b=patientID[0][0],c=paymentType[0][0],d=totalPrice,e=userID[0][0]))
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
    return basketID[0][0]

def patient_table():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()
    cursor.execute("SELECT patient_name, patient_surname, patient_phone_number, patient_id_number FROM patients ORDER BY patient_id")
    patients = cursor.fetchall()
    return render_template("patient_table.html", userRole = role, patientList = patients, theme = getTheme())

#methods = ['POST','GET']
def update_medicine():
    basket_entry_id = request.args.get("basket_entry_id")
    amount =  request.args.get("amount")
    cursor = connection.cursor()
    if amount == "0":
        cursor.execute(f"delete from basket_entries where basket_entry_id = {basket_entry_id}")
    else: #TODO negatif şanslara girmesine izin verme
        cursor.execute(f"update basket_entries set quantity = quantity + {amount} where basket_entry_id = {basket_entry_id}")
    connection.commit()
    return redirect("/sell")

#methods = ['POST','GET']
def patient():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()

    citizenshipNumber = request.args.get("citizenshipNumber")
    
    print(citizenshipNumber)
    cursor.execute("SELECT patient_name, patient_surname, patient_phone_number, patient_id_number FROM patients WHERE patient_id_number = '{}'".format(citizenshipNumber))
    if (citizenshipNumber is None) or (cursor.rowcount == 0): #Empty patient card
        return render_template("patient.html", userRole = role)
    curPatient = cursor.fetchall()
    return render_template("patient.html", userRole = role, citizenshipNumber = citizenshipNumber, patient = curPatient, theme = getTheme()) #Full patient card

#methods = ['POST','GET']
def med():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()

    return render_template("med.html", userRole = role, theme = getTheme())

#methods = ['POST','GET']
def crud_patient():
    
    role = getUserRole()
    if role == -1:
        return redirect("/patient.html")
    cursor = connection.cursor()

    ###TEST AREA ###
    print(request.user_agent)
    print(request.remote_addr)
    ### ###

    citizenship = request.form['citizenship']
    cursor.execute("SELECT * FROM patients WHERE patient_id_number = '{}'".format(citizenship))
    if request.form["submit"] == "update":
        print("DEBUG2")
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        if cursor.rowcount == 0: #Add new patient
            cursor.fetchall() #Clear cursor
            if phone:
                cursor.execute("INSERT INTO patients (patient_name, patient_surname, patient_phone_number, patient_id_number, created_at) VALUES ('{a}', '{b}', '{c}', '{d}', CURRENT_TIMESTAMP)".format(a=name, b=surname, c=phone, d=citizenship))
            else:
                cursor.execute("INSERT INTO patients (patient_name, patient_surname, patient_id_number, created_at) VALUES ('{a}', '{b}', '{c}', CURRENT_TIMESTAMP)".format(a=name, b=surname, c=citizenship))
            connection.commit()
        else: #Update the patient
            cursor.fetchall() #Clear cursor
            if phone:
                cursor.execute("UPDATE patients SET patient_name = '{a}', patient_surname = '{b}', patient_phone_number = '{c}' WHERE patient_id_number = '{d}'".format(a=name, b=surname, c=phone, d=citizenship))
            else:
                cursor.execute("UPDATE patients SET patient_name = '{a}', patient_surname = '{b}' WHERE patient_id_number = '{c}'".format(a=name, b=surname, c=citizenship))
            connection.commit()

    elif request.form["submit"] == "remove":
        print("DEBUG")
        if cursor.rowcount != 0: #Remove patient
            cursor.execute("DELETE FROM patients WHERE patient_id_number = '{}'".format(citizenship))
            connection.commit()
    return redirect("/patient")


def med_table():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM medicines")
    meds = cursor.fetchall()

    cursor.execute("SELECT medicines.medicine_id, med_alternatives.med_alternative FROM medicines INNER JOIN med_alternatives ON medicines.medicine_id = med_alternatives.med_original ORDER BY medicines.medicine_id")
    orToAl = cursor.fetchall()
    
    altNameList = []
    len = cursor.rowcount
    for i in range(len): #[i][0] original [i][1] alternative
        print(orToAl[i][1])
        cursor.execute("SELECT med_name FROM medicines WHERE medicine_id = {}".format(orToAl[i][1]))
        altNameList.append(cursor.fetchall()[0][0])
    print(altNameList)
    print("-----")
    print(orToAl)
    mergedList = [(orToAl[0][0], orToAl[0][1], altNameList[0])]
    for i in range(1, len):
        mergedList.append((orToAl[i][0], orToAl[i][1], altNameList[i]))
    print("-----")
    print(mergedList)
    print("-----")
    
    return render_template("med_table.html", userRole = role, medList = meds, theme = getTheme(), alternativeList = mergedList)

def sale_table():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    print(sales)
    return render_template("sale_table.html", userRole = role, saleList = sales, theme = getTheme())

def profile():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()
    kurabiye = request.cookies.get("session_id")
    if kurabiye is not None:
        cursor.execute("SELECT * FROM users INNER JOIN sessions ON sessions.user_id = users.user_id WHERE sessions.session_id = '{0}'".format((kurabiye)))
        profileData = cursor.fetchall()
        
    return render_template("profile.html", userRole = role,theme = getTheme(), profileData = profileData)

def reports():
    role = getUserRole()
    if role == -1:
        return redirect("/")
    cursor = connection.cursor()
    cursor.execute("SELECT user_id || '. ' || user_name || ' [' || user_role || ']' myUser, SUM(price), COUNT(sale_id) FROM sales INNER JOIN users USING (user_id) GROUP BY myUser")
    byUser = cursor.fetchall()

    cursor.execute("SELECT payment_method_id, SUM(price), COUNT(sale_id) FROM sales GROUP BY payment_method_id")
    byMethod = cursor.fetchall()

    cursor.execute("SELECT patient_name || ' ' || patient_surname full_name, SUM(price), COUNT(sale_id) total FROM sales INNER JOIN patients USING (patient_id) GROUP BY full_name ORDER BY total")
    byPatient = cursor.fetchall()
    return render_template("reports.html", userRole = role, theme = getTheme(), byUser = byUser, byMethod = byMethod, byPatient = byPatient)

###REPORTS###
#Total Sales (How much is credit)
#Sales made by employee
#Medicine Sales (for better orderlist)
###

###Missing###
#Add item to storage (add, cancel)
#Daily, monthly yearly sales report
#Search med for name /category / id
###


##PATLAYACAKLAR
##Nakit ya da kredi yoksa reports-2 patlar

##PATLAYANLAR VE DÜZELTİLECEKLER
#Foreign key violation CREATE deletedPatient and deletedUser