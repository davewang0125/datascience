from flask import Flask, render_template, url_for, request, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
mysql = MySQL(app)
if mysql:
   print("Connection Successful!")
else:
   print("Connection Failed!")


@app.route('/', methods=['POST','GET'])
def index():
    if request.method == "POST":
        cust_id = request.form['customerId']
        cust_name = request.form['customerName']
        cont_lname = request.form['contactlname']
        cont_fname = request.form['contactfname']
        phone = request.form['phone']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postalCode']
        country = request.form['country']
        sales_id = request.form['salesrepId']
        limit = request.form['limit']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO classicmodels.customers(customerNumber, customerName, contactLastName, contactFirstName, phone, addressLine1, addressLine2, city, state, postalCode, country, salesRepEmployeeNumber, creditLimit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (cust_id, cust_name, cont_lname, cont_fname, phone, address1, address2, city, state, postal_code, country, sales_id, limit))
        mysql.connection.commit()
        return redirect('/')
    
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM classicmodels.customers ORDER BY creditLimit DESC LIMIT 10''')
        results = cursor.fetchall()
        return render_template('index.html', results=results)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT * FROM classicmodels.customers where customerNumber= {id}")
    result = cursor.fetchall()
    print(result)
    print(type(result))
    if result:
        result = list(result)
        result[0] = list(result[0])
        
        if request.method == 'POST':
            result[0][1] = request.form['customerName']
            result[0][2] = request.form['contactlname']
            result[0][3] = request.form['contactfname']
            result[0][4] = request.form['phone']
            result[0][5] = request.form['address1']
            result[0][6] = request.form['address2']
            result[0][7] = request.form['city']
            result[0][8] = request.form['state']
            result[0][9] = request.form['postalCode']
            result[0][10] = request.form['country']
            result[0][11] = request.form['salesrepId']
            result[0][12] = request.form['limit']
            cursor.execute("UPDATE classicmodels.customers SET customerName = %s, contactLastName = %s, contactFirstName = %s, phone = %s, addressLine1 = %s, addressLine2 = %s, city = %s, state = %s, postalCode = %s, country = %s, salesRepEmployeeNumber = %s, creditLimit = %s WHERE customerNumber = %s",
            (result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7], result[0][8], result[0][9], result[0][10], result[0][11], result[0][12], id))
            try:
                mysql.connection.commit()
                return redirect('/')
            except:
                return render_template('update.html', result=result, id=id)
        else:
            return render_template('update.html', result=result, id=id)


if __name__ == "__main__":
    app.run(debug=True)