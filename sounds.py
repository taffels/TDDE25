""" Contains imported sounds """


from pygame.mixer import Sound
import pygame

pygame.mixer.init()

shot_sound = Sound("data/sounds/bulletfire.wav")
hit_sound = Sound("data/sounds/hurt.wav")
wood_sound = Sound("data/sounds/cratehit.wav")
point_sound = Sound("data/sounds/points.wav")