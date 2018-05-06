# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 20:12:35 2017

@author: Li
"""

import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((1600, 900))
bg_color = (0, 0, 128)
pygame.display.set_caption('Blue Sky')
screen.fill(bg_color)
pygame.display.flip()
