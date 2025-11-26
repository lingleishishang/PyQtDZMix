# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 15:20:36 2025

@author: ThinkPad
"""
from scipy.stats import  linregress

def calculate_cross_correlation(pdf_a, pdf_b):
    """计算两个PDF之间的交叉相关系数(R²)并返回回归线参数"""
    slope, intercept, r_value, p_value, std_err = linregress(pdf_a, pdf_b)
    return r_value**2, slope, intercept