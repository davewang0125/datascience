use classicmodels;

-- Who reports to Mary Patterson?
-- self join question
select A.firstName, A.lastName
from employees A, employees B
where A.reportsTo = B.employeeNumber
and B.firstName = "Mary" and B.lastName = "Patterson";

-- Which payments in any month and year are more than twice the average for that month and year 
-- (i.e. compare all payments in Oct 2004 with the average payment for Oct 2004)? 
-- Order the results by the date of the payment. 
-- You will need to use the date functions.
create view average_payment_per_month
as select avg(amount) as average_amount, month(paymentDate) as pay_month, year(paymentDate) as pay_year
from payments
group by month(paymentDate), year(paymentDate)
order by year(paymentDate), month(paymentDate);

select *
from payments
where amount > 2 * (select average_amount from average_payment_per_month where month(paymentDate) = pay_month and year(paymentDate) = pay_year)
order by year(paymentDate), month(paymentDate);


-- Report for each product, the percentage value of its stock on hand as a percentage of 
-- the stock on hand for product line to which it belongs. 
-- Order the report by product line and percentage value within product line descending. 
-- Show percentages with two decimal places.
create view product_line_value
as select sum(quantityInStock*buyPrice) as line_value, productLine
from products
group by productLine;

select round(quantityInStock*buyPrice/line_value, 2) as pertage_value, productName, products.productLine
from products
left join product_line_value
on products.productLine = product_line_value.productLine
order by products.productLine DESC;

-- For orders containing more than two products, 
-- report those products that constitute more than 50% of the value of the order.
create view order_value
as select sum(quantityOrdered*priceEach) as order_value, orderNumber
from orderdetails
group by orderNumber;

drop view order_value;
select * from order_value;


select sum(orderdetails.quantityOrdered*orderdetails.priceEach)/order_value as percentage, productName, orderdetails.orderNumber
from orderdetails
left join products
on orderdetails.productCode = products.productCode
left join order_value
on orderdetails.orderNumber = order_value.orderNumber
group by orderdetails.orderNumber, orderdetails.productCode;
