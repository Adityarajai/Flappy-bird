while True:
    a=int(input("Enter Number: "))
    n=1
    if a == 0:
        break
    while n<11:
         print(f"{a} × {n} = {a*n}")
         n+=1