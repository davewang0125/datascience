use classicmodels;
-- 1. Employees all over the world. Can you tell me the top three cities that we have employees?
-- Expected result:
-- City      employee count
-- San Francisco   6
-- Paris                  5
-- Syndney            4
select city, count(*) as employeeCount
from employees
left join offices
on employees.officeCode = offices.officeCode
group by city
order by employeeCount DESC
limit 3;


-- 	2. For company products, each product has inventory and buy price, msrp. 
-- 	Assume that every product is sold on msrp price. 
-- Can you write a query to tell company executives: profit margin on each productlines
-- Profit margin= sum(profit if all sold) - sum(cost of each=buyPrice) / sum (buyPrice)
-- Product line = each product belongs to a product line. You need group by product line. 
select (sum(quantityOrdered*MSRP) - sum(quantityOrdered*buyPrice))/sum(quantityOrdered*buyPrice) as profit_margin, productLine
from orderdetails
left join products
on orderdetails.productCode = products.productCode
group by productLine;

-- 3. company wants to award the top 3 sales rep They look at who produces the most sales revenue.
-- 		A. can you write a query to help find the employees. 
--      B. if we want to promote the employee to a manager, what do you think are the tables to be updated. 
--      C. An employee  is leaving the company, write a stored procedure to handle the case. 
-- 		1). Make the current employee inactive, 
-- 		2). Replaced with its manager employeenumber in order table. 
select sum(quantityOrdered * priceEach) as sales, employees.employeeNumber as employee_number, employees.lastName, employees.firstName
from orderdetails
left join orders
on orderdetails.orderNumber = orders.orderNumber
left join customers
on orders.customerNumber = customers.customerNumber
left join employees
on customers.SalesRepEmployeeNumber = employees.employeeNumber
group by employeeNumber
order by sales DESC
limit 3;
 
DELIMITER //
CREATE PROCEDURE employee_leave
(IN employee_number INT)
BEGIN
	UPDATE customers
    SET salesRepEmployeeNumber = (select reportsTo from employees where emplyeeNumber = employee_number)
	WHERE salesRepEmployeeNumber = employee_number;
    
    DELETE
    FROM employees
    WHERE emplyeeNumber = employee_number;
END //
DELIMITER 

=======following challenge:
Employee 
[employee_id, employee_name, gender, current_salary, department_id, start_date, term_date]

Employee_salary 
[employee_id, salary, year, month]

Department 
[department_id, department_name]

4. Employee Salary Change Times 
Ask to provide a table to show for each employee in a certain department how many times their Salary changes 


-- 5. Top 3 salary
-- Ask to provide a table to show for each department the top 3 salary with employee name 
-- and employee has not left the company.
