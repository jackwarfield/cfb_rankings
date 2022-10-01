import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

def g (phi):
    return 1/np.sqrt(1 + 3*phi**2 / np.pi**2)

def Ej (mu, muj, phij):
    return 1/(1 + np.exp(-g(phij) * (mu-muj)))

def v (mu, muj, phij):
    E_val = Ej(mu,muj,phij)
    return 1/(g(phij)**2 * E_val * (1 - E_val))

def f (x, delta, phi, vi, a, tau):
    topl = np.exp(x) * (delta**2 - phi**2 - vi - np.exp(x))
    botl = 2 * (phi**2 + vi + np.exp(x))**2
    right = (x-a)/tau**2
    return (topl/botl - right)

def iterSigPr (sig, delta, phi, vi, tau, eps=1e-6):
    a = np.log(sig**2)
    A = a
    if (delta**2 > phi**2 + vi):
        B = np.log(delta**2 - phi**2 - vi)
    else:
        k = 1
        while (f(a-k*tau, delta, phi, vi, a, tau) < 0):
            k += 1
        B = a - k*tau
    fA = f(A, delta, phi, vi, a, tau)
    fB = f(B, delta, phi, vi, a, tau)
    while np.abs(B - A) > eps:
        C = A + (A-B) * fA / (fB - fA)
        fC = f(C, delta, phi, vi, a, tau)
        if fC*fB < 0:
            A = B
            fA = fB
        else:
            fA = fA/2.0
        B = C
        fB = fC
    return np.exp(A/2)

def update_ratings (id1, id2, t1win, df, ot=False):
    table = df
    tau = 0.2

    r1 = table[table.id == id1]['rating'].values[0]
    rd1 = table[table.id == id1]['rd'].values[0]
    sig1 = table[table.id == id1]['volatility'].values[0]
    mu1 = (r1 - 1500)/173.7178
    phi1 = rd1/173.7178

    r2 = table[table.id == id2]['rating'].values[0]
    rd2 = table[table.id == id2]['rd'].values[0]
    sig2 = table[table.id == id2]['volatility'].values[0]    
    mu2 = (r2 - 1500)/173.7178
    phi2 = rd2/173.7178

    v1 = v(mu1, mu2, phi2)
    v2 = v(mu2, mu1, phi1)

    if (ot == False):
        if (t1win == True):
            s1,s2 = 1,0
        elif (t1win == False):
            s1,s2 = 0,1 

    delta1 = v1 * g(phi2) * (s1 - Ej(mu1,mu2,phi2))
    delta2 = v2 * g(phi1) * (s2 - Ej(mu2,mu1,phi1))
    
    sigPr1 = iterSigPr (sig1, delta1, phi1, v1, tau)
    sigPr2 = iterSigPr (sig2, delta2, phi2, v2, tau)

    phiStar1 = np.sqrt(phi1**2 + sigPr1**2)
    phiStar2 = np.sqrt(phi2**2 + sigPr2**2)

    phiPr1 = 1/np.sqrt(1/phiStar1**2 + 1/v1) 
    phiPr2 = 1/np.sqrt(1/phiStar2**2 + 1/v2) 

    muPr1 = mu1 + phiPr1**2 * g(phi2) * (s1 - Ej(mu1,mu2,phi2))
    muPr2 = mu2 + phiPr2**2 * g(phi1) * (s2 - Ej(mu2,mu1,phi1))

    rPr1 = 173.7178*muPr1 + 1500
    rdPr1 = 173.7178*phiPr1
    rPr2 = 173.7178*muPr2 + 1500
    rdPr2 = 173.7178*phiPr2

    r1,rd1,sig1 = rPr1, rdPr1, sigPr1
    r2,rd2,sig2 = rPr2, rdPr2, sigPr2

    table.loc[table.id == id1, 'rating'] = r1
    table.loc[table.id == id1, 'rd'] = rd1
    table.loc[table.id == id1, 'volatility'] = sig1

    table.loc[table.id == id2, 'rating'] = r2
    table.loc[table.id == id2, 'rd'] = rd2
    table.loc[table.id == id2, 'volatility'] = sig2

    return table
