use classicmodels;

-- List products sold by order date.
select productCode
from orderdetails
join orders
on orderdetails.orderNumber = orders.orderNumber
order by orderDate;

-- List the order dates in descending order for orders for the 1940 Ford Pickup Truck.
select orderDate
from orders
join orderdetails
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where productName = '1940 Ford Pickup Truck'
order by orderDate DESC;

-- List the names of customers and their corresponding order number 
-- where a particular order from that customer has a value greater than $25,000?
select customerName, orderNumber, amount
from payments
left join orders
on orders.customerNumber = payments.customerNumber
left join customers
on payments.customerNumber = customers.customerNumber
where amount > 25000;

-- question, total 329, max 28 for a single product
-- Are there any products that appear on all orders?
select count(distinct productCode)
from products;

select count(distinct orderNumber)
from orders;

select productCode, count(distinct orderNumber)
from orderdetails
group by productCode;


-- List the names of products sold at less than 80% of the MSRP.
select distinct(products.productCode), productName
from orderdetails
join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where priceEach < 0.8 * MSRP;


-- Reports those products that have been sold with a markup of 100% or more 
-- (i.e.,  the priceEach is at least twice the buyPrice)
select distinct(products.productCode), productName
from orderdetails
join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where priceEach >= 2 * buyPrice;




-- List the products ordered on a Monday.
select products.productCode, productName
from orderdetails
join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where weekday(orderDate) = 0;


-- What is the quantity on hand for products listed on 'On Hold' orders?
select products.productCode, productName, quantityInStock
from orderdetails
join orders
on orderdetails.orderNumber = orders.orderNumber
left join products
on orderdetails.productCode = products.productCode
where status = 'On Hold';
 