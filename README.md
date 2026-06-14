# Flappy Bird AI (NeuroEvolution of Augmenting Topologies)

An autonomous agent trained to play Flappy Bird using NeuroEvolution of Augmenting Topologies (NEAT) and Pygame.

## Overview

This project implements a self-learning agent to play Flappy Bird. Instead of hardcoding jumping thresholds, the agent uses a feedforward neural network evolved over multiple generations. Once the network reaches a score threshold of 50, the best genome is serialized and saved.

## How it Works

### 1. Neural Network Input Features
The feedforward neural network accepts three input parameters:
*   **Bird Y-Coordinate**: The vertical position of the bird on the screen.
*   **Distance to Top Pipe**: The absolute distance from the bird to the bottom edge of the upper pipe.
*   **Distance to Bottom Pipe**: The absolute distance from the bird to the top edge of the lower pipe.

### 2. Genetic Algorithm & Fitness Function
*   **Base Fitness**: The bird accumulates a fitness score of `+0.1` for every frame it remains alive.
*   **Obstacle Clearance**: The bird is rewarded with `+5` fitness points for each pipe successfully passed.
*   **Failure Penalty**: A penalty of `-1` is subtracted from its fitness if the bird collides with a pipe or boundary.
*   **Generational Mutation**: Genomes mutate, perform crossover, and split into species across generations based on configuration parameters.

## File Structure

```
flappy_bird/
├── Font/                               # Font assets for display text
│   ├── PixelifySans-Bold.ttf
│   ├── PixelifySans-Medium.ttf
│   └── PixelifySans-VariableFont_wght.ttf
├── imgs/                               # Game sprites (bird, pipes, background)
│   ├── base.png
│   ├── bg.png
│   ├── bird1.png
│   ├── bird2.png
│   ├── bird3.png
│   └── pipe.png
├── applied_model.py                    # Plays game autonomously using the trained model
├── config-feedforward.txt              # NEAT genetic algorithm configuration
├── flappy.pickle                       # Serialized trained model
├── game.py                             # Manual playable version of the game
└── main.py                             # NEAT training loop script
```

## Requirements

Install dependencies using pip:
```bash
pip install pygame neat-python
```

## Running the Code

### Train the AI:
```bash
python main.py
```

### Run the Trained Agent:
```bash
python applied_model.py
```

### Play the Game Manually:
```bash
python game.py
```
