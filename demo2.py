count=0
while(count<5):
    print(count)
    print(count)
    print(count)
    print(count)
    print(count)
    print(count)
    print(count)
    count +=1
    count +=1
    count +=1
    count +=1
    count +=1
    print(count)
    print(count)
    print(count)
    print(count)
else:
    print("count value reached %d" %(count))

# Prints out 1,2,3,4
for i in range(1, 10):
    if(i%5==0):
        break
    print(i)
else:
    print("this is not printed because for break but not due to fail in condition")
