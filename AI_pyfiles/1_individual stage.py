import numpy as np
import scipy
import math
import scipy.integrate as si
import scipy.optimize as so

V=[]
B=[0]*10
Z=[0]*10
Q=[0]*10
val=[0]*10

L=[2]*5
for i in range(5,10):
	L.append(1)

# print("L" ,L) 
#define !!!!!!!!! DISCUS WITH ABHINANDAN


R=[2]*10 
#define !!!!!!!!!
# distribution function for valuation.. variable:x

def distribFunc():
		V.clear()
		while(1):
			a=np.random.exponential(1)
			if(a>1 and a<4):
				V.append(a)
				if(len(V)==10):
					break
		print("valuations ",V)
		print("")

def integrand(x):
	return 1-(math.exp(-x))

# allocattion Rule

def allocationRule(V,B):
	for b in range(0,10):
		resVal(spendPolicy(B,b),b)
		if(V[b]>R[b]):
			Z[b]=1
	print("allocation" ,Z)

def spendPolicy(B,b):
	S=B[b]
	B[b]-=S
	return S

def resVal(sp,b):
	if(sp!=0):
		return lowLimit(sp,R,b)

def func(x,sp,R,iter):
	return si.quad(integrand, x, R[iter])[0]-sp

def lowLimit(sp,R,iter):
	sol=so.fsolve(func,1,args=(sp,R,iter))
	return sol[0]

def paymentRule(V,Z,B):	
	for b in range(0,10):
		Q[b]=Z[b]*R[b]
	print("payment rule ",Q)

def depositPolicy(R,Z,B,L):
	for b in range(0,10):
		val[b]=integVal(b)
	# print("val ",val)
	# print ("")
	for b in range(0,10):
		D=Z[b]*min(L[b],val[b])
		B[b]+=D
	print ("Balance after deposit ", B)

def integVal(iter):
    val,err = scipy.integrate.quad(integrand, 0, R[iter] )
    return val

def findR(B):
	for b in range(0,10):
		sp=spendPolicy(B,b)
		print(sp)
		resVal(sp,b)
print("STAGE 1")
print("Reserve price",R)
print ("")
distribFunc()
allocationRule(V,B)
print("")
paymentRule(V,Z,B)
print("")
depositPolicy(R,Z,B,L)
P=[]
for b in range(0,10):
	P.append(Q[b]+B[b])
print("payment after stage 1",P)
print ("")


print("STAGE 2")
print("Reserve price",R)
print ("")
distribFunc()
allocationRule(V,B)
print ("")
paymentRule(V,Z,B)
print ("")
depositPolicy(R,Z,B,L)

P=[]
for b in range(0,10):
	P.append(Q[b]+B[b])
print("payment after stage 2", P)