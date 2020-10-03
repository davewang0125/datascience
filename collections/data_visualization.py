# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# from pandas.plotting import parallel_coordinates

#connect to database
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='classicmodels',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()

        #Visualize in blue the number of items for each product scale.
        cursor.execute("select count(*) as number, productScale from products group by productScale;")
        record = list(cursor.fetchall())
        print("You're connected to database: ", record)
        
        X = []
        Y = []
        for i, j in record:
            X.append(j)
            Y.append(i)
        plt.title('Visualize in blue the number of items for each product scale.')
        plt.scatter(X,Y)
        plt.show()

        #Prepare a line plot with appropriate labels for total payments for each month in 2004.
        cursor.execute("select sum(amount) as total_payments, month(paymentDate) as month_2014 from payments where year(paymentDate) = 2004 group by month(paymentDate) order by month(paymentDate) ASC;")
        record_1 = list(cursor.fetchall())
        print("You're connected to database: ", record_1)

        X = []
        Y = []
        for i, j in record_1:
            X.append(j)
            Y.append(i)
        plt.plot(X, Y)
        plt.title('Total payments for each month in 2004')
        plt.show()

        #Create a histogram with appropriate labels for the value of orders received from the Nordic countries (Denmark,Finland, Norway,Sweden).
        cursor.execute("select quantityOrdered*priceEach as total_payments, country from orderdetails left join orders on orderdetails.orderNumber = orders.orderNumber left join customers on orders.customerNumber = customers.customerNumber where country = 'Denmark' or country = 'Finland' or country = 'Norway' or country = 'Sweden';")
        record_2 = list(cursor.fetchall())
        print("You're connected to database: ", record_2)

        X = []
        Y = []
        for i, j in record_2:
            X.append(i)
            Y.append(j)
        X= [int(float(x)) for x in X]
        num_bins = 5
        n, bins, patches = plt.hist(X, num_bins, facecolor='blue', alpha=0.5)
        plt.title('Value of orders received from the Nordic countries')
        plt.show()

        #Create a heatmap for product lines and Norwegian cities.
        cursor.execute("select distinct(city) from customers where country = 'Denmark' or country = 'Finland' or country = 'Norway' or country = 'Sweden' group by city order by city DESC;")
        record_3 = list(cursor.fetchall())
        city=[]
        for i in record_3:
            city.append(i[0])
        
        cursor.execute("select distinct(productLine) from products order by productLine DESC;")
        record_4 = list(cursor.fetchall())
        productLine=[]
        for i in record_4:
            productLine.append(i[0])
        
        cursor.execute("select distinct(productLine) from products order by productLine DESC;")
        record_4 = list(cursor.fetchall())
        productLine=[]
        for i in record_4:
            productLine.append(i[0])
 
        cursor.execute("select city, products.productLine, sum(quantityOrdered) as total_quantity\
            from orderdetails\
                left join products\
                    on orderdetails.productCode = products.productCode\
                        left join orders\
                            on orderdetails.orderNumber = orders.orderNumber\
                                left join customers\
                                    on customers.customerNumber = orders.customerNumber\
                                        where country = 'Denmark' or country = 'Finland' or country = 'Norway' or country = 'Sweden'\
                                            group by city, productLine\
                                                order by city DESC, productLine DESC;")
        record_5 = list(cursor.fetchall())
        print("You're connected to database: ", record_5)
        m=len(city)
        n=len(productLine)
        data=np.zeros((m,n))
        for i in range(0, m):
            for j in range(0, n):
                for t in record_5:
                     if t[0] == city[i] and t[1] == productLine[j]:
                        data[i][j] = t[2]
        print(data)

        fig, ax = plt.subplots()
        im = ax.imshow(data)

        # We want to show all ticks...
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(m))
        # ... and label them with the respective list entries
        ax.set_xticklabels(city)
        ax.set_yticklabels(productLine)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        for i in range(m):
            for j in range(n):
                text = ax.text(j, i, data[i, j],
                            ha="center", va="center", color="w")

        ax.set_title("ProductLine by City")
        fig.tight_layout()
        plt.show()
        

        #Create a parallel coordinates plot for product scale, quantity in stock, and MSRP in the Products table.
        cursor.execute("select productScale, quantityInStock, MSRP, productName from products;")
        record_6 = pd.DataFrame(cursor.fetchall())
        record_6.columns = ['productScale', 'quantityInStock', 'MSRP', 'productName']
        print("You're connected to database: ", record_6)
        record_6['quantityInStock'] = record_6['quantityInStock'].apply(str)
        record_6['MSRP'] = record_6['MSRP'].apply(str)
        parallel_coordinates(record_6, 'productName', colormap=plt.get_cmap("Set2"))
        plt.show()


except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")



