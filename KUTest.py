#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 10:05:34 2025

@author: liufangbin
"""

import numpy as np

def kuipertest2_tnc(x1, x2, n):
    """
    Python translation of kuipertest2_tnc (MATLAB version).
    
    Parameters
    ----------
    x1 : array_like
        Input array (sample or pdf-like data).
    x2 : array_like
        Input array (sample or pdf-like data).
    n : int
        Effective sample size (both n1 and n2 assumed = n).
    
    Returns
    -------
    p : float
        Kuiper test p-value (approximate).
    V : float
        Kuiper statistic value.
    """
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    n1, n2 = n, n

    # CDFs（注意：原 MATLAB 代码不是严格经验 CDF，而是归一化累积和）
    sampleCDF1 = np.cumsum(x1) / np.sum(x1)
    sampleCDF2 = np.cumsum(x2) / np.sum(x1)   # MATLAB 里也是 sum(x1)，可能是笔误
    
    deltaCDF1 = sampleCDF2 - sampleCDF1
    maxdeltaCDF1 = np.max(deltaCDF1)

    deltaCDF2 = sampleCDF1 - sampleCDF2
    maxdeltaCDF2 = np.max(deltaCDF2)

    V = maxdeltaCDF1 + maxdeltaCDF2

    ne = (n1 * n2) / (n1 + n2)
    lam = (np.sqrt(ne) + 0.155 + (0.24 / np.sqrt(ne))) * V

    if lam < 0.4:
        p=1
        #h=0
    else:
        j = np.arange(1, 102)
        pare = 4 * lam * lam * (j ** 2) - 1
        expo = np.exp(-2 * lam * lam * (j ** 2))
        argo = pare * expo
        p = 2 * np.sum(argo)

    return p, V