import numpy as np
import random
import copy
import matplotlib.pyplot as plt
import itertools
import json


# Determines who won, if no one won returns False
def winner(boadrd_hash):
    if np.sum(boadrd_hash[:3]) == 3 or np.sum(boadrd_hash[3:6]) == 3 or np.sum(boadrd_hash[6:]) == 3:
        return 1
    elif np.sum(boadrd_hash[:3]) == -3 or np.sum(boadrd_hash[3:6]) == -3 or np.sum(boadrd_hash[6:]) == -3:
        return -1
    elif np.sum(boadrd_hash[ : :3]) == 3 or np.sum(boadrd_hash[1: :3]) == 3 or np.sum(boadrd_hash[2: :3]) == 3:
        return 1
    elif np.sum(boadrd_hash[ : :3]) == -3 or np.sum(boadrd_hash[1: :3]) == -3 or np.sum(boadrd_hash[2: :3]) == -3:
        return -1
    elif np.sum (boadrd_hash[ : :4]) == 3 or np.sum(boadrd_hash[2:7:2]) == 3:
        return 1
    elif np.sum (boadrd_hash[ : :4]) == -3 or np.sum(boadrd_hash[2:7:2]) == -3:
        return -1
    else:
        return False


# Creates a dictionary with rewards
def generation_rewards_dict():
    cells = [1, 0, -1]
    rewards = {}
    combinations = np.array(list(itertools.product(cells, repeat = 9)))
    for comb in combinations:
        if winner(comb) == 1:
            comb = str(comb).strip('[]')
            rewards[comb] = 1
        elif winner(comb) == -1:
            comb = str(comb).strip('[]')
            rewards[comb] = 0
        else:
            comb = str(comb).strip('[]')
            rewards[comb] = 0.5
    write_to_file(rewards)


# Writes the dictionary to a file
def write_to_file(rewards):
    with open('rewards.txt', 'w') as f:
        f.write(json.dumps(rewards))


# Gets a dictionary from a file
def get_rewards_dict():
    with open('rewards.txt', 'r') as f:
     rewards = json.loads(f.read())
     return rewards




#Generates a matrix and creates a list of empty cells
def board_start():
    board = np.zeros((3, 3), dtype=int)
    empty_cells = []
    for i, row in enumerate(board):
        for j, coll in enumerate(row):
            if board[i][j] == 0:
                empty_cells.append((i, j))
    return empty_cells, board


# Returns a random move to an empty cell
def random_choice(empty_cells):
    action_id = random.randint(0, len(empty_cells) - 1)
    action = empty_cells[action_id]
    empty_cells.remove(action)
    return action, empty_cells


# The agent decides which move to choose
def player(empty_cells, board, saved_states):
    action = 0
    if random.random() < 0.1:
        action, empty_cells = random_choice(empty_cells)
    else:
        choice = []
        for cell in empty_cells:
            new_state = copy.deepcopy(board)
            new_state[cell] = 1
            new_state_hash = str(new_state.reshape(3*3)).strip('[]')
            choice.append({'action': cell, 'award': saved_states.get(new_state_hash)})
        max_award = choice[0]['award']
        max_award = choice[0]['award']
        action = choice[0]['action']
        for i in choice:
            if i['award'] >= max_award:
                max_award = i['award']
                action = i['action']
        empty_cells.remove(action)
    return action, empty_cells


# The teacher goes to a random or winning cell
def teacher(empty_cells, board):
    action = 0
    for cell in empty_cells:
        new_state = copy.deepcopy(board)
        new_state[cell] = -1
        if winner(new_state) == -1:
            action = cell
    if action == 0:
        action, empty_cells = random_choice(empty_cells)
    else:
        empty_cells.remove(action)
    return action, empty_cells


# Checks if the game is over
def game_over(empty_cells, board):
    board_hash = copy.deepcopy(board.reshape(3*3))
    winner1 = winner(board_hash)
    if winner1 == False and len(empty_cells) == 0:
        return 0
    return winner1



#Adds a new state to the saved states and to the hash of the game
def rewise_rewards(board, rewards, game_hash):
    state_hash = copy.deepcopy(str(board.reshape(3*3)).strip('[]'))
    game_hash.append({'state': state_hash, 'reward': rewards.get(state_hash)})
    if len(game_hash) > 1:
        game_hash[-2]['reward'] += 0.1 * (game_hash[-1]['reward'] - game_hash[-2]['reward'])
    return game_hash


# Adds a new state to the hash of the game, recalculates the values of the previous state
def write_rewards(game_hash, saved_states):
    for state in game_hash:
        saved_states[state['state']] = state['reward']
    return saved_states


# Plays a certain number of rounds
def play(rounds, agent_status):
    if agent_status == 'да':
        generation_rewards_dict()
    rewards = get_rewards_dict()
    games_number = []
    wins_number = []
    agent_wins = 0
    for game in range(rounds):
        empty_cells, board = board_start()
        game_hash = []
        game_hash = rewise_rewards(board, rewards, game_hash)
        win = 0
        while True:
            teacher_action, empty_cells = teacher(empty_cells, board)
            board[teacher_action] = -1
            game_hash = rewise_rewards(board, rewards, game_hash)
            winner = game_over(empty_cells, board)
            if type(winner) != type(False):
                rewards = write_rewards(game_hash, rewards)
                agent_wins +=winner
                break
            player_action, empty_cells = player(empty_cells, board, rewards)
            board[player_action] = 1
            game_hash = rewise_rewards(board, rewards, game_hash)
            winner = game_over(empty_cells, board)
            if type(winner) != type(False):
                rewards = write_rewards(game_hash, rewards)
                agent_wins +=winner
                break
            wins_number.append(agent_wins)
            games_number.append(game)
    write_to_file(rewards)
    print('Разница между победами и поражениями: ', agent_wins)
    return(wins_number, games_number)


if __name__ == "__main__":
    agent_status = input('Начать обучение агента заново? ')
    rounds = int(input('Сколько раундов сыграть агенту для обучения? '))
    y, x = play(rounds, agent_status)
    plt.plot(x, y)
    plt.ylabel('Разница между победами и поражениями')
    plt.xlabel('Количество игр')
    plt.savefig('graph.png')
