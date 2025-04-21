import pygame
import sys
from rps_agent_advanced import AdvancedRPSAgent

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
PREDICTION_BAR_HEIGHT = 30
PREDICTION_BAR_WIDTH = 200

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (100, 149, 237)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
BLUE = (0, 0, 255)

class RPSGameUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rock Paper Scissors AI")
        
        # Initialize AI agent
        self.agent = AdvancedRPSAgent()
        
        # Game state
        self.player_score = 0
        self.ai_score = 0
        self.round_result = ""
        self.player_move = None
        self.ai_move = None
        
        # Prediction probabilities
        self.rock_prob = 0.33
        self.paper_prob = 0.33
        self.scissors_prob = 0.33
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create buttons
        self.buttons = {
            'rock': pygame.Rect(50, WINDOW_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT),
            'paper': pygame.Rect(250, WINDOW_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT),
            'scissors': pygame.Rect(450, WINDOW_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT),
            'quit': pygame.Rect(650, WINDOW_HEIGHT - 100, BUTTON_WIDTH, BUTTON_HEIGHT)
        }
    
    def calculate_move_probabilities(self):
        """Calculate probabilities for each move based on AI's prediction"""
        if len(self.agent.player_history) < 3:
            return
            
        total_moves = sum(self.agent.move_frequencies.values()) or 1
        self.rock_prob = self.agent.move_frequencies['rock'] / total_moves
        self.paper_prob = self.agent.move_frequencies['paper'] / total_moves
        self.scissors_prob = self.agent.move_frequencies['scissors'] / total_moves
    
    def draw_prediction_bars(self):
        """Draw prediction probability bars"""
        # Rock probability
        bar_x = 50
        bar_y = 300
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, PREDICTION_BAR_WIDTH, PREDICTION_BAR_HEIGHT))
        pygame.draw.rect(self.screen, RED, 
                        (bar_x, bar_y, int(PREDICTION_BAR_WIDTH * self.rock_prob), PREDICTION_BAR_HEIGHT))
        text = self.small_font.render(f"Rock: {self.rock_prob:.1%}", True, BLACK)
        self.screen.blit(text, (bar_x + 10, bar_y + 5))
        
        # Paper probability
        bar_y += 50
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, PREDICTION_BAR_WIDTH, PREDICTION_BAR_HEIGHT))
        pygame.draw.rect(self.screen, GREEN,
                        (bar_x, bar_y, int(PREDICTION_BAR_WIDTH * self.paper_prob), PREDICTION_BAR_HEIGHT))
        text = self.small_font.render(f"Paper: {self.paper_prob:.1%}", True, BLACK)
        self.screen.blit(text, (bar_x + 10, bar_y + 5))
        
        # Scissors probability
        bar_y += 50
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, PREDICTION_BAR_WIDTH, PREDICTION_BAR_HEIGHT))
        pygame.draw.rect(self.screen, BLUE,
                        (bar_x, bar_y, int(PREDICTION_BAR_WIDTH * self.scissors_prob), PREDICTION_BAR_HEIGHT))
        text = self.small_font.render(f"Scissors: {self.scissors_prob:.1%}", True, BLACK)
        self.screen.blit(text, (bar_x + 10, bar_y + 5))
    
    def draw_stats(self):
        """Draw game statistics"""
        stats_text = [
            f"Games Played: {self.agent.stats['wins'] + self.agent.stats['losses'] + self.agent.stats['draws']}",
            f"AI Wins: {self.agent.stats['wins']}",
            f"Player Wins: {self.agent.stats['losses']}",
            f"Draws: {self.agent.stats['draws']}",
            f"Learning Rate: {self.agent.epsilon:.3f}"
        ]
        
        y = 50
        for text in stats_text:
            surface = self.small_font.render(text, True, BLACK)
            self.screen.blit(surface, (WINDOW_WIDTH - 250, y))
            y += 30
    
    def draw_moves(self):
        """Draw current moves"""
        if self.player_move:
            text = self.font.render(f"Your move: {self.player_move}", True, BLACK)
            self.screen.blit(text, (50, 150))
        if self.ai_move:
            text = self.font.render(f"AI move: {self.ai_move}", True, BLACK)
            self.screen.blit(text, (50, 200))
        if self.round_result:
            text = self.font.render(self.round_result, True, BLACK)
            self.screen.blit(text, (50, 250))
    
    def draw(self):
        """Draw the game screen"""
        self.screen.fill(WHITE)
        
        # Draw buttons
        for text, button in self.buttons.items():
            pygame.draw.rect(self.screen, LIGHT_BLUE, button)
            text_surface = self.font.render(text.title(), True, BLACK)
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)
        
        # Draw prediction bars
        self.draw_prediction_bars()
        
        # Draw statistics
        self.draw_stats()
        
        # Draw moves
        self.draw_moves()
        
        pygame.display.flip()
    
    def handle_move(self, move):
        """Process a player's move"""
        self.player_move = move
        current_state = self.agent.get_state()
        
        # AI makes its move
        self.ai_move = self.agent.choose_action(current_state)
        
        # Update histories and learn
        self.agent.update_history(self.player_move, self.ai_move)
        reward = 1 if self.ai_move == self.agent.get_counter_move(self.player_move) else -1
        next_state = self.agent.get_state()
        self.agent.learn(current_state, self.ai_move, reward, next_state)
        
        # Determine winner
        if self.player_move == self.ai_move:
            self.round_result = "It's a draw!"
        elif (
            (self.player_move == 'rock' and self.ai_move == 'scissors') or
            (self.player_move == 'paper' and self.ai_move == 'rock') or
            (self.player_move == 'scissors' and self.ai_move == 'paper')
        ):
            self.round_result = "You win!"
        else:
            self.round_result = "AI wins!"
        
        # Update stats
        self.agent.update_stats(self.player_move, self.ai_move)
        
        # Update probabilities
        self.calculate_move_probabilities()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    # Check button clicks
                    for move, button in self.buttons.items():
                        if button.collidepoint(mouse_pos):
                            if move == 'quit':
                                running = False
                            else:
                                self.handle_move(move)
            
            self.draw()
        
        # Save learning progress when quitting
        self.agent.save_learning()
        pygame.quit()

if __name__ == "__main__":
    game = RPSGameUI()
    game.run() 