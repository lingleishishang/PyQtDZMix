#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:09:46 2023

@author: liufangbin
"""
import numpy as np


def SircombeHazeltonDistance(A, B):
    """
    计算 Sircombe–Hazelton (2004, Sedimentary Geology) 距离
    
    Sircombe–Hazelton 距离是一种用于比较概率分布的度量，
    其范围从 0（完全相同）到正无穷（完全不同）。
    
    参数:
        A: 第一个概率分布 (numpy array)
        B: 第二个概率分布 (numpy array)
    
    返回:
        D_SH: Sircombe–Hazelton 距离
    """
    # 确保两个分布都是有效的概率分布（非负且和为1）
    # 如果有负值，设为极小值
    A = np.maximum(A, 1e-10)
    B = np.maximum(B, 1e-10)
    
    # 归一化
    A = A / np.sum(A)
    B = B / np.sum(B)
    
    # 计算 Bhattacharyya 系数
    bc = np.sum(np.sqrt(A * B))
    
    # 计算 Sircombe–Hazelton 距离
    # D_SH = -log(bc^2) 或者等价地
    D_SH = -2 * np.log(bc)
    
    return D_SH
