import numpy as np
import scipy
import math
import scipy.integrate as si
import scipy.optimize as so

V=[]
B=[0]*B*N
Z=[0]*B*N
Q=[0]*B*N
val=[0]*B*N
LB=[0]*B*N

# bank account limit : random number (range to be decided) matrix of size BxT
L=[][]

# lower reserved value rt(0) range and values to be decided.

R=[]*B*T 

# distribution function for valuation.. variable:x 
# exponential distribution

def valuations():
		V.clear()
		while(1):
			a=np.random.exponential(1)
			if(a>1 and a<4):
				V.append(a)
				if(len(V)==10):
					break
		print("valuations ",V)
		print("")


###########################################################################################################################
####################################### 1.FUNCTIONS FOR MECHANISM 2 OF THE DOUBLE RESERVE AUCTION ########################


#integrand or 1-F(v) where F(v) is the distribution function.

def integrand(x):
	return 1-(math.exp(-x))

# function to find the integration of the integrand from low to up.

def integVal(lowl,upl):
    val,err = scipy.integrate.quad(integrand, lowl,upl )
    return val

# dynamic reserved value function

def resVal(sp,b,t): ## t is added newly for stage integration to be taken care.
	if(sp!=0):
		return findrt(sp,R,b,t)
	else:
		return R[b][t]

# function to find the reserve price for non-zero spend.
# lower limit of "the" integration with spent value as the result and rt(0) as upper limit

def findrt(sp,R,iter1,iter2):
	sol=so.fsolve(solveforll,1,args=(sp,R,iter1,iter2))
	return sol[0]

#function to solve for lower limit.

def solveforll(x,sp,R,iter1,iter2):
	return si.quad(integrand, x, R[iter1][iter2])[0]-sp

# allocattion Rule

def allocationRule(V,B,t):
	for b in range(0,10):
		R[b][t]=resVal(spendPolicy(B,b,t),b,t)
		if(V[b][t]>R[b][t]):
			Z[b][t]=1
	print("allocation" ,Z)

def paymentRule(V,Z,B,t):	
	for b in range(0,10):
		Q[b][t]=Z[b][t]*resVal(spendPolicy(B,b,t),b,t)
	print("payment rule ",Q)

def spendPolicy(B,b,t):
	return B[b][t]

def depositPolicy(R,Z,B,L,t):
	for b in range(0,10):
		val[b][t+1]=integVal(0,R[b][t+1])

		LB[b][t+1]=min(L[b][t+1],val[b][t+1])

		D=Z[b][t]*LB[b][t+1]

		B[b][t]=B[b][t]+D-spendPolicy(B,b,t)

	print ("Balance after deposit ", B)
	print ("L bar after deposit ", LB)

# run loop for t stages calling the respective functions.
# for 1 to T :
# call valuations.
# call allocation rule.
# call payment policy.
# call spendpolicy.
# call deposit policy.
# calculate the total revenue that is generated. (need to discuss on how it is to be done)


#####################################################################################################################################
################################################# 1.END #############################################################


##################################################################################################################################
##################################### 2.oPTIMAL REVENUE CALCULATION. ###########################################################

alp=[0]*N*T

def alphdet(B,LB):
	for b in range (0,N):
		if(B[b][1]==LB[b][1]):  ###  LB[b][t]=min(L[b][t],val[b][t])
			alp[b][1]=1
		else:
			alp[b][1]=0

		for t in range (1,T):
			alp[b][t+1]=1-alp[b][t]*distribFunc(resVal(LB,b,t))-(1-alp[b][t])*distribFunc(resVal(0,b,t))

def rhoh(u):
	return u*(1-distribFunc(u))


def maxim(t):
	mx=R[0][t]
	for b in range (0,N):
		if (R[b][t]>mx):
			mx=R[b][t]
	return mx


def Kt(alp,b,t):
	return alp[b][t]*(rhoh(resVal(LB,b,t))-rhoh(resVal(0,b,t))+integVal(resVal(LB,b,t),resVal(0,b,t)))

def esrev():
	for b in range (0,N):
		bm=maxim(T) ## determines maximum of resVal(0,b,t) among all the buyers.
		H[T]=Kt(alp,bm,T)+rhoh(resVal(0,bm,T))
		for t in range (T-1,1,-1):
			bm=maxim(t)
			H[t]=Kt(alp,bm,t)+rhoh(resVal(0,bm,t))+H[t+1]

	print("Estimated revenue ", H[1])