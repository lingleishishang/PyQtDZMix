#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 15:57:18 2023

@author: liufangbin
"""
import numpy as np
def R2(x,y):
    A=x
    B=y
    
    Len_A=len(A)
    
    Amean=np.mean(A)
    Bmean=np.mean(B)
    
    Acov=np.zeros(len(A))
    Bcov=np.zeros(len(B))
    
    for i in range(Len_A):
        Acov[i]=A[i]-Amean
    for i in range(Len_A):
        Bcov[i]=B[i]-Bmean
        
    mult=Acov*Bcov
    numerator = np.sum(mult)
    
    Acov2 = Acov*Acov
    sumAcov2 = np.sum(Acov2)
    Bcov2 = Bcov*Bcov;
    sumBcov2 = np.sum(Bcov2)
    mult2 = sumAcov2*sumBcov2
    denominator = np.sqrt(mult2);

    r = numerator/denominator

    r2 = r*r
    return r2
    
    