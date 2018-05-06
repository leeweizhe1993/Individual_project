# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 19:47:45 2017

@author: Li
"""

import sys
import pygame

def check_events():
    '''响应键盘和鼠标事件'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                #向右移动飞船
                ship.rect.centerx += 1
            
def update_screen(ai_settings, screen, ship):
    '''更新屏幕图像并切换到新屏幕'''
    #每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color)
    ship.blitme()
    
    #让最近绘制的屏幕可见
    pygame.display.flip()
