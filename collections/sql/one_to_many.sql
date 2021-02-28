use classicmodels;

-- Report the account representative for each customer.
SELECT customerName, CONCAT(employees.firstName, " ", employees.lastName) AS account_representative
FROM customers left join employees
ON salesRepEmployeeNumber = employeeNumber;

-- Report total payments for Atelier graphique.
select sum(amount)
from payments left join customers
on payments.customerNumber = customers.customerNumber
where customerName = 'Atelier graphique';

-- Report the total payments by date
select sum(amount), paymentDate
from payments
group by paymentDate;

-- Report the products that have not been sold.
select *
from products
where productCode not in (select productCode from orderdetails);

-- List the amount paid by each customer.
select customerName, sum(amount)
from payments left join customers
on payments.customerNumber = customers.customerNumber
group by customerName;


-- How many orders have been placed by Herkku Gifts?
select count(*)
from orders left join customers
on orders.customerNumber = customers.customerNumber
where customerName = 'Herkku Gifts';

-- Who are the employees in Boston?
select CONCAT(employees.firstName, " ", employees.lastName) as employee_name
from employees left join offices
on employees.officeCode = offices.officeCode
where city = 'Boston';

-- Report those payments greater than $100,000. 
-- Sort the report so the customer who made the highest payment appears first.
select customerName, amount
from payments left join customers
on payments.customerNumber = customers.customerNumber
where amount > 100000
order by amount;

-- List the value of 'On Hold' orders.
select customerName, amount
from payments left join orders
on payments.customerNumber = customers.customerNumber
where amount > 100000
order by amount;

-- Report the number of orders 'On Hold' for each customer.
select count(orderNumber), customerName
from orders left join customers
on orders.customerNumber = customers.customerNumber
where orders.status = 'On hold'
group by customerName;
