import sys

def fibinaci(n):
    "1, 1, 2, 3, 5, 8, ...... "
    a = 1
    b = 1
    while b < n:
        a, b = b, a+b
        print (a)
        

def main(args): 
    fibinaci(500)  
    
    
def myfunction(first, second):
        pass
    
def bar(first, second, third, **options):
    if options.get("action") == "sum":
        print("The sum is: %d" %(first + second + third))

    if options.get("number") == "first":
        return first

    result = bar(1, 2, 3, action = "sum", number = "first")
    print("Result: %d" %(result))

def repeater(old_function):
    """add repeater"""
    def new_function(*args, **kwds): # See learnpython.org/en/Multiple%20Function%20Arguments for how *args and **kwds works
        old_function(*args, **kwds) # we run the old function
        old_function(*args, **kwds) # we do it twice
    return new_function # we have to return the new_function, or it wouldn't reassign it to the value

@repeater
def myfunc():
    print("mytest")

if __name__ == '__main__':
    main(sys.argv[1:])  
    
        
    
