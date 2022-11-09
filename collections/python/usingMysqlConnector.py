import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="classicmodels"
)
cursor = mydb.cursor()

query1 = ("SELECT monamount, mon, yea, ranking FROM ("
"SELECT monamount, mon, yea, RANK() OVER (PARTITION BY yea ORDER BY monamount DESC) ranking FROM ("
"SELECT SUM(amount) monamount, MONTH(paymentDate) mon, YEAR(paymentDate) yea FROM payments GROUP BY MONTH(paymentDate), YEAR(paymentDate) "
") AS myAmount"
") As myRank "
"WHERE ranking <= 3;")

query2 = ("SELECT monamount, lmamount, (monamount-lmamount)/lmamount pdiff, mon, yea, RANK() OVER (PARTITION BY mon ORDER BY yea DESC) ranking FROM ("
"SELECT monamount, mon, yea, LEAD(monamount, 1) OVER (PARTITION BY mon ORDER BY yea DESC) lmamount FROM ("
"SELECT SUM(amount) monamount, MONTH(paymentDate) mon, YEAR(paymentDate) yea FROM payments GROUP BY MONTH(paymentDate), YEAR(paymentDate)"
") AS myAmount"
") AS myRank WHERE lmamount IS NOT NULL;"
)

cursor.execute(query1)
print("Query1")
for (monamount, mon, yea, ranking) in cursor:
    print(monamount, mon, yea, ranking)

cursor.execute(query2)
print("Query2")
for (monamount, lmonamount, pdiff, mon, yea, ranking) in cursor:
    print(monamount, lmonamount, pdiff, mon, yea, ranking)

cursor.close()
mydb.close()