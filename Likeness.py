#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:09:46 2023

@author: liufangbin
"""
import numpy as np
def Likeness(A,B):
    LikeAB=1-np.sum(np.absolute(A-B))/2
    return LikeAB