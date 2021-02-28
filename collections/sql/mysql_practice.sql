use classicmodels;

#single entity

#1
select * 
from offices
order by country, state, city;

#2
select count(employeeNumber) as 'total_employees'
from employees;

#3
select sum(amount) as 'total_payment'
from payments;

#4
select productLine
from productlines
where productLine like('%Cars%');

#5
select sum(amount) as 'payments_20041028'
from payments
where paymentDate = '2004-10-28';

#6
select * 
from payments
where amount > 100000;

#7
select productLine, productName
from products
order by productLine asc;

#8
select productLine, count(productCode) as 'product_count'
from products
group by productLine;

#9
select min(amount) as 'min_payment'
from payments;

#10
select *
from payments
having amount > (select 2*avg(amount) from payments);

#11
select avg((MSRP - buyPrice) /buyPrice) * 100 as avg_percentage_markup
from products;

#12
select count(distinct productName) as num_product
from products;

#13
select customerName, city
from customers
where salesRepEmployeeNumber is null;

#14
select concat(firstName, ' ', lastName) as executive_name, jobTitle
from employees
where jobTitle like ('%VP%') or jobTitle like('%Manager%');

#15
select * 
from orderdetails
group by orderNumber
HAVING sum(priceEach * quantityOrdered) > 5000;



#one to many relationship

#1
select customerName, concat(e.firstName, ' ',e.lastName) as rep_name
from customers c 
left join employees e on c.salesRepEmployeeNumber = e.employeeNumber;

#2
select c.customerName, sum(p.amount) as total_payment
from customers c
join payments p on c.customerNumber = p.customerNumber
where c.customerName = 'Atelier graphique';

#3
select paymentDate, sum(amount) as total_payment
from payments
group by paymentDate
order by paymentDate asc;

#4
select *
from products
where quantityInStock > 0;

#5
select c.customerName, sum(p.amount) as amount_paid
from payments p
join customers c on p.customerNumber = c.customerNumber
group by p.customerNumber;

#6
select c.customerName, count(o.orderNumber) as order_count
from orders o 
join customers c on o.customerNumber = c.customerNumber
where c.customerName = 'Herkku Gifts';

#7
select concat(e.firstName, ' ', e.lastName) as emp_name, o.city as work_city
from employees e
join offices o on e.officeCode = o.officeCode
where o.city = 'Boston';

#8
select p.amount, c.customerName
from payments p
join customers c on p.customerNumber = c.customerNumber
where p.amount > 100000
order by p.amount desc;

#9
select o.orderNumber, sum(od.quantityOrdered * od.priceEach) as order_value, o.status
from orders o
join orderdetails od on o.orderNumber = od.orderNumber
where o.status = 'On Hold'
group by od.orderNumber;

#10
select c.customerName, count(o.orderNumber) as onhold_orders
from orders o 
join customers c on o.customerNumber = c.customerNumber
where o.status = 'On Hold'
group by o.customerNumber;


# Many to many relationship

#1
select p.productName, o.orderDate
from orders o
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
order by o.orderDate asc;

#2
select p.productName, o.orderDate
from orders o
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
where p.productName = '1940 Ford Pickup Truck'
order by o.orderDate desc;

#3
select c.customerName, o.orderNumber, sum(priceEach*quantityOrdered) as order_amount
from customers c
join orders o on c.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
group by od.orderNumber
having sum(priceEach*quantityOrdered) > 25000;

#4
select od.productCode, p.productName
from orderdetails od 
join orders o on od.orderNumber = o.orderNumber
join products p on od.productCode = p.productCode
group by od.productCode
having count(od.orderNumber) = (select count(distinct orderNumber) from orderdetails);

#5
select p.productName, (priceEach/MSRP)*100 as price_percentage_MSRP
from products p 
join orderdetails od on p.productCode = od.productCode
WHERE (priceEach/MSRP) < 0.8;

#6
select p.productCode, p.productName, od.orderNumber, 100*(od.priceEach - p.buyPrice)/p.buyPrice as mark_up_percentage
from products p 
join orderdetails od on p.productCode = od.productCode
where od.priceEach > 2 * p.buyPrice;

#7
select p.productCode, p.productName, o.orderDate
from orders o
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
where weekday(o.orderDate) = 0;

#8
select p.productCode, p.productName, p.quantityInStock
from orders o 
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
where o.status = 'On Hold';



# regular expression

#1
select *
from products
where  productName like ('%Ford%');

#2
select *
from products
where productName like ('%ship');

#3
select country, COUNT(customerNumber) as customer_count
from customers
where country in ('Denmark','Norway','Sweden')
group by country;

#4
SELECT productCode, productName
from products
where productCode between 'S700_1000' and 's700_1499';

#5
select customerName
from customers
where customerName REGEXP '[0-9]';

#6
select firstName,lastName
from employees
where firstName in ('Dianne','Diane') or lastName in ('Dianne','Diane');

#7
select productName
from products
where productName like '%ship%' or productName like '%boat%';

#8
select productCode
from products
where productCode like 'S700%';

#9
select firstName, lastName
from employees
where firstName in ('Larry','Barry') or lastName in ('Larry','Barry');

#10
select firstName,lastName
from employees
where not (firstName regexp '[a-z]') or not (lastName regexp '[a-z]');

#11
select distinct productVendor
from products
where productVendor like '%Diecast';






#General queries
#1
select employeeNumber, firstName, lastName
from employees
where reportsTo is null;

#2
select employeeNumber,firstName,lastName
from employees
where reportsTo = (select employeeNumber from employees where firstName = 'William' and lastName = 'Patterson');

#3
select DISTINCT p.productName
from customers c
join orders o on c.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
where c.customerName = 'Herkku Gifts';

#4
select e.firstName, e.lastName, sum(od.priceEach * od.quantityOrdered)*0.05 as comission
from employees e
join customers c on e.employeeNumber = c.salesRepEmployeeNumber
join orders o on c.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
group by e.employeeNumber
order by e.lastName, e.firstName;

#5
select datediff(max(orderDate), min(orderDate)) as days_diff
from orders;

#6
select c.customerName, avg(shippedDate - orderDate) as average_diff
from customers c
join orders o on c.customerNumber = o.customerNumber
group by c.customerNumber
order by avg(datediff(shippedDate,orderDate)) desc;

#7
select o.orderNumber, sum(od.priceEach * od.orderLineNumber) as order_value
from orders o 
join orderdetails od on o.orderNumber = od.orderNumber
where month(shippedDate) = 8 and year(shippedDate) =2004
group by o.orderNumber;

#8
select sum(od.quantityOrdered * od.priceEach) as value_ordered, sum(p.amount) as payment, sum(od.quantityOrdered * od.priceEach)-sum(p.amount) as diff_order_payment
from customers c
join orders o on c.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
join payments p on c.customerNumber = p.customerNumber
where year(o.orderDate) = 2004 and year(p.paymentDate) = 2004
group by c.customerNumber;

#9
select concat(e1.firstName, ' ', e1.lastName) as employee_name
from employees e1
join employees e2 on e1.reportsTo = e2.employeeNumber
join employees e3 on e2.reportsTo = e3.employeeNumber
where e3.firstName = 'Diane' and e3.lastName = 'Murphy';

#10
select productCode, productName, 100 * sum(quantityInStock * MSRP)/(SELECT sum(quantityInStock*MSRP) from products) as value_percentage
from products
group by productCode
order by sum(quantityInStock * MSRP) desc;

#11
delimiter $$
create function mpg_convert(v_mpg double) returns double
deterministic no sql reads sql data
begin
declare v_lpk double;
return 2.35215 * v_mpg;
end $$
delimiter ;

#12
delimiter $$
create procedure increase_price(in increase_percentage double, in category varchar(255))
begin
update products
set MSRP = (increase_percentage + 1)  * MSRP
where productLine = category;
end $$
delimiter ;


#13
select o.orderNumber, sum(od.priceEach * od.orderLineNumber) as order_value
from orders o 
join orderdetails od on o.orderNumber = od.orderNumber
where month(shippedDate) = 8 and year(shippedDate) =2004
group by o.orderNumber;

#14
select month(orderDate) as order_month, sum(od.quantityOrdered * od.priceEach)/ sum(p.amount) as ratio
from payments p
join orders o on p.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
group by order_month;

#15
SELECT 
    tb1.payment_month,
    tb1.monthly_payment AS 2004_payment,
    tb2.monthly_payment AS 2003_payment,
    tb1.monthly_payment - tb2.monthly_payment AS payment_difference
FROM
    (SELECT 
        MONTH(paymentDate) AS payment_month,
            SUM(amount) AS monthly_payment
    FROM
        payments
    WHERE
        YEAR(paymentDate) = 2004
    GROUP BY MONTH(paymentDate)) AS tb1
        JOIN
    (SELECT 
        MONTH(paymentDate) AS payment_month,
            SUM(amount) AS monthly_payment
    FROM
        payments
    WHERE
        YEAR(paymentDate) = 2003
    GROUP BY MONTH(paymentDate)) AS tb2 ON tb1.payment_month = tb2.payment_month
ORDER BY payment_month ASC;

#16
delimiter $$
create procedure amount_ordered(in v_month integer, in v_year integer, in v_name varchar(255))
begin
	select sum(od.quantityOrdered * od.priceEach)
    from customers c
    left join orders o on c.customerNumber = o.customerNumber
    join orderdetails od on o.orderNumber = od.orderNumber
    where month(o.orderDate) = v_month and year(o.orderDate) = v_year and c.customerName regexp v_name ;
end $$
delimiter ;

#17
delimiter $$
create procedure change_credit_limit(in v_percentage double, in v_country varchar(255))
begin
update customers
set creditLimit = (1 + v_percentage) * creditLimit
where country = v_country;
end$$
delimiter ;

#18
#???????



#19
SELECT 
    c.customerNumber,
    c.customerName,
    SUM(od.quantityOrdered * od.priceEach) AS revenue,
    100 * SUM(od.quantityOrdered * od.priceEach) / (SELECT 
            SUM(quantityOrdered * priceEach)
        FROM
            orderdetails) AS revenue_percentage
FROM
    customers c
        LEFT JOIN
    orders o ON c.customerNumber = o.customerNumber
        JOIN
    orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY c.customerNumber
order by c.customerName;


#20
SELECT 
    c.customerNumber,
    c.customerName,
    SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) AS profit,
    100 * SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) / (SELECT 
            SUM(quantityOrdered * (priceEach - buyPrice))
        FROM
            orderdetails od
                JOIN
            products p ON od.productCode = p.productCode) AS profit_percentage
FROM
    customers c
        LEFT JOIN
    orders o ON c.customerNumber = o.customerNumber
        JOIN
    orderdetails od ON o.orderNumber = od.orderNumber
        JOIN
    products p ON od.productCode = p.productCode
GROUP BY c.customerNumber
ORDER BY profit DESC;


#21
SELECT 
    e.employeeNumber,
    e.firstName,
    e.lastName,
    SUM(od.priceEach * od.quantityOrdered) AS revenue
FROM
    customers c
        JOIN
    employees e ON c.salesRepEmployeeNumber = e.employeeNumber
        JOIN
    orders o ON c.customerNumber = o.customerNumber
        JOIN
    orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY e.employeeNumber;


#22
select 
	e.employeeNumber,
    e.lastName,
    e.firstName,
    sum(quantityOrdered * (priceEach - buyPrice)) as profit
from customers c
left join employees e on c.salesRepEmployeeNumber = e.employeeNumber
join orders o on c.customerNumber = o.customerNumber
join orderdetails od on o.orderNumber = od.orderNumber
join products p on od.productCode = p.productCode
group by e.employeeNumber
order by profit desc;


#23
select  
	p.productName,
    sum(quantityOrdered * priceEach) as revenue
from products p 
join orderdetails od on p.productCode = od.productCode
group by p.productCode
order by p.productName;


#24
select 
	p.productLine,
    sum(quantityOrdered * (priceEach - buyPrice)) as profit
from products p
join orderdetails od on p.productCode = od.productCode
group by p.productLine
order by profit desc;


#25
SELECT 
    tb_2003.productCode,
    tb_2003.productName,
    revenue_2004 / revenue_2003 AS ratio
FROM
    (SELECT 
        p.productCode,
            p.productName,
            SUM(od.priceEach * od.quantityOrdered) AS revenue_2003
    FROM
        products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    WHERE
        YEAR(o.orderDate) = 2003
    GROUP BY p.productCode) AS tb_2003
        LEFT JOIN
    (SELECT 
        p.productCode,
            SUM(od.priceEach * od.quantityOrdered) AS revenue_2004
    FROM
        products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    WHERE
        YEAR(o.orderDate) = 2004
    GROUP BY p.productCode) AS tb_2004 ON tb_2003.productCode = tb_2004.productCode
GROUP BY productCode;


#26
SELECT 
    tb_2003.customerNumber,
    tb_2003.customerName,
    tb_2003.payments AS payment_2003,
    tb_2004.payments AS payment_2004,
    tb_2004.payments / tb_2003.payments AS payments_ratio
FROM
    (SELECT 
        c.customerNumber, c.customerName, SUM(p.amount) AS payments
    FROM
        customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    WHERE
        YEAR(paymentDate) = 2003
    GROUP BY c.customerNumber) AS tb_2003
        LEFT JOIN
    (SELECT 
        c.customerNumber, SUM(p.amount) AS payments
    FROM
        customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    WHERE
        YEAR(paymentDate) = 2004
    GROUP BY c.customerNumber) AS tb_2004 ON tb_2003.customerNumber = tb_2004.customerNumber
GROUP BY tb_2003.customerNumber;


#27
SELECT DISTINCT
    p.productCode, p.productName
FROM
    products p
        LEFT JOIN
    orderdetails od ON p.productCode = od.productCode
        JOIN
    orders o ON od.orderNumber = o.orderNumber
WHERE
    p.productCode IN (SELECT DISTINCT
            p.productCode
        FROM
            products p
                JOIN
            orderdetails od ON p.productCode = od.productCode
                JOIN
            orders o ON od.orderNumber = o.orderNumber
        WHERE
            YEAR(o.orderDate) = 2003)
        AND p.productCode NOT IN (SELECT DISTINCT
            p.productCode
        FROM
            products p
                JOIN
            orderdetails od ON p.productCode = od.productCode
                JOIN
            orders o ON od.orderNumber = o.orderNumber
        WHERE
            YEAR(o.orderDate) = 2004);
            
#28
SELECT DISTINCT
    p.customerNumber, c.customerName
FROM
    payments p
        JOIN
    customers c ON p.customerNumber = c.customerNumber
WHERE
    c.customerNumber NOT IN (SELECT DISTINCT
            customerNumber
        FROM
            payments
        WHERE
            YEAR(paymentDate) = 2003);
            


#correlated subqueries
#1
SELECT DISTINCT
    employeeNumber, lastName, firstName
FROM
    employees
WHERE
    reportsTo = (SELECT 
            employeeNumber
        FROM
            employees
        WHERE
            lastName = 'Patterson'
                AND firstName = 'Mary');


#3
select
	productLine,
	productCode,
    productName,
    round(100 * product_value / sum(product_value),2) as value_percentage
from (
	select 
		productCode,
        productName,
        productLine,
        buyPrice * quantityInStock as product_value
    from products) tb1
order by productLine, product_value DESC;
                
                
#4
select 
	orderNumber,
    productCode, 
    product_value,
    100 * (product_value/sum(product_value)) as percentage
from (
	select 
		orderNumber, 
        productCode,
        quantityOrdered * priceEach as product_value
    from orderdetails
    ) tb1
group by orderNumber
HAVING count(productCode) >= 2 and product_value > 0.5 * sum(product_value);
                











#spatial data
# no data available






