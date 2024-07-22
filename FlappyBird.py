import pygame
import random
import os
import time
import neat
#import visualize
import pickle
pygame.font.init()        # init font

WIN_WIDTH = 600           # Dimensions of UI
WIN_HEIGHT = 800
FLOOR = 730

STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# pygame.transform.scale2x --> makes 2 times bigger
# pygame.image.load  --> loads image
# we move base_img which makes it look moving
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0

class Bird:
    """
    Bird class representing the flappy bird
    """
    MAX_ROTATION = 25   # how much bird tilt in degrees
    IMGS = bird_images  # use bird images
    ROT_VEL = 20        # how much we rotate in every frame or every time the bird moves
    ANIMATION_TIME = 5  # how long we show bird animation

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0             # degrees to tilt, how much is tilted
        self.tick_count = 0       # physics of bird
        self.vel = 0
        self.height = self.y
        self.img_count = 0        # to know which image we are showing
        self.img = self.IMGS[0]   # refers to bird image

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5          # random number selected, negative velocity to go upwards
        self.tick_count = 0       # tracks when we last jumped
        self.height = self.y      # where the bird jumped from

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1     # denotes we have moved

        # for downward acceleration   s = ut + 0.5 at^2
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement
        # moves in a parabolic path --> -10.5 + 1.5 = -9 --> -7 --> -5 --> -3 --> 0 --> 2

        # terminal velocity; ensures we are not moving too far either up or down
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement                     # change y position

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:                                              # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1      # how many times we have shown image

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:          # count < 5     show 1st image
            self.img = self.IMGS[0]                        
        elif self.img_count <= self.ANIMATION_TIME*2:      # count < 10
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:      # count < 15
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:      # count < 20
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:  # count < 21    show 1st image
            self.img = self.IMGS[0]
            self.img_count = 0                             # reset the count

        # so when bird is nose diving it isn't flapping, display 2nd image for this
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2  # when we jump up start at count = 10; display 2nd image


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)

class Pipe():
    """
    represents a pipe object
    """
    GAP = 200                 # space between pipes
    VEL = 5                   # how fast pipes are moving

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0             # random height

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)    # flip the pipe image
        self.PIPE_BOTTOM = pipe_img

        self.passed = False        # has the bird passed the pipe

        self.set_height()          #

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL       # change x wrt velocity

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()                                     # get mask
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)              # get mask
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)        # get mask
        top_offset = (self.x - bird.x, self.top - round(bird.y))        # how far away are masks from each other
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))  # how far away are masks from each other

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)         # point of overlap between bird mask and bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset)               # point of overlap between bird mask and top pipe

        if b_point or t_point:                                          # if collinding then it returns true
            return True

        return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5                                # same as pipe velocity
    WIDTH = base_img.get_width()           # how wide
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0                     # one of the base images starts at 0
        self.x2 = self.WIDTH            # the other base image starts after the 1st image

    def move(self):
        """
        move floor so it looks like its scrolling
        we use two images and move left
        :return: None
        """
        self.x1 -= self.VEL                      # move the image wrt velocity
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:             # if 1st image has completely gone outta screen, put it behind 2nd image
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH      # if 2nd image has completely gone outta screen, put it behind 1st image

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:       # draw all pipes
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))  # show score
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))   # show generation
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))  # show alive
    win.blit(score_label, (10, 50))

    pygame.display.update()





