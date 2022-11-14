##------------------------------------

import numpy as np
from scipy.linalg import eig


##------------------------------------


# our control parameters
#_gammadot = 1.0
#_tau = 2.4
#_tau_a = 0.4

## wavelength of the linear mode
#k = 1


def ev(k,_gammadot,_tau,_tau_a,):
	"""Takes in a set of parameters and returns the spectrum that 
	corresponds to these parameter values.

	Args:
		k (float): wavenumber
		_gammadot (float): external shear rate
		_tau (float): liquid crystal relaxation time
		_tau_a (float): activity time scale

	Returns:
		list[complx numbers]: a (cleaned of any infinities) list of eigenvalues
	"""
	# resolution
	M = 50

	# parameters we don't really vary
	_llambda = 1.0
	_ell_over_W_squared = 0.1
	_tmp_const = (_llambda*(_gammadot*_tau)**2)/(1+(_gammadot*_tau)**2)

	##------------------------------------
	mode_number = 94 #79
	do_plot_mode = 0

	##------------------------------------

	II = np.identity(M,dtype='d')

	cbar = np.ones(M,dtype='d')
	cbar[0] = 2.0
	cbar[M-1] = 2.0

	ygl = np.zeros(M,dtype='d')
	for m in range(M):
		ygl[m] = np.cos(np.pi*m/(M-1))

	D1 = np.zeros((M,M),dtype='d')
	for l in range(M):
		for j in range(M):
			if l != j:
				D1[l,j] = cbar[l]*((-1)**(l+j))/(cbar[j]*(ygl[l]-ygl[j]))

	for j in range(1,M-1):
		D1[j,j] = -0.5*ygl[j]/(1.0-ygl[j]*ygl[j])

	D1[0,0] = (2.0*(M-1)*(M-1)+1.0)/6.0
	D1[M-1,M-1] = -D1[0,0]

	# The factor 2 takes care of the domain being from -1/2 to 1/2
	D1 = 2*D1

	D2 = np.dot(D1,D1)

	## Auxiliary matrices

	Lmin = D2 - k*k*II 
	Lplus = D2 + k*k*II 


	## LHS

	## Variable layout
	## psi[0:M] Qxx[M:2*M] Qxy[2*M:3*M] 

	Rpsi  = slice(0*M,1*M)
	RQxx  = slice(1*M,2*M)
	RQxy  = slice(2*M,3*M)


	LHS = np.zeros((3*M,3*M),dtype='D')

	# Stokes equation

	LHS[Rpsi,Rpsi] = np.dot(Lmin,Lmin)
	LHS[Rpsi,RQxx] = -(2*1j*k/(_gammadot*_tau_a))*D1
	LHS[Rpsi,RQxy] = -Lplus/(_gammadot*_tau_a)

	## Qxx equation

	LHS[RQxx,Rpsi] = -_tmp_const*Lmin - 2*1j*k*_llambda*_gammadot*_tau*D1
	LHS[RQxx,RQxx] = II - _ell_over_W_squared*Lmin + 1j*k*_gammadot*_tau*ygl*II
	LHS[RQxx,RQxy] = -_gammadot*_tau*II

	## Qxy equation

	LHS[RQxy,Rpsi] = _gammadot*_tau*_tmp_const*Lmin - _llambda*_gammadot*_tau*Lplus
	LHS[RQxy,RQxx] = _gammadot*_tau*II
	LHS[RQxy,RQxy] = II - _ell_over_W_squared*Lmin + 1j*k*_gammadot*_tau*ygl*II


	RHS = np.zeros((3*M,3*M),dtype='D')

	RHS[RQxx,RQxx] = -_tau*II
	RHS[RQxy,RQxy] = -_tau*II

	## Boundary conditions

	LHS[0]     = np.zeros(3*M,dtype='D') # Psi vanishes at the boundaries
	LHS[1]     = np.zeros(3*M,dtype='D') # and dy(Psi) (?) vanishes at the boundaries
	LHS[M-2]   = np.zeros(3*M,dtype='D') # how does this code account for no-slip?
	LHS[M-1]   = np.zeros(3*M,dtype='D')

	LHS[0,0]      = 1.0
	LHS[1,Rpsi]   = D1[0]
	LHS[M-2,Rpsi] = D1[M-1]
	LHS[M-1,M-1]  = 1.0

	LHS[M]     = np.zeros(3*M,dtype='D') # dy(Qxx) vanishes at the boundaries
	LHS[2*M-1] = np.zeros(3*M,dtype='D')

	LHS[M,RQxx]     = D1[0]
	LHS[2*M-1,RQxx] = D1[M-1]

	LHS[2*M]   = np.zeros(3*M,dtype='D') # dy(Qxy) vanishes at the boundaries
	LHS[3*M-1] = np.zeros(3*M,dtype='D')

	LHS[2*M,RQxy]   = D1[0]
	LHS[3*M-1,RQxy] = D1[M-1]


	RHS[0]     = np.zeros(3*M,dtype='D')
	RHS[1]     = np.zeros(3*M,dtype='D')
	RHS[M-2]   = np.zeros(3*M,dtype='D')
	RHS[M-1]   = np.zeros(3*M,dtype='D')
	RHS[M]     = np.zeros(3*M,dtype='D')
	RHS[2*M-1] = np.zeros(3*M,dtype='D')
	RHS[2*M]   = np.zeros(3*M,dtype='D')
	RHS[3*M-1] = np.zeros(3*M,dtype='D')


	_spec = eig(LHS,RHS,left=0,right=1)

	_eig_list = _spec[0]
	_modes_list = _spec[1]

	_clean_eig_list = list(filter(lambda ev: np.isfinite(ev), _eig_list))
	return _clean_eig_list

#print("at k={}, gammadot={}, tau={}, tau_a={}, fastest growth rate:{:.4f} @ freq={:.4f}"\
#.format(k,_gammadot,_tau,_tau_a,np.real(max_val),np.imag(max_val)))
#print("at k={}, tBar={}, aBar={}, fastest growth rate:{:.4f} @ freq={:.4f}"\
#.format(k,_gammadot*_tau,1/(_gammadot*_tau_a),np.real(max_val),np.imag(max_val)))

"""
f=open('spectrum.txt','w')
for i in range(len(_eig_list)):
	if np.isfinite(_eig_list[i]):
	f.write('%20.18f %20.18f\n'%(np.real(_eig_list[i]),np.imag(_eig_list[i]))    )
f.close()

f=open('list.txt','w')
for i in range(len(_eig_list)):
	f.write('%d %20.18f %20.18f\n'%(i,np.real(_eig_list[i]),np.imag(_eig_list[i]))    )    
f.close()
  """


## OUTPUT
"""
_my_mode=_modes_list[:,mode_number]

_psi=_my_mode[0:M]
_Qxx=_my_mode[M:2*M]
_Qxy=_my_mode[2*M:3*M]

if do_plot_mode:

	f=open('psi.field','w')
	for m in range(M):
	f.write('%f %20.18f %20.18f\n'%(ygl[m],np.real(_psi[m]),np.imag(_psi[m])))
	f.close()

	f=open('Qxx.field','w')
	for m in range(M):
	f.write('%f %20.18f %20.18f\n'%(ygl[m],np.real(_Qxx[m]),np.imag(_Qxx[m])))
	f.close()

	f=open('Qxy.field','w')
	for m in range(M):
	f.write('%f %20.18f %20.18f\n'%(ygl[m],np.real(_Qxy[m]),np.imag(_Qxy[m])))
	f.close()
"""

def max_ev_kg_grid(ks, gds, tau, tau_a):
	#assert len(ks)==len(gds), "Input vectors must have equal sizes for grid!"
	# ks and gds are two vectors with EQUAL SIZES
	kv, gv = np.meshgrid(ks, gds)

	# N - number of rows, M - number of columns
	Nk, Mk = len(kv), len(kv[0])
	Ng, Mg = len(gv), len(gv[0])

	evv = np.zeros([Nk, Mk])

	for i in range(Nk):
		for j in range(Mk):
			k = kv[i][j]
			gd = gv[i][j]
			evv[i][j] = np.max(np.real(ev(k,gd,tau,tau_a)))

	return evv

