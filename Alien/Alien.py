# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 11:09:00 2017

@author: Li
"""
import sys
import pygame
from settings import Settings
from ship import Ship
import game_functions as gf

# 初始化游戏并创建一个屏幕对象
def run_game():    
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width,
                                     ai_settings.screen_height))
    pygame.display.set_caption('Alien Invasion')
    
    #创建一艘飞船
    ship = Ship(screen)
    
    #开始主循环
    while True:    
        gf.check_events(ship)
        gf.udpate_screen(ai_settings, screen, ship)
       
run_game()