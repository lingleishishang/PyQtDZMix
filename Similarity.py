#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:03:05 2023

@author: liufangbin
"""
import numpy as np
def Similarity(pdpA,pdpB):
    """
    计算两个概率分布的相似度（Bhattacharyya系数）
    
    返回值范围：[0, 1]
    - 1 表示两个分布完全相同
    - 0 表示两个分布完全不重叠
    """
    # 确保非负
    pdpA = np.maximum(pdpA, 1e-10)
    pdpB = np.maximum(pdpB, 1e-10)
    
    # 归一化
    pdpA = pdpA / np.sum(pdpA)
    pdpB = pdpB / np.sum(pdpB)
    
    # 计算 Bhattacharyya 系数
    SimAB = np.sum(np.sqrt(pdpA * pdpB))
    return SimAB
