# Flappy Bird using NEAT

## Introduction

"Flappy Bird" revolutionized the mobile gaming industry in 2013. In this project, I have developed an intelligent agent to play Flappy Bird autonomously using the NeuroEvolution of Augmenting Topologies (NEAT) algorithm. This project was part of the AIDI 2001 course under the guidance of Sadia Malik.

![My Image](images/my_image.png)

## Project Overview

The aim of this project is to demonstrate the effectiveness of a genetic algorithm in training an intelligent agent to play Flappy Bird. Traditionally, reinforcement learning has been used for such tasks, but here we leverage the NEAT algorithm to evolve neural networks that control the bird in the game.

## Features

- **Autonomous Gameplay:** The intelligent agent plays Flappy Bird without user interaction.
- **Genetic Algorithm:** Uses NEAT, a genetic algorithm, to evolve the neural network controlling the bird.
- **Python Implementation:** The project is implemented in Python using the Pygame library.

## Setup and Installation

To run the game and train the model, you'll need to install the following Python packages:

```bash
pip install pygame
pip install neat-python
```

## Project Structure

- **FlappyBird.py:** Contains the main classes used in the game.
- **Train.py:** Used for training the agent.
- **Run.py:** Used for viewing how the trained agent works.

## How to Run

1. **Train the Agent:**

   ```bash
   python Train.py
   ```

2. **Run the Trained Agent:**

   ```bash
   python Run.py
   ```

## Detailed Explanation

### Game Development

The primary module used for development is Pygame. The game consists of three main objects:

- **Bird:** Handles the bird's movements and interactions.
- **Pipe:** Manages the obstacles in the game.
- **Base:** Manages the game's ground base movement.

### Training the Model

- **Fitness Function:** Combines collision penalty, alive time, and game score.
- **Inputs:** Horizontal distance between the bird and the pipe, vertical distance between the bird and the top/bottom pipes.
- **Neural Network:** A shallow neural network with one hidden layer.

### Key Hyperparameters

- **Fitness Threshold:** Determines if the solution is good enough to end the evolution process.
- **Population Size:** Number of genomes per generation (set to 50).
- **Survival Threshold:** Proportion of genomes selected for reproduction per species (set to 0.2).

## References

- [NEAT Overview by K. Stanley](https://www.cs.ucf.edu/~kstanley/neat.html)
- [NEAT Paper by K. Stanley](https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf)
- [Flappy Bird Design Tutorial](https://www.youtube.com/watch?v=jfU92kiVnFI)
- [Pygame Documentation](https://www.pygame.org/wiki/tutorials)
- [Dino Game AI Tutorial](https://github.com/kilian-kier/Dino-Game-AI)
