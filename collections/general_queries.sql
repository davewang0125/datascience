use classicmodels;
-- General queries
-- Who is at the top of the organization (i.e.,  reports to no one).
select * 
from employees
where reportsTo is null;

-- Who reports to William Patterson?
select * 
from employees
where reportsTo = (select employeeNumber from employees where lastName = 'Patterson' and firstName = 'William');

-- List all the products purchased by Herkku Gifts.
select productName
from orders
left join customers
on orders.customerNumber = customers.customerNumber
left join orderdetails
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where customerName = 'Herkku Gifts';

-- Compute the commission for each sales representative, 
-- assuming the commission is 5% of the value of an order. Sort by employee last name and first name.
select sum(quantityOrdered*priceEach*0.05) as commission, CONCAT(employees.lastName, "-", employees.firstName) as name
from orderdetails
left join orders
on orders.orderNumber = orderdetails.orderNumber
left join customers
on orders.customerNumber = customers.customerNumber
left join employees
on customers.salesRepEmployeeNumber = employees.employeeNumber
group by CONCAT(employees.lastName, "-", employees.firstName)
order by CONCAT(employees.lastName, "-", employees.firstName);

-- What is the difference in days between the most recent and oldest order date in the Orders file?
select datediff(max(orderDate), min(orderDate))
from orders;

-- Compute the average time between order date and ship date for each customer ordered by the largest difference.
select avg(datediff(shippedDate, orderDate)), customerName
from orders
left join customers
on orders.customerNumber = customers.customerNumber
group by customerName
order by avg(datediff(shippedDate, orderDate)) desc;

-- What is the value of orders shipped in August 2004? (Hint).
select sum(quantityOrdered*priceEach)
from orderdetails
left join orders
on orders.orderNumber = orderdetails.orderNumber
where month(shippedDate) = 8 and year(shippedDate) = 2004;

-- Compute the total value ordered, total amount paid, and their difference for each customer 
-- for orders placed in 2004 and payments received in 2004 
-- (Hint; Create views for the total paid and total ordered).
create view total_ordered_2004
as select sum(priceEach*quantityOrdered) as sum_value, customerName
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join payments
on orders.customerNumber = payments.customerNumber
left join customers
on customers.customerNumber = payments.customerNumber
where year(orderDate) = 2004 and year(paymentDate) = 2004
group by customerName;

select * from total_ordered_2004;

create view total_paid_amount_2004
as select sum(amount) as sum_paid, customerName
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join payments
on orders.customerNumber = payments.customerNumber
left join customers
on customers.customerNumber = payments.customerNumber
where year(orderDate) = 2004 and year(paymentDate) = 2004
group by customerName;

select * from total_paid_amount_2004;

select sum_value - sum_paid as difference, total_ordered_2004.customerName as customer
from total_ordered_2004
left join total_paid_amount_2004
on total_ordered_2004.customerName = total_paid_amount_2004.customerName;

-- List the employees who report to those employees who report to Diane Murphy. 
-- Use the CONCAT function to combine the employee's first name and last name into a single field for reporting.
select employeeNumber
from employees
where firstName = 'Diane' and lastName = 'Murphy';

select concat(firstName, " ", lastName)
from employees
where reportsTo in (select employeeNumber from employees where reportsTo = 1002);

-- What is the percentage value of each product in inventory 
-- sorted by the highest percentage first (Hint: Create a view first).
create view inventory
as select quantityInStock*buyPrice as value, productCode, productName
from products;

select sum(value)
from inventory;

select value/30534316.23 as percentage_value, productCode, productName
from inventory
order by percentage_value desc;

-- function?
-- Write a function to convert miles per gallon to liters per 100 kilometers.
DELIMITER $$
CREATE FUNCTION Convert_mg_to_kl ( mg INT )
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE kl INT;
    SET kl = 0;
    SET kl = mg / 3.78541 * 1.60934 / 100;
    RETURN kl;
END$$
DELIMITER ;

-- debug
-- Write a procedure to increase the price of a specified product category by a given percentage. 
-- You will need to create a product table with appropriate data to test your procedure. 
-- Alternatively, load the ClassicModels database on your personal machine so you have complete access. 
-- You have to change the DELIMITER prior to creating the procedure.
DELIMITER //
CREATE PROCEDURE increase_price
(IN product_line CHAR(20), percentage DECIMAL)
BEGIN
	UPDATE products
    SET buyPrice = buyPrice * (1 + percentage)
	WHERE productLine = product_line;
END //
DELIMITER ;

-- DROP procedure increase_price;

-- call increase_price('Mortorcycles', 1);

-- What is the value of orders shipped in August 2004? (Hint).
select sum(priceEach * quantityOrdered) as value_ordered
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
where year(shippedDate) = 2004 and month(shippedDate) = 8;

-- What is the ratio the value of payments made to orders received 
-- for each month of 2004. (i.e., divide the value of payments made by the orders received)?
select sum(amount)
from payments
left join orders
on orders.customerNumber = payments.customerNumber
where year(paymentDate) = 2004;

select sum(amount)/21104232.41 as ratio_per_month, month(paymentDate) as month
from payments
left join orders
on orders.customerNumber = payments.customerNumber
where year(paymentDate) = 2004
group by month(paymentDate);

-- What is the difference in the amount received for each month of 2004 compared to 2003?
create view total_2004
as select sum(amount) as month_total_2004, month(paymentDate) as month_2004
from payments
left join orders
on orders.customerNumber = payments.customerNumber
where year(paymentDate) = 2004
group by month(paymentDate);

create view total_2003
as select sum(amount) as month_total_2003, month(paymentDate) as month_2003 
from payments
left join orders
on orders.customerNumber = payments.customerNumber
where year(paymentDate) = 2003
group by month(paymentDate);

-- drop view total_2003;
-- drop view total_2004;

select month_total_2004 - month_total_2003 as difference, month_2003 as month_
from total_2004
left join total_2003
on month_2004 = month_2003;

-- Write a procedure to report the amount ordered in a specific month and year 
-- for customers containing a specified character string in their name.


-- Write a procedure to change the credit limit of all customers in a specified country by a specified percentage.


-- Basket of goods analysis: A common retail analytics task is to analyze each basket or order to 
-- learn what products are often purchased together. Report the names of products that appear in the same order ten or more times.
create view record
as select productCode, count(productCode) as frequency
from orderdetails
group by productCode;

create view frequent_product
as select productCode as frequent_product_code
from record
where frequency >= 10;

create view full_list
as select CONCAT(A.productCode, "-", B.productCode) as related_product, A.productCode as product_code_A, B.productCode as product_code_B, A.orderNumber
from orderdetails A, orderdetails B
where A.orderNumber = B.orderNumber;

select * from full_list;

create view relate_list
as select related_product, count(related_product) as frequency
from full_list
group by related_product 
having frequency >= 10;

select product_code_A, product_code_B
from full_list
where related_product in (select related_product from relate_list);

-- ABC reporting: Compute the revenue generated by each customer based on their orders. 
-- Also, show each customer s revenue as a percentage of total revenue. Sort by customer name.
create view revenue_customer_name
as select sum(quantityOrdered*priceEach) as revenue, customerName
from orderdetails
left join products
on orderdetails.productCode = products.productCode
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join customers
on orders.customerNumber = customers.customerNumber
group by customerName
order by revenue DESC;

select sum(revenue)
from revenue_customer_name;

select revenue/9604190.61 as percentage, customerName
from revenue_customer_name
group by customerName;

-- Compute the profit generated by each customer based on their orders. 
-- Also, show each customer's profit as a percentage of total profit. Sort by profit descending.


-- Compute the revenue generated by each sales representative based on the orders from the customers they serve.
create view revenue_customer
as select sum(quantityOrdered*priceEach) as revenue, salesRepEmployeeNumber
from orderdetails
left join products
on orderdetails.productCode = products.productCode
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join customers
on orders.customerNumber = customers.customerNumber
group by customers.customerNumber
order by revenue DESC;

select sum(revenue) as total_revenue, salesRepEmployeeNumber
from revenue_customer
group by salesRepEmployeeNumber
order by total_revenue DESC;

-- Compute the profit generated by each sales representative based on the orders from the customers they serve. 
-- Sort by profit generated descending.
create view profit_customer
as select sum(quantityOrdered*(priceEach -buyPrice)) as profit, salesRepEmployeeNumber
from orderdetails
left join products
on orderdetails.productCode = products.productCode
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join customers
on orders.customerNumber = customers.customerNumber
group by customers.customerNumber
order by profit DESC;

select sum(profit) as total_profit, salesRepEmployeeNumber
from profit_customer
group by salesRepEmployeeNumber
order by total_profit DESC;



-- Compute the revenue generated by each product, sorted by product name.
select sum(quantityOrdered*priceEach) as reveue, productName
from orderdetails
left join products
on orderdetails.productCode = products.productCode
group by products.productCode
order by products.productCode;


-- Compute the profit generated by each product line, sorted by profit descending.
select sum(quantityOrdered*(priceEach-buyPrice)) as profit, productLine
from orderdetails
left join products
on orderdetails.productCode = products.productCode
group by productLine
order by profit DESC;


-- Same as Last Year (SALY) analysis: Compute the ratio for each product of sales for 2003 versus 2004.
create view order_2003
as select sum(quantityOrdered*priceEach) as sales, productCode
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
where year(orderDate) = 2003
group by productCode;

select * from order_2003;

create view order_2004
as select sum(quantityOrdered*priceEach) as sales, productCode
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
where year(orderDate) = 2004
group by productCode;

select * from order_2004;

select order_2003.sales/order_2004.sales as ratio, order_2003.productCode
from order_2003
left join order_2004
on order_2003.productCode = order_2004.productCode;

-- Compute the ratio of payments for each customer for 2003 versus 2004.
create view payment_2003
as select sum(amount) as sum_amount, customerNumber
from payments
where year(paymentDate) = 2003
group by customerNumber;

select * from payment_2003;

create view payment_2004
as select sum(amount) as sum_amount, customerNumber
from payments
where year(paymentDate) = 2004
group by customerNumber;

select * from payment_2004;

select payment_2003.sum_amount/payment_2004.sum_amount as ratio, payment_2003.customerNumber as customer_number
from payment_2003
left join payment_2004
on  payment_2003.customerNumber =  payment_2004.customerNumber;


-- Find the products sold in 2003 but not 2004.
create view product_2003
as select  products.productCode as product_code, products.productName as product_name
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where year(orders.orderDate) = 2003;

select * from product_2003; 




create view product_2004
as select  products.productCode as product_code, products.productName as product_name
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where year(orders.orderDate) = 2004;

select * from product_2004; 

select product_2003.product_code, product_2003.product_name
from product_2003
where product_2003.product_code not in (select product_2004.product_code
from product_2004);

-- Find the customers without payments in 2003.
create view payment_customer_2003
as select customers.customerNumber as customer_number, sum(amount) as sum_amount
from payments
left join customers
on payments.customerNumber = customers.customerNumber
where year(paymentDate)=2003
group by payments.customerNumber;

-- drop view payment_customer_2003;

select *
from payment_customer_2003;

select customerName
from customers
where customerNumber in (select customer_number from payment_customer_2003 where sum_amount = 0);
