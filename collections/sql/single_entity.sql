use classicmodels;

SELECT 
    customerNumber,
    SUM(amount) AS total_amount
FROM payments
where year(paymentDate) = 2004
GROUP BY customerNumber
ORDER BY total_amount DESC
LIMIT 3;

-- Single entity
-- 1 Prepare a list of offices sorted by country, state, city.
select * 
from offices
ORDER BY country ASC, state ASC, city ASC;

-- 2 How many employees are there in the company?
SELECT COUNT(*) 
FROM employees;

-- What is the total of payments received?
select sum(amount)
from payments;

-- List the product lines that contain 'Cars'.
select *
from productlines
where productLine like '%cars%';

-- Report total payments for October 28, 2004.
select sum(amount)
from payments
where paymentDate = '2004-10-28';

-- Report those payments greater than $100,000.
select *
from payments
where amount > 100000;

-- List the products in each product line.
select * 
from products
order BY productLine ASC;

-- How many products in each product line?
select productLine, count(*)
from products
group BY productLine;

-- What is the minimum payment received?
select min(amount)
from payments;

-- List all payments greater than twice the average payment.
select *
from payments
where amount > 2 * (select avg(amount) from payments);

-- What is the average percentage markup of the MSRP on buyPrice?
select avg(MSRP/buyPrice)
from products;

-- How many distinct products does ClassicModels sell?
select count(distinct productCode)
from products;

-- Report the name and city of customers who don't have sales representatives?
select customerName, city
from customers
where salesRepEmployeeNumber is null;

-- What are the names of executives with VP or Manager in their title? 
-- Use the CONCAT function to combine the employee's first name and last name into a single field for reporting.
SELECT CONCAT(firstName, " ", lastName) AS Name
FROM employees
WHERE jobTitle like '%VP%' or 'Manager';


-- Which orders have a value greater than $5,000?
select *
from orders
where customerNumber in (select customerNumber from payments where amount >5000);
