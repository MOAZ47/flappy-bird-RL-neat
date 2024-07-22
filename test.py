from FlappyBird import *

import neat
import pickle

genome_path = os.path.join(os.path.dirname(__file__), 'bestbird.pickle')
genome = pickle.load(open(genome_path, 'rb'))

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward.txt')
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)


def draw_test_window(win, bird, pipes, base, score, pipe_ind):
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

    win.blit(bg_img, (0,0))

    for pipe in pipes:       # draw all pipes
        pipe.draw(win)

    base.draw(win)

    bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))  # show score
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()

def main(genome, config):
    score = 0

    bird = Bird(230, 350)     # ADDING BIRD
    base = Base(FLOOR)        # ADDING BASE
    pipes = [Pipe(700)]       # ADDING PIPES
    #win = pygame.display.set_mode(WIN_WIDTH, WIN_HEIGHT)


    net = neat.nn.FeedForwardNetwork.create(genome, config)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        ############  PIPE CHECK  ######################################
        pipe_ind = 0  # pipe index is set to zero, we are focusing on one pipe at a time
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # if we have passed the pipe, then use focus on second pipe
            pipe_ind = 1

        ################################################################

        ############  BIRD MOVE  #######################################
        bird.move()

        # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
        output = net.activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

        if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
            bird.jump()

        ################################################################

        ############  PIPE ADDITION and REMOVAL  #######################
        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()   # MOVING PIPE

            if pipe.collide(bird, WIN):
                pygame.quit()
                quit()
                break
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # if pipe is completely off screen
                rem.append(pipe)                        # add pipe to remove list

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))  # add new pipe to pipes list
        for r in rem:               # once passed a pipe remove previous pipe from remove list
            pipes.remove(r)
        ################################################################

        ############  EXIT GAME WHEN BIRD HITS FLOOR  ##################
        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:  # bird hit the floor
            pygame.quit()
            quit()
            break
        ##############################################################

        base.move()  # MOVING BASE
        draw_test_window(WIN, bird, pipes, base, score, pipe_ind)

if __name__ == '__main__':
    main([genome], config)