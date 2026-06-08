# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 08:36:40 2025

@author: ThinkPad
"""
import numpy as np
from scipy.stats import linregress
def calculate_qq_plot(data1, data2, num_points=1000):
    """计算Q-Q图数据点并返回R²值"""
    # 计算分位数
    quantiles = np.linspace(0, 1, num_points)
    q1 = np.quantile(data1, quantiles)
    q2 = np.quantile(data2, quantiles)
    
    # 计算Q-Q图的R²值
    slope, intercept, r_value, p_value, std_err = linregress(q1, q2)
    r_squared = r_value**2
    
    return q1, q2, r_squared, slope, intercept