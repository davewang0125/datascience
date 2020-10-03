use classicmodels;

-- Find products containing the name 'Ford'.
select *
from products
where productName like '%Ford%';

-- List products ending in 'ship'.
select * 
from products
where productName like '%ship';

-- Report the number of customers in Denmark, Norway, and Sweden.
select *
from customers
where country in ('Dnnmark','Norway','Sweden');


-- What are the products with a product code in the range S700_1000 to S700_1499?
select *
from products
where productCode between 'S700_1000' and 'S700_1499';

-- Which customers have a digit in their name?
select *
from customers
where customerName REGEXP '[0-9]';

-- List the names of employees called Dianne or Diane.
select *
from employees
where lastName like '%Dianne%' or lastName like '%Diane%' or firstName like '%Dianne%' or firstName like '%Diane%';

-- List the products containing ship or boat in their product name.
select *
from products
where productName like '%ship%' or productName like '%boat%';

-- List the products with a product code beginning with S700.
select *
from products
where productCode like 'S700%';

-- List the names of employees called Larry or Barry.
select *
from employees
where lastName like '%Larry%' or lastName like '%Barry%' or firstName like '%Larry%' or firstName like '%Barry%';


-- List the names of employees with non-alphabetic characters in their names.
select *
from employees
where lastName regexp '^[^a-z0-9]' or firstName regexp '^[^a-z0-9]';

-- List the vendors whose name ends in Diecast
select *
from products
where productVendor like '%Diecast';