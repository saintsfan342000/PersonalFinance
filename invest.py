import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


import numpy as n
from scipy.optimize import minimize

# How much am I investing?
newmoney = 0

# What are my current MF balances
## ORDERED HOW VANGUARD LISTS THEM
VEXAX = 41631.76 #35931.83
VFWAX = 60216.65 #51317.32
VFSAX = 28563.49 #29335.94
VWIUX = 52273.12 #51999.64
VLCAX = 87155.73
VSMAX = 0 #6540.38
VTIAX = 0 #10285.54
VTSAX = 0 #89634.92

# ORDER for algorithm
# VTSAX, VSMAX, VTIAX, VFSAX, VWIUX
curbal = n.array([
    VTSAX+VLCAX,
    VSMAX+VEXAX,
    VTIAX+VFWAX,
    VFSAX,
    VWIUX
    ])

#curbal = n.array([33,17,22,12,15-2.])
#newmoney = 100 - curbal.sum()

# Realtime changes to these funds (as percentage)
curchange = n.array(
          [-8.63, 
           -10,
           -10.41,
           -11.13,
           -5.78
           ], dtype=float
          )*0

curchange*=.01
curchange+=1


# Adjust curbals
curbal *= curchange


# Desired AA
des_alloc = n.array([.33, .17, .23, .12, .15])

# Actual allocation given current balances
actual = curbal/curbal.sum()

# My errer function.
# Square of errors of actual AA with new money compared to perfect alloc
def best(alloc, newmoney, curbal, des_alloc):
    newbal = alloc*newmoney + curbal
    new_alloc = newbal / newbal.sum()
    # Traditional L2 norm
    # I get somewhat different answers based on whether I take the sqrt or not
    #return n.sqrt( ((new_alloc - des_alloc)**2).sum() )
    #return ((new_alloc - des_alloc)**2).sum() 
    # "Normalized L2" a la http://optimalrebalancing.tk/explanation.html
    # Does not differ based on whether I take a sqrt
    return (( (new_alloc/des_alloc - 1)**2 ).sum())

# Bounds for my pcts of new money
bounds = [(0,1)]*len(curbal)

# Constraining my new money allocs such that they sum to 1
confun = lambda x: x.sum() - 1
cons = {'type':'eq', 'fun':confun}

res = minimize(fun=best, 
               x0=des_alloc,
               args=(newmoney,curbal,des_alloc),
               bounds=bounds,
               constraints=(cons,),
               method='SLSQP',
               options={'maxiter':100, 'disp':False})


x = res.x
y = x*newmoney + curbal

funds = 'VTSAX, VSMAX/VEXAX, VTIAX/VFWAX, VFSAX, VWIUX'.split(', ')

colnames = 'Fund,Current Aloc,New Alloc,Amt to Buy.'.split(',')
row_format ="{:>15}"
print((row_format*len(colnames)).format(*colnames))
for fname, cural, newal, buy in zip(funds, actual, y/y.sum(), x*newmoney):
    buyfmt = '{:>15.2f}'
    #print(buy)
    if buy < 1:
        buy = '--'
        buyfmt = '{:>15}'
    print(('{:>15s}{:>15.1f}%{:>15.1f}%' + buyfmt).format(
        fname, cural*100, newal*100, buy))
