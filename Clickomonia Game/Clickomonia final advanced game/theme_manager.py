
import pygame
import os, math
class ThemeManager:
    def __init__(self):
        self.index=0
        self.themes=[
            ("Tropical Sunset","theme1.png"),
            ("Orange Lagoon","theme3.png"),
            ("Fantasy Forest","forest1.png"),
            ("Cartoon Forest","theme4.jpg")
        ]
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.images=[pygame.image.load(os.path.join(base_path, f)).convert() for _,f in self.themes]
    def next_theme(self):
        self.index=(self.index+1)%len(self.themes)
    def name(self):
        return self.themes[self.index][0]
    def draw_background(self,screen,ticks):
        bg=pygame.transform.smoothscale(self.images[self.index],screen.get_size())
        screen.blit(bg,(0,0))
        w,h=screen.get_size()
        s=pygame.Surface((w,h),pygame.SRCALPHA)
        if self.index==2:
            for i in range(40):
                x=(i*97 + ticks*0.03)%w
                y=(i*53)%h
                a=120+int(60*math.sin(i+ticks*0.002))
                pygame.draw.circle(s,(255,255,180,a),(int(x),int(y)),2)
        elif self.index==3:
            for i in range(6):
                x=(ticks*0.04+i*220)%(w+100)-50
                pygame.draw.circle(s,(255,255,255,35),(int(x),120+i*20),25)
        screen.blit(s,(0,0))
