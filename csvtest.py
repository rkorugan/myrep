#This Python file uses the following encoding: utf-8
import csv
f=open("c:\\Users\Ravi\\Desktop\\python\\test.csv","r")
reader = csv.reader(f)
for row in reader:
    print row  
    # f.close()
    f1=open("c:\\Users\Ravi\\Desktop\\python\\tet1.csv","w")
    f1.write("This is first line\n")
    f1.write("This is second line")
    