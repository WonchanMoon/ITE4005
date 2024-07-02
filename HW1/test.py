import sys

input1 = sys.argv[1]
input2 = sys.argv[2]

f1 = open(input1, "r") #정답
f2 = open(input2, "r") #내꺼
lines_1 = f1.readlines()
lines_2 = f2.readlines()

j = 0
for i in lines_1:
    if i in lines_2:
        j+=1
    else:
        print(i)

print(j)
f1.close()
f2.close()