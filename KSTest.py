#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 10:13:48 2025

@author: liufangbin
"""

import numpy as np

def kstest2b_tnc(x1, x2, alpha=0.05, tail='unequal', n=None):
    """
    Two-sample Kolmogorov-Smirnov goodness-of-fit hypothesis test (MATLAB version translation).
    
    Parameters
    ----------
    x1, x2 : array_like
        Input vectors (samples).
    alpha : float, optional
        Significance level (default=0.05).
    tail : {'unequal', 'smaller', 'larger'}, optional
        Type of test (default='unequal').
    n : int, optional
        Sample size (both n1 and n2 assumed = n). 
        If None, defaults to len(x1).
    
    Returns
    -------
    H : int
        Test decision (1 = reject null, 0 = do not reject).
    pValue : float
        Approximate p-value.
    KSstatistic : float
        Kolmogorov-Smirnov statistic.
    """

    # Convert to numpy arrays and remove NaN
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    x1 = x1[~np.isnan(x1)]
    x2 = x2[~np.isnan(x2)]

    if len(x1) == 0:
        raise ValueError("Sample x1 contains no data.")
    if len(x2) == 0:
        raise ValueError("Sample x2 contains no data.")

    if not (0 < alpha < 1):
        raise ValueError("alpha must be between 0 and 1.")

    # Handle tail parameter
    if isinstance(tail, str):
        tail = tail.lower()
        if tail == 'unequal':
            tail_code = 0
        elif tail == 'smaller':
            tail_code = -1
        elif tail == 'larger':
            tail_code = 1
        else:
            raise ValueError("tail must be 'unequal', 'smaller', or 'larger'.")
    elif isinstance(tail, (int, float)):
        if tail in [-1, 0, 1]:
            tail_code = int(tail)
        else:
            raise ValueError("tail must be -1, 0, or 1.")
    else:
        raise ValueError("Invalid tail parameter.")

    # 默认 n = len(x1) (但 MATLAB 代码里是外部传入)
    if n is None:
        n = len(x1)
    n1 = n2 = n

    # 构造经验 CDF (注意：原始 MATLAB 代码用的是 cumsum(x)/sum(x)，并非标准经验CDF)
    sumCounts1 = np.cumsum(x1) / np.sum(x1)
    sumCounts2 = np.cumsum(x2) / np.sum(x2)

    sampleCDF1 = sumCounts1[:-1]
    sampleCDF2 = sumCounts2[:-1]

    # 计算检验统计量
    if tail_code == 0:      # two-sided
        deltaCDF = np.abs(sampleCDF1 - sampleCDF2)
    elif tail_code == -1:   # one-sided, smaller
        deltaCDF = sampleCDF2 - sampleCDF1
    elif tail_code == 1:    # one-sided, larger
        deltaCDF = sampleCDF1 - sampleCDF2

    KSstatistic = np.max(deltaCDF)

    # 有效样本量
    ne = n1 * n2 / (n1 + n2)
    lam = max((np.sqrt(ne) + 0.12 + 0.11 / np.sqrt(ne)) * KSstatistic, 0)

    # 计算 p-value
    if tail_code != 0:  # one-sided
        pValue = np.exp(-2 * lam * lam)
    else:  # two-sided
        j = np.arange(1, 102)
        pValue = 2 * np.sum((-1) ** (j - 1) * np.exp(-2 * lam * lam * j ** 2))
        pValue = min(max(pValue, 0), 1)

    H = int(alpha >= pValue)  # 决策

    return H, pValue, KSstatistic