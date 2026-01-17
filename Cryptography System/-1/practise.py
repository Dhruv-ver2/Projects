import string
import random


with open("log.txt","a") as f:

    f.write("==========Trial==========\n")

    m=input("Type the message:")
    result=''
    alpha=string.ascii_uppercase
    shift=random.randint(2,25)

    f.write(f"user Typed Message: {m}\n")
    f.write(f"random generated key: {shift}\n")

    for i in m:
        i=i.upper()
        if i in alpha:
            p=alpha.find(i)
            np=(p+shift)%26
            result+=alpha[np]
        else:
            result+=i

    f.write(f"Altered message: {result.lower()}\n")
    f.write("==========Session Over==========\n\n")

print(result.lower())
    
