from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# 依據按鍵做相對指令

def init():
    pygame.init()
    pygame.set_caption("Tello")
    win = pygame.display.set_mode((400, 400))

def getKey(keyName):
    ans = False
    for eve in pygame.event.get(): pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    pygame.display.update()
    return ans

def main():
    if getKey("LEFT"):
        print("Left key")


if __name__ == '__main__':
    init()
    while True:
        main()