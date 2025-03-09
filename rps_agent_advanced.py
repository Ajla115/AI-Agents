import numpy as np
import random
from collections import deque, Counter
import json
import os
from datetime import datetime

class AdvancedRPSAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.choices = ['rock', 'paper', 'scissors']
        self.state_size = 5  # Increased history size
        self.action_size = 3
        
        # Learning parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995
        
        # Advanced tracking
        self.player_history = deque(maxlen=self.state_size)
        self.agent_history = deque(maxlen=self.state_size)
        self.move_frequencies = {'rock': 0, 'paper': 0, 'scissors': 0}
        self.pattern_frequencies = {}
        self.transition_matrix = {
            'rock': {'rock': 0, 'paper': 0, 'scissors': 0},
            'paper': {'rock': 0, 'paper': 0, 'scissors': 0},
            'scissors': {'rock': 0, 'paper': 0, 'scissors': 0}
        }
        
        # Performance tracking
        self.stats = {
            'wins': 0, 'losses': 0, 'draws': 0,
            'player_patterns': {},
            'winning_moves': Counter(),
            'session_start': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Initialize histories
        self._initialize_histories()
        
        # Load previous learning if available
        self.load_learning()
    
    def _initialize_histories(self):
        """Initialize move histories"""
        for _ in range(self.state_size):
            self.player_history.append('none')
            self.agent_history.append('none')
    
    def get_state(self):
        """Get current state including pattern analysis"""
        basic_state = self._get_basic_state()
        frequency_state = self._get_frequency_state()
        return f"{basic_state}|{frequency_state}"
    
    def _get_basic_state(self):
        """Get state from move histories"""
        player_state = ','.join(list(self.player_history))
        agent_state = ','.join(list(self.agent_history))
        return f"{player_state}|{agent_state}"
    
    def _get_frequency_state(self):
        """Analyze move frequencies"""
        total_moves = sum(self.move_frequencies.values()) or 1
        frequencies = {k: v/total_moves for k, v in self.move_frequencies.items()}
        return f"{max(frequencies, key=frequencies.get)}"
    
    def analyze_pattern(self, moves):
        """Analyze pattern in recent moves"""
        if len(moves) < 3:
            return None
        pattern = ','.join(list(moves)[-3:])
        if pattern not in self.pattern_frequencies:
            self.pattern_frequencies[pattern] = {'rock': 0, 'paper': 0, 'scissors': 0}
        return pattern
    
    def update_transition_matrix(self, prev_move, current_move):
        """Update transition probabilities"""
        if prev_move != 'none':
            self.transition_matrix[prev_move][current_move] += 1
    
    def predict_next_move(self):
        """Predict player's next move using multiple strategies"""
        if len(self.player_history) < 3 or list(self.player_history)[-1] == 'none':
            return random.choice(self.choices)
        
        # Get last pattern
        recent_pattern = ','.join(list(self.player_history)[-3:])
        
        # Pattern-based prediction
        pattern_pred = None
        if recent_pattern in self.pattern_frequencies:
            pattern_pred = max(self.pattern_frequencies[recent_pattern].items(),
                             key=lambda x: x[1])[0]
        
        # Frequency-based prediction
        freq_pred = None
        if sum(self.move_frequencies.values()) > 0:
            freq_pred = max(self.move_frequencies.items(), key=lambda x: x[1])[0]
        
        # Transition-based prediction
        last_move = list(self.player_history)[-1]
        trans_pred = None
        if last_move in self.transition_matrix and sum(self.transition_matrix[last_move].values()) > 0:
            trans_pred = max(self.transition_matrix[last_move].items(),
                           key=lambda x: x[1])[0]
        
        # Combine predictions
        predictions = [pred for pred in [pattern_pred, freq_pred, trans_pred] if pred]
        if predictions:
            return max(set(predictions), key=predictions.count)
        return random.choice(self.choices)
    
    def get_counter_move(self, predicted_move):
        """Get the move that beats the predicted move"""
        counter_moves = {
            'rock': 'paper',
            'paper': 'scissors',
            'scissors': 'rock'
        }
        return counter_moves[predicted_move]
    
    def choose_action(self, state):
        """Choose action using advanced strategy"""
        # Exploration
        if random.random() < self.epsilon:
            return random.choice(self.choices)
        
        # Exploitation with prediction
        predicted_move = self.predict_next_move()
        return self.get_counter_move(predicted_move)
    
    def learn(self, state, action, reward, next_state):
        """Enhanced learning process"""
        # Update pattern frequencies
        pattern = self.analyze_pattern(self.player_history)
        if pattern:
            last_move = list(self.player_history)[-1]
            self.pattern_frequencies[pattern][last_move] += 1
        
        # Update move frequencies
        last_player_move = list(self.player_history)[-1]
        if last_player_move != 'none':
            self.move_frequencies[last_player_move] += 1
        
        # Update transition matrix
        if len(self.player_history) >= 2:
            prev_move = list(self.player_history)[-2]
            curr_move = list(self.player_history)[-1]
            if prev_move != 'none':
                self.update_transition_matrix(prev_move, curr_move)
        
        # Adjust exploration rate based on performance
        if reward > 0:  # Won
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def update_stats(self, player_move, agent_move):
        """Update comprehensive statistics"""
        # Basic stats
        if player_move == agent_move:
            self.stats['draws'] += 1
        elif (
            (player_move == 'rock' and agent_move == 'paper') or
            (player_move == 'paper' and agent_move == 'scissors') or
            (player_move == 'scissors' and agent_move == 'rock')
        ):
            self.stats['wins'] += 1
            self.stats['winning_moves'][agent_move] += 1
        else:
            self.stats['losses'] += 1
        
        # Update pattern stats
        pattern = self.analyze_pattern(self.player_history)
        if pattern:
            if pattern not in self.stats['player_patterns']:
                self.stats['player_patterns'][pattern] = 0
            self.stats['player_patterns'][pattern] += 1
    
    def save_learning(self):
        """Save learning progress to file"""
        learning_data = {
            'move_frequencies': self.move_frequencies,
            'pattern_frequencies': self.pattern_frequencies,
            'transition_matrix': self.transition_matrix,
            'stats': self.stats
        }
        with open('rps_learning.json', 'w') as f:
            json.dump(learning_data, f)
    
    def load_learning(self):
        """Load previous learning progress"""
        if os.path.exists('rps_learning.json'):
            with open('rps_learning.json', 'r') as f:
                data = json.load(f)
                self.move_frequencies = data['move_frequencies']
                self.pattern_frequencies = data['pattern_frequencies']
                self.transition_matrix = data['transition_matrix']
                # Merge stats but keep current session info
                old_stats = data['stats']
                self.stats['wins'] += old_stats['wins']
                self.stats['losses'] += old_stats['losses']
                self.stats['draws'] += old_stats['draws']
                self.stats['player_patterns'].update(old_stats['player_patterns'])
                self.stats['winning_moves'].update(old_stats['winning_moves'])
    
    def update_history(self, player_move, agent_move):
        """Update move histories"""
        self.player_history.append(player_move)
        self.agent_history.append(agent_move)

def play_game():
    """Enhanced game loop with advanced features"""
    agent = AdvancedRPSAgent()
    print("\nWelcome to Advanced Rock Paper Scissors AI!")
    print("This AI learns and adapts to your playing style.")
    print("\nCommands:")
    print("- Type 'rock', 'paper', or 'scissors' to play")
    print("- Type 'stats' for game statistics")
    print("- Type 'patterns' to see your most common patterns")
    print("- Type 'learning' for AI learning status")
    print("- Type 'quit' to end the game\n")
    
    try:
        while True:
            current_state = agent.get_state()
            player_move = input("\nYour move: ").lower()
            
            if player_move == 'quit':
                break
            elif player_move == 'stats':
                print("\nGame Statistics:")
                print(f"AI Wins: {agent.stats['wins']}")
                print(f"Player Wins: {agent.stats['losses']}")
                print(f"Draws: {agent.stats['draws']}")
                print("\nMost Successful AI Moves:")
                for move, count in agent.stats['winning_moves'].most_common(3):
                    print(f"- {move}: {count} wins")
                continue
            elif player_move == 'patterns':
                print("\nYour Most Common Patterns:")
                patterns = sorted(agent.stats['player_patterns'].items(),
                               key=lambda x: x[1], reverse=True)[:3]
                for pattern, count in patterns:
                    print(f"- {pattern}: {count} times")
                continue
            elif player_move == 'learning':
                print("\nAI Learning Status:")
                print(f"Exploration Rate: {agent.epsilon:.3f}")
                print(f"Patterns Learned: {len(agent.pattern_frequencies)}")
                print("Move Frequencies:")
                total = sum(agent.move_frequencies.values()) or 1
                for move, count in agent.move_frequencies.items():
                    print(f"- {move}: {count/total:.1%}")
                continue
            elif player_move not in agent.choices:
                print("Invalid move! Please choose rock, paper, or scissors.")
                continue
            
            # AI makes its move
            agent_move = agent.choose_action(current_state)
            print(f"AI chose: {agent_move}")
            
            # Update histories before processing
            agent.update_history(player_move, agent_move)
            
            # Process the round
            reward = 1 if agent_move == agent.get_counter_move(player_move) else -1
            next_state = agent.get_state()
            agent.learn(current_state, agent_move, reward, next_state)
            
            # Show round result
            if player_move == agent_move:
                print("It's a draw!")
            elif (
                (player_move == 'rock' and agent_move == 'scissors') or
                (player_move == 'paper' and agent_move == 'rock') or
                (player_move == 'scissors' and agent_move == 'paper')
            ):
                print("You win!")
            else:
                print("AI wins!")
            
            agent.update_stats(player_move, agent_move)
    
    finally:
        # Save learning progress when game ends
        agent.save_learning()
        print("\nThanks for playing! AI learning progress has been saved.")

if __name__ == "__main__":
    play_game() 