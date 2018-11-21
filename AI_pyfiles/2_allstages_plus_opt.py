import numpy as np
import scipy
import math
import scipy.integrate as si
import scipy.optimize as so
import random
import csv

T=4
N=10

V=[]
B=[[0 for b in range (N)]for t in range (T)]
Z=[[0 for b in range (N)]for t in range (T)]
Q=[[0 for b in range (N)]for t in range (T)]
val=[[0 for b in range (N)]for t in range (T)]
LB=[[0 for b in range (N)]for t in range (T)]

# bank account limit : random number (range to be decided) matrix of size TxB
l=random.uniform(0,1.2)
L=[[l for b in range (N)]for t in range (T)]
# for b in range (10):
#     for t in range (4):
#         L[t][b]=l
#     l+=0.12
print("\n L ",L[0][0])

# lower reserved value rt(0) range and values to be decided.

#R=[1 for t in range (T)]

# distribution function for valuation.. variable:x 
# exponential distribution

def valuations():
		V.clear()
		while(1):
			a=np.random.exponential(1)
			V.append(a)
			if(len(V)==N):
				break
		print("valuations ",V)
		return V


###########################################################################################################################
############################## 1.FUNCTIONS FOR MECHANISM 2 OF THE DOUBLE RESERVE AUCTION ##################################


#integrand or 1-F(v) where F(v) is the distribution function.

def integrand(x):
	return 1-(math.exp(-x))

# function to find the integration of the integrand from low to up.

def integVal(lowl,upl):
    val,err = scipy.integrate.quad(integrand,lowl,upl)
    return val

# dynamic reserved value function

def resVal(sp,t,b):
	if(sp!=0):
		return findrtnz(sp,R)
	else:
		return R

# function to find the reserve price for non-zero spend.
# lower limit of "the" integration with spent value as the result and rt(0) as upper limit

def findrtnz(sp,R):
	sol=so.fsolve(solveforll,0,args=(sp,R))
	return sol[0]

#function to solve for lower limit.

def solveforll(x,sp,R):
	return si.quad(integrand, x, R)[0]-sp

# allocattion Rule

def allocationRule(V,B,t):
	for b in range(N):
		if(V[b]>resVal(spendPolicy(B,t,b),t,b)):
			Z[t][b]=1
	print("allocation at stage ",t," : ",Z[t])

def paymentRule(V,Z,B,t):	
	for b in range(N):
		Q[t][b]=Z[t][b]*resVal(spendPolicy(B,t,b),t,b)
	print("payment rule at stage ",t," : ",Q[t])

def spendPolicy(B,t,b):
	return B[t][b]

def depositPolicy(Z,B,L,t):
	for b in range(N):
		val[t+1][b]=integVal(0,resVal(0,t,b))

		LB[t+1][b]=min(L[t+1][b],val[t+1][b])

		D=Z[t][b]*LB[t+1][b]

		B[t+1][b]=B[t][b]+D-spendPolicy(B,t,b)

	print ("Balance after deposit for stage ", t," : ", B[t])
	print ("L bar after deposit ", LB)

storedRt0=[]

for t in range (T):
	print("\nStage ",t+1,"\n")
	V=valuations()
	R=random.uniform(min(V),max(V))
	storedRt0.append(R)
	print("R ",R)
	allocationRule(V,B,t)
	paymentRule(V,Z,B,t)
	if(t!=T-1):
		depositPolicy(Z,B,L,t)

sm=0
for t in range(T):
	sm+=max(Q[t])

rb=[]
# for b in range(N):
# 	sm=0
# 	for t in range (1,T):
# 		sm+=Q[t][b]
# 	rb.append(sm)
print ("MAX revenue",sm)
# print("Revenue from Mechanism 2 is ",rb)



# run loop for t stages calling the respective functions.
# for 1 to T :
# call valuations.
# call allocation rule.
# call payment rule.
# call deposit policy.
# calculate the total revenue that is generated. (need to discuss on how it is to be done)


#####################################################################################################################
################################################# 1.END #############################################################


#####################################################################################################################
##################################### 2.OPTIMAL REVENUE CALCULATION. ################################################






alp=[[0 for b in range (N)]for t in range (T)]

def alphdet(B,LB,alp):
	for b in range (0,N):
		if(B[1][b]==LB[1][b]):  ###  LB[b][t]=min(L[b][t],val[b][t])
			alp[1][b]=1
		else:
			alp[1][b]=0

		for t in range (2,T-1):
			alp[t+1][b]=1-alp[t][b]*math.exp(-1*resVal(LB[t][b],t,b))-(1-alp[t][b])*math.exp(-1*resVal(0,t,b))


def rhoh(u):
	return u*(1-math.exp(-u))


# def maxim(t):
# 	mx=0
# 	for b in range (0,N):
# 		if (R[b][t]>mx):
# 			mx=R[b][t]
# 	return mx


def Kt(alp,t,b,storedRt0):
	kt=alp[t][b]*(rhoh(resVal(LB[t][b],t,b))-rhoh(storedRt0[t])+integVal(resVal(LB[t][b],t,b),storedRt0[t]))
	return kt

H=[[0 for b in range (N)]for t in range (T)]

def esrev(storedRt0,alp):
	for b in range(N):
		rt0=max(storedRt0) ## determines maximum of resVal(0,b,t) among all the buyers.
		H[T-1][b]=Kt(alp,T-1,b,storedRt0)+rhoh(rt0)
		# print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",H[T-1][b])
		for t in range (T-2,-1,-1):
			H[t][b]=Kt(alp,t,b,storedRt0)+rhoh(rt0)+H[t+1][b]


alphdet(B,LB,alp)
esrev(storedRt0,alp)
print("Estimated revenue ", max(H[0]))

#with open(r'Plot.csv', 'ab', newline='') as csvfile:
writer = csv.writer(open('Plot.csv', 'a'))
#fieldnames = ['Limit','Max Revenue','Estimated Revenue']
#writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#row = []
lt = str(L[0][0]).encode('utf-8')
mxrev = str(sm).encode('utf-8')
esrev = str(max(H[0])).encode('utf-8')
writer.writerow([lt,mxrev,esrev])