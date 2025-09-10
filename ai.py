import requests
import json
import numpy as np
import random
import pickle
from collections import defaultdict

URL = "http://localhost:8080"
Q = defaultdict(lambda: np.zeros(9))  # Q[state_tuple] = [values for actions 0-8]
alpha = 0.5  # Learning rate, increased for faster learning
gamma = 0.95  # Discount
epsilon = 0.5  # Start with exploration
ai_wins = 0
opp_wins = 0
draws = 0

def get_state():
    res = requests.get(f"{URL}/state")
    board_list = res.json()['board']
    board_array = np.array(board_list)
    return tuple(board_array.flatten())

def get_winner():
    res = requests.get(f"{URL}/state")
    return res.json()['winner']

def is_full():
    state = get_state()
    return 0 not in state

def get_valid_actions(state_tuple):
    board = np.array(state_tuple).reshape(3, 3)
    valid = [i for i in range(9) if board.flatten()[i] == 0]
    return valid

def choose_action(state_tuple, valid_actions):
    if random.random() < epsilon:
        return random.choice(valid_actions)
    q_values = Q[state_tuple]
    return max(valid_actions, key=lambda a: q_values[a])

def make_move(action):
    row, col = divmod(action, 3)
    requests.post(f"{URL}/move/{row}/{col}")

def random_move():
    state = get_state()
    valid = get_valid_actions(state)
    if valid:
        action = random.choice(valid)
        make_move(action)

def play_ai_move(move_history):
    state = get_state()
    valid = get_valid_actions(state)
    if not valid:
        return None
    action = choose_action(state, valid)
    make_move(action)
    next_state = get_state()
    # Store move for backpropagation
    move_history.append((state, action, next_state))
    return action

def total_games():
    return ai_wins + opp_wins + draws

def train(num_episodes=10000):
    global epsilon, ai_wins, opp_wins, draws
    for ep in range(num_episodes):
        requests.get(f"{URL}/new-game")
        state = get_state()
        move_history = []  # Track (state, action, next_state) for AI moves
        if sum(state) == 0:
            random_move()
        
        while True:
            winner = get_winner()
            if winner != 0 or is_full():
                full_reward = 1 if winner == -1 else (-1 if winner == 1 else 0)
                if winner == -1:
                    ai_wins += 1
                elif winner == 1:
                    opp_wins += 1
                else:
                    draws += 1
                total = total_games()
                ai_win_pct = (ai_wins / total * 100) if total > 0 else 0
                opp_win_pct = (opp_wins / total * 100) if total > 0 else 0
                draw_pct = (draws / total * 100) if total > 0 else 0
                print(f"Episode {ep}: Reward {full_reward} (Winner: {winner}, AI Win%: {ai_win_pct:.2f}, Opp Win%: {opp_win_pct:.2f}, Draw%: {draw_pct:.2f})")
                # Backpropagate end-game reward through AI moves
                for state, action, next_state in reversed(move_history):
                    old_q = Q[state][action]
                    next_max = np.max(Q[next_state]) if get_valid_actions(next_state) else 0
                    Q[state][action] = old_q + alpha * (full_reward + gamma * next_max - old_q)
                break
            
            play_ai_move(move_history)
            
            winner = get_winner()
            if winner != 0 or is_full():
                full_reward = 1 if winner == -1 else (-1 if winner == 1 else 0)
                if winner == -1:
                    ai_wins += 1
                elif winner == 1:
                    opp_wins += 1
                else:
                    draws += 1
                total = total_games()
                ai_win_pct = (ai_wins / total * 100) if total > 0 else 0
                opp_win_pct = (opp_wins / total * 100) if total > 0 else 0
                draw_pct = (draws / total * 100) if total > 0 else 0
                print(f"Episode {ep}: Reward {full_reward} (Winner: {winner}, AI Win%: {ai_win_pct:.2f}, Opp Win%: {opp_win_pct:.2f}, Draw%: {draw_pct:.2f})")
                # Backpropagate end-game reward
                for state, action, next_state in reversed(move_history):
                    old_q = Q[state][action]
                    next_max = np.max(Q[next_state]) if get_valid_actions(next_state) else 0
                    Q[state][action] = old_q + alpha * (full_reward + gamma * next_max - old_q)
                break
            
            random_move()
        
        # Decay epsilon faster: reach 0.1 by ~300 episodes
        if ep % 20 == 0:
            epsilon = max(0.1, epsilon * 0.9)
            if ep % 1000 == 0:
                print(f"Epsilon now: {epsilon}")
                with open('q_table.pkl', 'wb') as f:
                    pickle.dump(dict(Q), f)

if __name__ == "__main__":
    train()