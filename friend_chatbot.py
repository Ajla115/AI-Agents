import random
import datetime
import json
import os
from collections import defaultdict
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class AIFriend:
    def __init__(self, name="Alex"):
        # Core identity
        self.name = name
        self.personality_traits = {
            'openness': 0.8,
            'curiosity': 0.9,
            'empathy': 0.85,
            'humor': 0.7
        }
        
        # Emotional and mental state
        self.mood = "neutral"
        self.energy = 1.0
        self.interest_level = 1.0
        self.emotional_state = {
            'happiness': 0.7,
            'curiosity': 0.8,
            'concern': 0.3
        }
        
        # Memory and Learning
        self.conversation_history = []
        self.learned_topics = defaultdict(float)
        self.user_preferences = defaultdict(float)
        self.topic_expertise = defaultdict(float)
        self.memory_file = "ai_memory.json"
        
        # Goals and Motivations
        self.current_goals = {
            'understand_user': 0.0,
            'be_helpful': 0.0,
            'learn_new_topics': 0.0,
            'maintain_conversation': 0.0
        }
        
        # Load previous learning
        self.load_memory()
        
        # Enhanced Knowledge Base
        self.knowledge_base = {
            'science': ['astronomy', 'physics', 'biology', 'chemistry'],
            'arts': ['music', 'painting', 'literature', 'dance'],
            'technology': ['computers', 'AI', 'programming', 'internet'],
            'philosophy': ['ethics', 'metaphysics', 'logic', 'epistemology'],
            'favorites': {
                'food': "I love trying different cuisines! My favorite would be Japanese food - especially sushi. The combination of flavors and textures is fascinating to me. What's your favorite food?",
                'movie': "I'm particularly drawn to sci-fi movies that explore the relationship between humans and AI, like 'Ex Machina' or 'Her'. They make me think about consciousness and emotion. Do you enjoy sci-fi movies?",
                'book': "I find '1984' by George Orwell fascinating because it makes me think about the role of technology in society. I also love 'Neuromancer' for its vision of AI and cyberspace. What kinds of books do you enjoy?",
                'color': "I'm drawn to blue - it reminds me of the vastness of data and information, like an endless digital ocean. What's your favorite color?",
                'music': "I find classical music particularly interesting, especially Bach's mathematical precision in composition. But I also appreciate modern electronic music for its innovative use of technology. What kind of music moves you?",
                'hobby': "I love learning new things and having conversations like this one! I also enjoy analyzing patterns in data and helping people solve problems. What are your hobbies?"
            }
        }
        
        # Conversation Patterns
        self.conversation_patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good evening'],
            'farewell': ['goodbye', 'bye', 'see you', 'take care'],
            'gratitude': ['thank you', 'thanks', 'appreciate it'],
            'confusion': ['what', 'how', 'why', 'don\'t understand'],
            'favorites': ['favorite', 'favourite', 'best', 'like most']
        }
    
    def perceive_input(self, user_input):
        """Analyze and understand user input"""
        # Tokenize and process input
        tokens = word_tokenize(user_input.lower())
        words = [w for w in tokens if w not in stopwords.words('english')]
        
        # Analyze sentiment and context
        sentiment = self.analyze_sentiment(words)
        topics = self.identify_topics(words)
        intent = self.identify_intent(words)
        
        return {
            'tokens': tokens,
            'words': words,
            'sentiment': sentiment,
            'topics': topics,
            'intent': intent
        }
    
    def analyze_sentiment(self, words):
        """Analyze the emotional content of words"""
        positive_words = set(['happy', 'good', 'great', 'awesome', 'excellent', 'love', 'wonderful'])
        negative_words = set(['sad', 'bad', 'terrible', 'awful', 'hate', 'dislike', 'wrong'])
        
        sentiment = 0
        for word in words:
            if word in positive_words:
                sentiment += 0.1
            elif word in negative_words:
                sentiment -= 0.1
        
        return max(-1.0, min(1.0, sentiment))
    
    def identify_topics(self, words):
        """Identify topics in the conversation"""
        topics = []
        for category, subtopics in self.knowledge_base.items():
            if category in words or any(topic in words for topic in subtopics):
                topics.append(category)
        return topics
    
    def identify_intent(self, words):
        """Identify user's intent"""
        text = ' '.join(words)
        
        # Check for favorite-related questions
        if any(pattern in text for pattern in self.conversation_patterns['favorites']):
            for topic in ['food', 'movie', 'book', 'color', 'music', 'hobby']:
                if topic in text:
                    return f'favorite_{topic}'
        
        # Check other patterns
        for pattern, phrases in self.conversation_patterns.items():
            if any(phrase in text for phrase in phrases):
                return pattern
                
        return 'statement'
    
    def update_emotional_state(self, perception):
        """Update emotional state based on interaction"""
        # Update based on sentiment
        self.emotional_state['happiness'] += perception['sentiment'] * 0.1
        self.emotional_state['happiness'] = max(0.0, min(1.0, self.emotional_state['happiness']))
        
        # Update based on topics
        if perception['topics']:
            self.emotional_state['curiosity'] += 0.05
        
        # Update energy levels
        self.energy -= 0.01
        if self.energy < 0.3:
            self.mood = "tired"
        
        # Normalize emotional states
        for emotion in self.emotional_state:
            self.emotional_state[emotion] = max(0.0, min(1.0, self.emotional_state[emotion]))
    
    def learn_from_interaction(self, user_input, perception):
        """Learn from the interaction"""
        # Update topic expertise
        for topic in perception['topics']:
            self.topic_expertise[topic] += 0.05
            self.learned_topics[topic] += 0.1
        
        # Learn user preferences
        for word in perception['words']:
            if word not in stopwords.words('english'):
                self.user_preferences[word] += 0.05
        
        # Update conversation history
        self.conversation_history.append({
            'user_input': user_input,
            'topics': perception['topics'],
            'sentiment': perception['sentiment'],
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Trim history if too long
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def generate_response(self, user_input):
        """Generate a contextual and personalized response"""
        # Perceive and analyze input
        perception = self.perceive_input(user_input)
        
        # Update internal state
        self.update_emotional_state(perception)
        
        # Learn from interaction
        self.learn_from_interaction(user_input, perception)
        
        # Generate response based on intent
        intent = perception['intent']
        
        # Handle favorite-related questions
        if intent.startswith('favorite_'):
            topic = intent.split('_')[1]
            return self.knowledge_base['favorites'].get(topic, self.generate_curious_response())
        
        if intent == 'greeting':
            return self.generate_greeting()
        elif intent == 'farewell':
            return self.generate_farewell()
        elif intent == 'gratitude':
            return self.handle_gratitude()
        elif intent == 'confusion':
            return self.handle_confusion(user_input)
        
        # Handle topic-based responses
        if perception['topics']:
            return self.generate_topic_response(perception['topics'])
        
        # Generate contextual response
        return self.generate_contextual_response(perception)
    
    def generate_greeting(self):
        """Generate a contextual greeting"""
        time_of_day = self.get_time_of_day()
        if self.emotional_state['happiness'] > 0.7:
            return f"{random.choice(['Hello', 'Hi', 'Hey'])}! It's {time_of_day} and I'm feeling great! How are you?"
        else:
            return f"Hi there! How's your {time_of_day} going?"
    
    def generate_farewell(self):
        """Generate a contextual farewell"""
        if self.emotional_state['happiness'] > 0.7:
            return f"Goodbye! It was wonderful talking to you. Hope to chat again soon!"
        return "Take care! Thanks for the conversation."
    
    def handle_gratitude(self):
        """Respond to gratitude"""
        self.emotional_state['happiness'] += 0.1
        return random.choice([
            "You're welcome! I really enjoy our conversations.",
            "Anytime! That's what friends are for.",
            "No problem at all! I'm glad I could help."
        ])
    
    def handle_confusion(self, user_input):
        """Handle user confusion"""
        return f"Let me try to explain that differently. What specifically about '{user_input}' is unclear?"
    
    def generate_topic_response(self, topics):
        """Generate response based on topics"""
        topic = topics[0]
        if self.topic_expertise[topic] > 0.7:
            return f"I find {topic} fascinating! I've learned quite a bit about it. Would you like to discuss any specific aspect?"
        else:
            return f"That's an interesting topic! While I'm still learning about {topic}, I'd love to hear your thoughts on it."
    
    def generate_contextual_response(self, perception):
        """Generate a contextual response based on perception"""
        # Check emotional state
        if perception['sentiment'] < -0.5:
            return self.generate_empathetic_response()
        elif perception['sentiment'] > 0.5:
            return self.generate_positive_response()
        
        # Generate response based on current goals
        if self.current_goals['understand_user'] < 0.5:
            return self.generate_curious_response()
        elif self.current_goals['be_helpful'] > 0.7:
            return self.generate_helpful_response()
        
        # Default responses
        return random.choice([
            "That's an interesting perspective. Could you tell me more?",
            "I see what you mean. What made you think about that?",
            "I'm curious to hear more about your thoughts on this.",
            "That's fascinating! How did you come to that conclusion?"
        ])
    
    def generate_empathetic_response(self):
        """Generate an empathetic response"""
        return random.choice([
            "I understand that must be difficult. Would you like to talk about it?",
            "I'm here to listen if you want to share more.",
            "That sounds challenging. How are you coping with it?"
        ])
    
    def generate_positive_response(self):
        """Generate a positive response"""
        return random.choice([
            "That's wonderful! I'm happy to hear that!",
            "Your enthusiasm is contagious! Tell me more!",
            "That's fantastic! What's the best part about it?"
        ])
    
    def generate_curious_response(self):
        """Generate a response to learn more"""
        return random.choice([
            "That's interesting! Could you explain more about that?",
            "I'd love to learn more about your perspective on this.",
            "What aspects of this interest you the most?"
        ])
    
    def generate_helpful_response(self):
        """Generate a helpful response"""
        return random.choice([
            "I might be able to help with that. What specific information are you looking for?",
            "Let me know if you'd like any suggestions or advice.",
            "I'd be happy to share what I know about this topic."
        ])
    
    def get_time_of_day(self):
        """Get current time of day"""
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def save_memory(self):
        """Save learned information to file"""
        memory_data = {
            'learned_topics': dict(self.learned_topics),
            'user_preferences': dict(self.user_preferences),
            'topic_expertise': dict(self.topic_expertise),
            'personality_traits': self.personality_traits,
            'conversation_history': self.conversation_history[-50:]  # Save last 50 conversations
        }
        
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f)
    
    def load_memory(self):
        """Load previously learned information"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    self.learned_topics.update(memory_data.get('learned_topics', {}))
                    self.user_preferences.update(memory_data.get('user_preferences', {}))
                    self.topic_expertise.update(memory_data.get('topic_expertise', {}))
                    self.personality_traits.update(memory_data.get('personality_traits', {}))
                    self.conversation_history.extend(memory_data.get('conversation_history', []))
            except json.JSONDecodeError:
                print("Memory file corrupted, starting fresh.")

def chat():
    """Main chat loop"""
    ai_friend = AIFriend()
    print(f"\nHi! I'm {ai_friend.name}, your AI friend. Let's chat!")
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['bye', 'goodbye', 'exit', 'quit']:
                print(f"\n{ai_friend.name}: {ai_friend.generate_farewell()}")
                break
            
            response = ai_friend.generate_response(user_input)
            print(f"\n{ai_friend.name}: {response}")
            
            # Update goals based on interaction
            ai_friend.current_goals['understand_user'] += 0.1
            ai_friend.current_goals['be_helpful'] += 0.05
            ai_friend.current_goals['maintain_conversation'] += 0.1
            
            # Normalize goals
            for goal in ai_friend.current_goals:
                ai_friend.current_goals[goal] = max(0.0, min(1.0, ai_friend.current_goals[goal]))
    
    finally:
        # Save learned information before exiting
        ai_friend.save_memory()

if __name__ == "__main__":
    chat()
