import sys
from itertools import combinations
import decimal
decimal.getcontext().rounding = decimal.ROUND_HALF_UP #for correct rounding

min_sup = float(sys.argv[1])
input_file = sys.argv[2]
output_file = sys.argv[3]

f = open(input_file, 'r')
transactions = list()
lines = f.readlines()
f.close()

for line in lines:
    transactions.append(tuple(map(int, line.rstrip().split('\t'))))
len_transactions = len(transactions)

def gen_C1(transactions): # first candidate
    items = set()
    C1 = dict()
    for transaction in transactions:
        for item in transaction:
            items.add(item)
    for i in items:
        C1[tuple([i])] = 0
    return C1

def gen_Ck(L_prev): #generate Ck
    Ck = dict()
    # self joining
    for i in L_prev:
        for j in L_prev:
            if len(set(i)-set(j)) == 1:
                itemset = tuple(sorted(set(i)|set(j)))
                # pruning
                if pruning(itemset, L_prev):
                    continue
                else:
                    Ck[itemset] = 0
    return Ck

def pruning(itemset, L_prev):
    subsets = list()
    for item in itemset:
        subsets.append(tuple(sorted(set(itemset) - set([item]))))
    for subset in subsets:
        if subset not in L_prev:
            return True
    return False

def gen_Lk(Ck, transactions, min_sup):
    Lk = set()
    if Ck == {}:
        return Lk
    # counting
    for transaction in transactions:
        for item in Ck:
            if set(transaction) >= set(item):
                Ck[item] += 1

    #add if sup >= min_sup
    for item in Ck:
        if Ck[item]/len_transactions*100 >= min_sup:
            Lk.add(item)
    return Lk
    
def apriori(transactions, min_sup):
    C1 = gen_C1(transactions)
    L = set() # total frequent itemsets
    Lk = gen_Lk(C1, transactions, min_sup)
    L = L | Lk
    while Lk != set():
        Ck = gen_Ck(Lk)
        Lk = gen_Lk(Ck, transactions, min_sup)
        L = L | Lk
    L = sorted(L, key = lambda x: (len(x), x))
    # print(L)
    return L

def gen_association_rules(transactions, L):
    f = open(output_file, 'w')
    for itemset in L:
        if len(itemset) < 2:
            continue
        for num in range(1,len(itemset)):
            subsets = list(combinations(itemset, num))
            for subset in subsets:
                A = set(subset)
                B = set(itemset) - A
                num_itemset = 0
                num_A = 0
                num_B = 0
                for transaction in transactions:
                    if set(itemset) <= set(transaction):
                        num_itemset+=1
                    if A <= set(transaction):
                        num_A+=1
                        if B<=set(transaction):
                            num_B+=1
                sup = num_itemset/len_transactions*100
                conf = num_B/num_A*100
                sup = decimal.Decimal(sup).quantize(decimal.Decimal('1.00'))
                conf = decimal.Decimal(conf).quantize(decimal.Decimal('1.00'))
                A = list(sorted(A, key = lambda x: x))
                B = list(sorted(B, key = lambda x: x))

                str_A = str(A).replace(" ", "")
                str_A = str_A.replace("[", "")
                str_A = str_A.replace("]", "")
                str_B = str(B).replace(" ", "")
                str_B = str_B.replace("[", "")
                str_B = str_B.replace("]", "")
                f.write("{%s}\t{%s}\t%.2f\t%.2f\n" % (str_A,str_B,sup,conf))
    f.close()

# apriori(transactions, min_sup)
gen_association_rules(transactions, apriori(transactions, min_sup))