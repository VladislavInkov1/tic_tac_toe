import numpy as np
import random
import copy
import matplotlib.pyplot as plt


#Generates a matrix and creates a list of empty cells
def board_start():
    board = np.zeros((3, 3))
    empty_cells = []
    for i, row in enumerate(board):
        for j, coll in enumerate(row):
            if board[i][j] == 0:
                empty_cells.append((i, j))
    return empty_cells, board


#Returns a random move to an empty cell
def random_choice(empty_cells):
    index = random.randint(0, len(empty_cells) - 1)
    action = empty_cells[index]
    return(action)


#The agent decides which move to choose
def player(empty_cells, board, saved_states):
    action = 0
    if random.random() < 0.1:
        action = random_choice(empty_cells)
    else:
        choice = []
        for cell in empty_cells:
            new_state = copy.deepcopy(board)
            new_state[cell[0]][cell[1]] = -1
            for state in saved_states:
                if state['state'] == new_state:
                    choice.append({'award':state['award'], 'action': cell})
        if len(choice) == 0:
            action = random_choice(empty_cells)
        else:
            max_award = choice[0]['award']
            for i in choice:
                if i['award'] >= max_award:
                    max_award = i['award']
                    action = i['action']
    return action


#The teacher goes to a random or winning cell
def teacher(empty_cells, board):
    for cell in empty_cells:
        new_state = copy.deepcopy(board)
        new_state[cell[0]][cell[1]] = -1
        if winner(new_state) == 1:
            return(cell)
    action = random_choice(empty_cells)
    return action


#Checks if there are empty cells
def game_over(empty_cells):
    if len(empty_cells) == 0:
        return True


#Checks if there is a win
def winner(board):
    for row in board:
        if sum(row) == 3:
            return 1
        elif sum(row) == -3:
            return -1
    if board[0][0] + board[1][0] + board[2][0] == 3 or board[0][1] + board[1][1] + board[2][1] == 3 or board[0][2] + board[1][2] + board[2][2] == 3:
        return 1
    elif board[0][0] + board[1][0] + board[2][0] == -3 or board[0][1] + board[1][1] + board[2][1] == -3 or board[0][2] + board[1][2] + board[2][2] == -3:
            return -1
    diag_sum1 = board[0][0] + board[1][1] + board[2][2]
    diag_sum2 = board[0][2] + board[1][1] + board[2][0]
    diag_sum = max(diag_sum1, diag_sum2, key=abs)
    if diag_sum == 3:
        return 1
    elif diag_sum == -3:
        return -1


#Adds a new state to the saved states and to the hash of the game
def add_new_state(board, saved_states, game_hash):
    state_in_list = False
    for state in saved_states:
        if board == state['state']:
            state_in_list = True
            game_hash.append({'state': copy.deepcopy(board), 'award': state['award']})
    if not state_in_list:
        game_hash.append({'state': copy.deepcopy(board), 'award': 0.5})
        saved_states.append({'state': copy.deepcopy(board), 'award': 0.5})
    return game_hash, saved_states


#Overestimates the rewards
def revaluation_of_values(game_hash, saved_states, win):
    if win == 1:
        game_hash.reverse()
        game_hash[0]['award'] = 0;
        i = 1
        while i < len(game_hash):
            game_hash[i]['award'] += 0.1 * (game_hash[0]['award'] - game_hash[i]['award'])
            i += 1
    elif win == -1:
        game_hash.reverse()
        game_hash[0]['award'] = 1;
        i = 1
        while i < len(game_hash):
            game_hash[i]['award'] += 0.1 * (game_hash[0]['award'] - game_hash[i]['award'])
            i += 1
    for state in saved_states:
        for step in game_hash:
            if state['state'] == step['state']:
                state['award'] = step['award']
    return saved_states


def play(rounds):
    saved_states = []
    games_number = []
    wins_number = []
    agent_wins = 0
    agent_lost = 0
    for i in range(rounds):
        empty_cells, board = board_start()
        game_hash = []
        board = board.tolist()
        game_hash, saved_states = add_new_state(board, saved_states, game_hash)
        win = 0
        while not game_over(empty_cells):
            teacher_action = teacher(empty_cells, board)
            board[teacher_action[0]][teacher_action[1]] = 1
            empty_cells.remove((teacher_action[0], teacher_action[1]))
            game_hash, saved_states = add_new_state(board, saved_states, game_hash)
            if winner(board) == 1:
                win = 1
                break
            elif game_over(empty_cells):
                win = 0.5
                break
            agent_action = player(empty_cells, board, saved_states)
            board[agent_action[0]][agent_action[1]] = -1
            empty_cells.remove((agent_action[0], agent_action[1]))
            game_hash, saved_states = add_new_state(board, saved_states, game_hash)
            if winner(board) == None:
                win = 0.5
                continue
            else:
                win = -1
                break
        if win == -1:
            agent_wins += 1
        elif win == 1:
            agent_lost += 1
        saved_states = revaluation_of_values(game_hash, saved_states, win)
        games_number.append(i)
        wins_number.append(agent_wins - agent_lost)
    print('Агент выиграл: ', agent_wins, ' раз.')
    print('Агент проиграл: ', agent_lost, ' раз.')
    return games_number, wins_number




games_number, wins_number = play(50000)
plt.plot(games_number, wins_number)
plt.ylabel('Разница между победами и поражениями')
plt.xlabel('Количество игр')
plt.savefig('graph.png')
