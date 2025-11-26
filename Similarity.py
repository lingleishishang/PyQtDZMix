#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:03:05 2023

@author: liufangbin
"""
import numpy as np
def Similarity(pdpA,pdpB):
    SimAB = np.sum((np.sqrt(pdpA*pdpB)))
    return SimAB
