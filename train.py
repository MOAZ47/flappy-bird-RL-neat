from FlappyBird import *
import neat
import pickle

def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0                           # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)   # create feed forward NN
        nets.append(net)
        birds.append(Bird(230,350))                         # bird object; all start at same position
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0  # pipe index is set to zero, we are focusing on one pipe at a time
        if len(birds) > 0:
            # determine whether to use the first or second pipe on the screen for neural network input
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # if we have passed the pipe, then use focus on second pipe
                pipe_ind = 1

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1  # every second bird is alive get 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()               # will produce random pipes moving towards bird
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1   # every time any bird hits pipe subtract 1 from fitness score
                    nets.pop(birds.index(bird))    # NN associated with collided bird removed
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))   # removes that bird object which collided

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # if pipe is completely off screen
                rem.append(pipe)                        # add pipe to remove list

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1               # we have passed a pipe increase score
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5  # every bird that passes pipes; we add 5 to Fitness score
            pipes.append(Pipe(WIN_WIDTH))   # add new pipe to pipes list

        for r in rem:               # once passed a pipe remove previous pipe from remove list
            pipes.remove(r)

        for bird in birds:         # check if any of the birds in generation has hit the ground
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:  # bird hit the floor
                nets.pop(birds.index(bird))   # NN associated with collided bird removed
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))  # removes that bird object which collided

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)
        
        if score > 80:
            break

        """
        # break if score gets large enough
        if score > 80:
            #pickle.dump(nets[0], open("bestbird.pickle", "wb"))
            pickle.dump()
            break
        """


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    local_dir = os.path.dirname(__file__)
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    #winner = p.run(eval_genomes, 50)
    config.Winner = p.run(eval_genomes, 50)
    
    ##############################################################################################
    with open(os.path.join(local_dir, 'ai.pkl'), "wb") as f:
        pickle.dump(config.Winner, f)
        f.close()
    # show final stats
    print('\nBest genome:\n{!s}'.format(config.Winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)