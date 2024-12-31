import pygame 
import neat
import time
import random
import os


# NOTE if velocity or displacement is negative it means we are moving upwards, and vice versa
#for displacement the origin is at the center of the game screen, while for velocity its at top left
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

GO_FONT = pygame.font.Font("Font/PixelifySans-Medium.ttf", 90)
STAT_FONT = pygame.font.Font("Font/PixelifySans-Medium.ttf", 55)

TITLE_FONT = pygame.font.Font("Font/PixelifySans-Medium.ttf", 80)
SMALL_FONT = pygame.font.Font("Font/PixelifySans-Medium.ttf", 40)
INS_FONT = pygame.font.Font("Font/PixelifySans-Medium.ttf", 35)
SYS_FONT = pygame.font.SysFont("comicsans", 40)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.img_count = 0

        self.height = self.y
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # formula for displacement (in pixels) where tick_count is basically the time since last jump, this gives us a parabolic trajectory
        # NOTE we haven't considered any acceleration here
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        #for tilting the bird upwards or downwards
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # a counter for the animation of images
        self.img_count += 1

        # we have already set animation time to 5
        # this loops through the images according to the animation time(img_count), making a flapping animation
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0    

        # condition to check if the bird crosses the centre of the screen
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
             
        #for rotating the image, new_rect to rotate it from center (since default: topleft)     
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect)

    #for collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    

class Pipe:
    GAP = 200
    VEL = 7

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(40, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        # top and bottom are the y co-ordinates

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        #when ever there is a collision they return None

        if t_point or b_point:
            return True
        
        return False
    
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # LOGIC imagine two boxes with x1 and x2 as their top left points
        """Now as the boxes rotate across the game screen, in the case where the top right end of the 1st box crosses the end of the screen
        we will place it at co-ordinate x2 + width (ie end of the second)"""

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


class Button:

    def start_screen(self, win):
        win.blit(BG_IMG, (0,0))
        title_text = TITLE_FONT.render("FLAPPY BIRD" , 1, (0, 0, 0))
        win.blit(title_text, ((WIN_WIDTH - title_text.get_width()) // 2, 200))
        text = SMALL_FONT.render("Press S to Start", 1, (0, 0, 0))
        win.blit(text, ((WIN_WIDTH- text.get_width()) // 2, 550))
        pygame.display.update()

    def restart_button (self, win):
        text = SMALL_FONT.render("Press R to Restart", 1, (0, 0, 0))
        win.blit(text, ((WIN_WIDTH- text.get_width()) // 2, 650))

    def res_is_pressed(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:
            return True
        return False

    def start_is_pressed(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_s]:
            return True
        return False



def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    ins_text = INS_FONT.render("Press SPACE to jump", 1, (0, 0, 0))
    base.draw(win)
    bird.draw(win)
    win.blit(ins_text, ((WIN_WIDTH - ins_text.get_width()) // 2, WIN_HEIGHT - ins_text.get_height() - 32))
    pygame.display.update()

def game_over_2(win, score):
    win.blit(BG_IMG, (0, 0))
    go_text = GO_FONT.render("GAME OVER" , 1, (0, 0, 0))
    score_text = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    centerx = WIN_WIDTH - go_text.get_width()
    center_score = WIN_WIDTH - score_text.get_width()
    win.blit(go_text, (centerx/2, 300))
    win.blit(score_text, (center_score/2, 400))

    button = Button()
    button.restart_button(win)
    if button.res_is_pressed():
        return True

    pygame.display.update()
    
    

def main():
    collision = False
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(650)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    win2 = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    high_score = 0

    run = True    
    

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        
        add_pipe = False
        rem = []
        
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_a:
        #         print("Jump")
        #         # bird.jump()

        for pipe in pipes:
            if pipe.collide(bird):
                collision = True
                break

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:  
                pipe.passed = True
                add_pipe = True
                
            pipe.move()

        if add_pipe and not collision:
            score +=1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        bird.move()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            bird.jump()
            # print("Jump")
        base.move()

        if bird.y + bird.img.get_height() >= 730:
            collision = True

        if collision:
            break
 
        draw_window(win, bird, pipes, base, score)
    
    while run and collision:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        restart = game_over_2(win, score)

        if restart:  # If the player chooses to restart, re-call the main function
            main()

        # game_over_2(win2, score)

    pygame.quit()
    quit()

start_win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
start_screen = Button()
start_screen.start_screen(start_win)

while True:    
    
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    if start_screen.start_is_pressed():
        main()



    
