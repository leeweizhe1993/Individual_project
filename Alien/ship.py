# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 10:25:42 2017

@author: Li
"""

import pygame

class Ship():
    
    def __init__(self, screen):
        '''
        初始化飞船并设置位置
        '''
        self.screen = screen
        
        #加载飞船图像并获取外接矩形
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        
        #将飞船置于底部中央
        self.rect.centerx = self.screen_rect.centerx        #矩形中心点X坐标
        self.rect.bottom = self.screen_rect.bottom        #矩形底部y坐标
        
    def blitme(self):
        '''
        在指定位置绘制飞船
        '''
        self.screen.blit(self.image, self.rect)
        