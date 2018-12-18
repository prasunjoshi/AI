import numpy as np
import scipy
import math
import scipy.integrate as si
import scipy.optimize as so
import random
import csv,os
import pandas as pd


T=4 # The total number of stages the auction is held on.
N=10 # Number of buyers taking part. can be changes to have different buyers in each stage.
V=[] # Valuations of each buyers. In this code taken from

B={} #Variable to store bank balance for each buyer.

Z={} #Indicates which buyer is assigned the product in each stage.

Q={} #Variable to store Payment made by the buyers(who are alloted the product) in each stage.

val={} # valt as in equation (19) in the paper reffered.

LB={} # varaible as in equation (19) used to calculate the deposit amount.

# all the above variables after V are calculated for two different types of auctions.

#index 0 is for the standard double Reserve Auction (Mechanism 2 in section 3.)
#index 1 is for HDR auction (Mechanism 3 in section 4.)
B[0]=[[0 for b in range (N)]for t in range (T)]
B[1]=[[0 for b in range (N)]for t in range (T)]


Z[0]=[[0 for b in range (N)]for t in range (T)]
Z[1]=[[0 for b in range (N)]for t in range (T)]


Q[0]=[[0 for b in range (N)]for t in range (T)]
Q[1]=[[0 for b in range (N)]for t in range (T)]


val[0]=[[0 for b in range (N)]for t in range (T)]
val[1]=[[0 for b in range (N)]for t in range (T)]


LB[0]=[[0 for b in range (N)]for t in range (T)]
LB[1]=[[0 for b in range (N)]for t in range (T)]

# for every run of the code we call the fucntion setL to set the Bank Account Limit to a value 0.012 units
# higher than the previous run. This is done so as to get a revenue v/s limit graph for both index 0 and index 1.
# the value of both revenues are stored in a file w.r.t corresponding limit.

def setL():
	global l
	if(os.path.exists("Plot_H.csv")==0):
		writer=csv.writer(open('Plot_H.csv','w'))
		writer.writerow(["Limit","Mechanism 2 Revenue","HDR Revenue","Optimal Revenue","Efficiency M2","Efficiency HDR"])
		l=-0.012
	else:
		l=0
		filename="Plot_H.csv"
		df=pd.read_csv(filename)
		if (df.empty==0):
			print(df)
			# print(df.iloc[0]["Limit"])
			l=df.iloc[-1]["Limit"]

	global L
	L=[[l+0.012 for b in range (N)]for t in range (T)]

	print("\nL ",L[0][0])



# function to ramdomly decide the Valuation of N buyers from an exponential distribution

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
######################## 1.FUNCTIONS FOR MECHANISM 2/MECHANISM 3 OF THE DOUBLE RESERVE AUCTION ###########################


#integrand or 1-F(v) where F(v) is the distribution function.
# This F(v) can be replaced by some other function which tells us an equation that defines how a given set of 
# valuations are distributed.

def integrand(x):
	return 1-(math.exp(-x))

# function to find the integration of the integrand from lower limit to upper limit.

def integVal(lowl,upl):
    val,err = scipy.integrate.quad(integrand,lowl,upl)
    return val



# used to dynamically change the reserved value for the later stages as defined in section 3.

def resVal(sp,t,b):
	if(sp!=0):
		return findrtnz(sp,storedRt0[t])
	else:
		return storedRt0[t]

# dynamic reserved value function for HDR Mechanism 3.

def resVal_H(sp,t,b):
	if(sp!=0):
		return findrtnz(sp,storedRt0[t])
	elif (sp==L[t][b]):
		return 0
	else:
		return storedRt0[t]

# function to find the reserve price for non-zero spend.
# lower limit of "the" integration with spent value as the result and rt(0) as upper limit

def findrtnz(sp,R):
	sol=so.fsolve(solveforll,0,args=(sp,R))
	return sol[0]

#function to solve for lower limit.

def solveforll(x,sp,R):
	return si.quad(integrand, x, R)[0]-sp

#for the functions below variable "fl" is a flag used to indicate Mechanism 2 and Mechanism 3.

# allocattion Rule

def allocationRule(V,B,t,fl):
	for b in range(N):
		if(V[b]>resVal(spendPolicy(B,t,b,fl),t,b)):
			Z[fl][t][b]=1
	print("allocation at stage0 ",t+1," : ",Z[fl][t])

# deciding the payment value each stage each mechanism each buyer

def paymentRule(V,Z,B,t,fl):	
	for b in range(N):
		Q[fl][t][b]=Z[fl][t][b]*resVal(spendPolicy(B,t,b,fl),t,b)
	print("payment rule at stage ",t," : ",Q[fl][t])

# deciding the spend policy according to the definition of DR.

def spendPolicy(B,t,b,fl):
	return B[fl][t][b]

# set the amount to be deposited to the bank account of every buyer at the end of each stage using equation (19)

def depositPolicy(Z,B,L,t,fl):
	for b in range(N):
		val[fl][t+1][b]=integVal(0,resVal(0,t,b))

		LB[fl][t+1][b]=min(L[t+1][b],val[fl][t+1][b])

		D=Z[fl][t][b]*LB[fl][t+1][b]

		B[fl][t+1][b]=B[fl][t][b]+D-spendPolicy(B,t,b,fl)
	print ("Balance after deposit for stage ", t," : ", B[fl][t])
	print ("L bar after deposit ", LB[fl])

# the below variable stores the initial reserved price, mentioned as rt(0) in the paper, for each stage.
storedRt0=[]

def doubleReserve():
	global sm0
	global sm1
	# below two variables are used to store the maximum revenue for each mechanisms.
	sm0=0
	sm1=0
	storedRt0.clear()
	for t in range (T):
		print("\nStage ",t+1,"\n")
		V=valuations()

		# reserved price calculated as average of all the valuations plus half of the max valuation.
		# this is done so as to make sure that some values are there in the randomly selected valuations
		# which pass the initial allocation. 
		# For a well defined dataset R will have a proper value depending on the product and for every stage.

		R=sum(V)/len(V)+max(V)/2
		storedRt0.append(R)
		print("R ",R)
		allocationRule(V,B,t,0)
		allocationRule(V,B,t,1)
		paymentRule(V,Z,B,t,0)
		paymentRule(V,Z,B,t,1)
		if(t!=T-1):
			depositPolicy(Z,B,L,t,0)
			depositPolicy(Z,B,L,t,1)
		sm0+=max(Q[0][t])
		sm1+=max(Q[1][t])
	print ("Mechanism 2 Revenue ",sm0)
	print ("HDR Revenue (Mechanism 3) ",sm1)



## explaination of the above double reserve function.
# run loop for t stages calling the respective functions.
# for 1 to T :
# call valuations.
# call allocation rule.
# call payment rule.
# call deposit policy.
# calculate the total revenue that is generated.


#####################################################################################################################
################################################# 1.END #############################################################


#####################################################################################################################
##################################### 2.OPTIMAL REVENUE CALCULATION. ################################################

# This part implements section 3.2 which gives the optimal revenue which is h[0], i.e from stage 0 to T.


alp=[[0 for b in range (N)]for t in range (T)]

def alphdet(B,LB,alp):
	for b in range (0,N):
		if(B[0][1][b]==LB[0][1][b]):  ###  LB[b][t]=min(L[b][t],val[b][t])
			alp[1][b]=1
		else:
			alp[1][b]=0
		for t in range (2,T-1):
			alp[t+1][b]=1-alp[t][b]*math.exp(-1*resVal(LB[0][t][b],t,b))-(1-alp[t][b])*math.exp(-1*resVal(0,t,b))

def rhoh(u):
	return u*(1-math.exp(-u))

def Kt(alp,t,b,storedRt0):
	kt=alp[t][b]*(rhoh(resVal(LB[0][t][b],t,b))-rhoh(storedRt0[t])+integVal(resVal(LB[0][t][b],t,b),storedRt0[t]))
	return kt

H=[[0 for b in range (N)]for t in range (T)]

def esrev(storedRt0,alp):
	for b in range(N):
		rt0=max(storedRt0) ## determines maximum of resVal(0,b,t) among all the buyers.
		H[T-1][b]=Kt(alp,T-1,b,storedRt0)+rhoh(rt0)
		# print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",H[T-1][b])
		for t in range (T-2,-1,-1):
			H[t][b]=Kt(alp,t,b,storedRt0)+rhoh(rt0)+H[t+1][b]

#The function below is used for calculation of h[0] for the buyer who provides maximum value.

def optimal():
	alphdet(B,LB,alp)
	esrev(storedRt0,alp)
	print("Estimated revenue ", max(H[0]))

#####################################################################################################################
################################################# 2.END #############################################################

####################################################################################################################
################################### 3. Storing Limits and revenues accordingly.#####################################

def writetocsv():
	writer = csv.writer(open('Plot_H.csv', 'a'))
	lt = float(str(L[0][0]).encode('utf-8'))

	m2rev = float(str(sm0).encode('utf-8'))

	m3rev = float(str(sm1).encode('utf-8'))

	esrev = float(str(max(H[0])).encode('utf-8'))

	effm2 = float(str(sm0/max(H[0])).encode('utf-8'))

	effhdr = float(str(sm1/max(H[0])).encode('utf-8'))

	writer.writerow([lt,m2rev,m3rev,esrev,effm2,effhdr])

def counts():
	df=pd.read_csv("Plot_H.csv")
	r=df.shape[0]
	return r

#####################################################################################################################
################################################## EOC. #############################################################