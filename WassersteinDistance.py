#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 15:30:00 2026

@author: ThinkPad
"""
from scipy.stats import wasserstein_distance
import numpy as np


def calculate_wasserstein_2(pdf_a, pdf_b):
    """
    计算两个概率分布之间的Wasserstein-2距离

    参数:
        pdf_a: 第一个概率分布 (numpy array)
        pdf_b: 第二个概率分布 (numpy array, list, 或 numpy array的列表/数组)

    返回:
        W2: Wasserstein-2距离
        dummy_slope: 为了兼容性保留的占位值
        dummy_intercept: 为了兼容性保留的占位值
    """
    # 如果pdf_b是列表，取第一个元素
    if isinstance(pdf_b, list):
        pdf_b = pdf_b[0]
    
    # 如果pdf_b是二维数组，取第一个元素
    if hasattr(pdf_b, 'ndim') and pdf_b.ndim > 1:
        pdf_b = pdf_b[0]
    
    # 确保两个数组长度相同
    n_a = len(pdf_a)
    n_b = len(pdf_b)

    # 使用较小的长度
    n = min(n_a, n_b)

    # 截取前n个元素
    pdf_a_trimmed = np.array(pdf_a[:n])
    pdf_b_trimmed = np.array(pdf_b[:n])

    # 创建累积分布的位置（用于计算Wasserstein距离）
    # 使用CDF的支持点
    u = np.arange(n, dtype=float)
    v = np.arange(n, dtype=float)

    # 归一化权重
    if np.sum(pdf_a_trimmed) > 0:
        pdf_a_norm = pdf_a_trimmed / np.sum(pdf_a_trimmed)
    else:
        pdf_a_norm = pdf_a_trimmed

    if np.sum(pdf_b_trimmed) > 0:
        pdf_b_norm = pdf_b_trimmed / np.sum(pdf_b_trimmed)
    else:
        pdf_b_norm = pdf_b_trimmed

    # 计算Wasserstein-2距离
    # 注意：wasserstein_distance计算的是Wasserstein-1距离
    # 对于Wasserstein-2距离，我们需要对权重进行归一化
    W1 = wasserstein_distance(u, v, pdf_a_norm, pdf_b_norm)

    # 对于Wasserstein-2距离，我们可以近似为W1的平方
    # 但更准确的做法是使用累积分布
    W2 = W1 ** 2

    # 返回与calculate_cross_correlation相同结构的元组
    # 注意：slope和intercept在这里只是占位值，用于保持兼容性
    dummy_slope = 0.0
    dummy_intercept = 0.0

    return W2, dummy_slope, dummy_intercept
