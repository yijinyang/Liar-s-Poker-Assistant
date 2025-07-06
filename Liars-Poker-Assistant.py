import tkinter as tk
from tkinter import ttk, messagebox
import itertools
import random
from collections import Counter
from PIL import Image, ImageTk

# Card rank to numeric value mapping
RANK_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

SUIT_SYMBOLS = {
    's': '♠',  # Spades
    'h': '♥',  # Hearts
    'd': '♦',  # Diamonds
    'c': '♣'   # Clubs
}

class TexasHoldemCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Liar's Poker Assistant")
        self.root.geometry("1200x750")  # Increased height for new elements
        self.root.configure(bg='#0a5c36')  # Dark green background
        
        # Card image cache
        self.card_images = {}
        self.image_references = []  # Store references to prevent garbage collection
        
        # Create main frames
        self.create_title_frame()
        self.create_input_frame()
        self.create_output_frame()
        self.create_control_frame()
        
        # Load card images
        self.load_card_images()
        
        # Initialize card displays
        self.init_card_displays()
        
        # Set up validation for bid and ante
        self.setup_validation()
        
    def setup_validation(self):
        """Set up validation for bid and ante inputs"""
        self.bid_var.trace_add("write", self.validate_bid_ante)
        self.ante_var.trace_add("write", self.validate_bid_ante)
        
    def validate_bid_ante(self, *args):
        """Ensure ante is at least as large as bid"""
        bid = self.bid_var.get()
        ante = self.ante_var.get()
        
        if ante < bid:
            self.ante_var.set(bid)
        
    def create_title_frame(self):
        title_frame = tk.Frame(self.root, bg='#0a5c36')
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(
            title_frame, 
            text="Liar's Poker Assistant", 
            font=('Arial', 18, 'bold'),
            fg='gold',
            bg='#0a5c36'
        )
        title_label.pack(pady=5)
        
    def create_input_frame(self):
        input_frame = tk.Frame(self.root, bg='#1c7947', padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side: Player cards
        left_frame = tk.Frame(input_frame, bg='#1c7947')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        player_frame = tk.LabelFrame(left_frame, text="Your Hole Cards", font=('Arial', 10, 'bold'),
                                   bg='#1c7947', fg='white', padx=5, pady=5)
        player_frame.pack(padx=5, pady=5)
        
        self.player_card_labels = []
        self.player_rank_vars = []
        self.player_suit_vars = []
        
        for i in range(2):
            card_frame = tk.Frame(player_frame, bg='#1c7947')
            card_frame.grid(row=0, column=i, padx=3)
            
            # Card image display
            card_label = tk.Label(card_frame, image=None, bg='#1c7947')
            card_label.grid(row=0, columnspan=2)
            self.player_card_labels.append(card_label)
            
            # Rank selection
            rank_var = tk.StringVar()
            rank_dropdown = ttk.Combobox(
                card_frame, 
                textvariable=rank_var, 
                width=4, 
                state='readonly'
            )
            rank_dropdown['values'] = ['', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            rank_dropdown.grid(row=1, column=0, pady=3)
            rank_dropdown.bind('<<ComboboxSelected>>', lambda e, idx=i: self.update_card_display('player', idx))
            self.player_rank_vars.append(rank_var)
            
            # Suit selection
            suit_var = tk.StringVar()
            suit_dropdown = ttk.Combobox(
                card_frame, 
                textvariable=suit_var, 
                width=2, 
                state='readonly'
            )
            suit_dropdown['values'] = ['', '♠', '♥', '♦', '♣']
            suit_dropdown.grid(row=1, column=1, pady=3)
            suit_dropdown.bind('<<ComboboxSelected>>', lambda e, idx=i: self.update_card_display('player', idx))
            self.player_suit_vars.append(suit_var)
        
        # Middle: Community cards
        middle_frame = tk.Frame(input_frame, bg='#1c7947')
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        community_frame = tk.LabelFrame(middle_frame, text="Community Cards", font=('Arial', 10, 'bold'),
                                       bg='#1c7947', fg='white', padx=5, pady=5)
        community_frame.pack(padx=5, pady=5)
        
        self.community_card_labels = []
        self.community_rank_vars = []
        self.community_suit_vars = []
        
        for i in range(5):
            card_frame = tk.Frame(community_frame, bg='#1c7947')
            card_frame.grid(row=0, column=i, padx=3)
            
            # Card image display
            card_label = tk.Label(card_frame, image=None, bg='#1c7947')
            card_label.grid(row=0, columnspan=2)
            self.community_card_labels.append(card_label)
            
            # Rank selection
            rank_var = tk.StringVar()
            rank_dropdown = ttk.Combobox(
                card_frame, 
                textvariable=rank_var, 
                width=4, 
                state='readonly'
            )
            rank_dropdown['values'] = ['', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            rank_dropdown.grid(row=1, column=0, pady=3)
            rank_dropdown.bind('<<ComboboxSelected>>', lambda e, idx=i: self.update_card_display('community', idx))
            self.community_rank_vars.append(rank_var)
            
            # Suit selection
            suit_var = tk.StringVar()
            suit_dropdown = ttk.Combobox(
                card_frame, 
                textvariable=suit_var, 
                width=2, 
                state='readonly'
            )
            suit_dropdown['values'] = ['', '♠', '♥', '♦', '♣']
            suit_dropdown.grid(row=1, column=1, pady=3)
            suit_dropdown.bind('<<ComboboxSelected>>', lambda e, idx=i: self.update_card_display('community', idx))
            self.community_suit_vars.append(suit_var)
        
        # Right side: Parameters
        right_frame = tk.Frame(input_frame, bg='#1c7947')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        params_frame = tk.LabelFrame(right_frame, text="Simulation Parameters", font=('Arial', 10, 'bold'),
                                    bg='#1c7947', fg='white', padx=10, pady=10)
        params_frame.pack(padx=5, pady=5)
        
        # Opponents input
        tk.Label(params_frame, text="Number of Opponents:", font=('Arial', 9), 
                bg='#1c7947', fg='white').grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.opponents_var = tk.IntVar(value=3)
        opponents_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=9, 
            textvariable=self.opponents_var,
            width=5
        )
        opponents_spin.grid(row=0, column=1, padx=5, pady=3)
        
        # Simulations input
        tk.Label(params_frame, text="Simulations:", font=('Arial', 9), 
                bg='#1c7947', fg='white').grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.simulations_var = tk.IntVar(value=1000)
        simulations_spin = ttk.Spinbox(
            params_frame, 
            from_=100, 
            to=100000, 
            increment=100,
            textvariable=self.simulations_var,
            width=8
        )
        simulations_spin.grid(row=1, column=1, padx=5, pady=3)
        
        # Current Bid input for Liar's Poker
        tk.Label(params_frame, text="Current Bid (1-8):", font=('Arial', 9), 
                bg='#1c7947', fg='white').grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.bid_var = tk.IntVar(value=1)
        bid_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=8, 
            textvariable=self.bid_var,
            width=5
        )
        bid_spin.grid(row=2, column=1, padx=5, pady=3)
        
        # Ante input for Liar's Poker
        tk.Label(params_frame, text="Ante (≥ Bid):", font=('Arial', 9), 
                bg='#1c7947', fg='white').grid(row=3, column=0, sticky='w', padx=5, pady=3)
        self.ante_var = tk.IntVar(value=2)
        ante_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=8, 
            textvariable=self.ante_var,
            width=5
        )
        ante_spin.grid(row=3, column=1, padx=5, pady=3)
    
    def create_output_frame(self):
        output_frame = tk.Frame(self.root, bg='#1c7947', padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Result frame
        result_frame = tk.LabelFrame(output_frame, text="Results", font=('Arial', 12, 'bold'),
                                   bg='#1c7947', fg='white', padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Probability bars
        left_frame = tk.Frame(result_frame, bg='#1c7947')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        prob_frame = tk.Frame(left_frame, bg='#1c7947')
        prob_frame.pack(fill=tk.X, pady=5)
        
        # Win probability
        tk.Label(prob_frame, text="Win:", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white', width=8).grid(row=0, column=0, sticky='w', padx=5)
        self.win_bar = ttk.Progressbar(prob_frame, orient='horizontal', length=250, mode='determinate')
        self.win_bar.grid(row=0, column=1, padx=5, sticky='we')
        self.win_label = tk.Label(prob_frame, text="0.0%", font=('Arial', 9, 'bold'), 
                                 bg='#1c7947', fg='gold', width=6)
        self.win_label.grid(row=0, column=2, padx=5)
        
        # Tie probability
        tk.Label(prob_frame, text="Tie:", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white', width=8).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.tie_bar = ttk.Progressbar(prob_frame, orient='horizontal', length=250, mode='determinate')
        self.tie_bar.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        self.tie_label = tk.Label(prob_frame, text="0.0%", font=('Arial', 9, 'bold'), 
                                 bg='#1c7947', fg='gold', width=6)
        self.tie_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Loss probability
        tk.Label(prob_frame, text="Loss:", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white', width=8).grid(row=2, column=0, sticky='w', padx=5)
        self.loss_bar = ttk.Progressbar(prob_frame, orient='horizontal', length=250, mode='determinate')
        self.loss_bar.grid(row=2, column=1, padx=5, sticky='we')
        self.loss_label = tk.Label(prob_frame, text="0.0%", font=('Arial', 9, 'bold'), 
                                 bg='#1c7947', fg='gold', width=6)
        self.loss_label.grid(row=2, column=2, padx=5)
        
        # Play Survival chance for Liar's Poker
        tk.Label(prob_frame, text="Play S.", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white', width=8).grid(row=3, column=0, sticky='w', padx=5, pady=(10, 5))
        self.survival_bar = ttk.Progressbar(prob_frame, orient='horizontal', length=250, mode='determinate')
        self.survival_bar.grid(row=3, column=1, padx=5, pady=(10, 5), sticky='we')
        self.survival_label = tk.Label(prob_frame, text="0.0%", font=('Arial', 9, 'bold'), 
                                 bg='#1c7947', fg='gold', width=6)
        self.survival_label.grid(row=3, column=2, padx=5, pady=(10, 5))
        
        # Fold Survival chance
        tk.Label(prob_frame, text="Fold S.", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white', width=8).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.fold_bar = ttk.Progressbar(prob_frame, orient='horizontal', length=250, mode='determinate')
        self.fold_bar.grid(row=4, column=1, padx=5, pady=5, sticky='we')
        self.fold_label = tk.Label(prob_frame, text="0.0%", font=('Arial', 9, 'bold'), 
                                 bg='#1c7947', fg='gold', width=6)
        self.fold_label.grid(row=4, column=2, padx=5, pady=5)
        
        # Hand evaluation
        hand_frame = tk.Frame(left_frame, bg='#1c7947', pady=10)
        hand_frame.pack(fill=tk.X)
        
        tk.Label(hand_frame, text="Your Hand:", font=('Arial', 9, 'bold'), 
                bg='#1c7947', fg='white').grid(row=0, column=0, sticky='w', padx=5)
        self.hand_label = tk.Label(hand_frame, text="", font=('Arial', 9, 'bold'), 
                                  bg='#1c7947', fg='gold', width=40, anchor='w')
        self.hand_label.grid(row=0, column=1, columnspan=2, padx=5, sticky='w')
        
        # Recommendation label
        self.recommendation_label = tk.Label(hand_frame, text="", font=('Arial', 10, 'bold'), 
                                           bg='#1c7947', fg='gold')
        self.recommendation_label.grid(row=1, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        
        # Hand strength description
        strength_frame = tk.Frame(left_frame, bg='#1c7947', pady=5)
        strength_frame.pack(fill=tk.X)
        
        strength_text = (
            "Hand Rankings: 9=RoyalFlush 8=StraightFlush 7=FourKind 6=FullHouse\n"
            "5=Flush 4=Straight 3=ThreeKind 2=TwoPair 1=OnePair 0=HighCard"
        )
        strength_label = tk.Label(strength_frame, text=strength_text, font=('Arial', 8), 
                                 bg='#1c7947', fg='white', justify=tk.LEFT)
        strength_label.pack(anchor='w', padx=5)
        
        # Right side: Play vs Fold comparison
        right_frame = tk.Frame(result_frame, bg='#1c7947', padx=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Play or Fold comparison frame
        comparison_frame = tk.LabelFrame(right_frame, text="Play or Fold?", font=('Arial', 10, 'bold'),
                                       bg='#1c7947', fg='white', padx=10, pady=10)
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a custom canvas for the dual-color bar
        canvas_frame = tk.Frame(comparison_frame, bg='#1c7947')
        canvas_frame.pack(fill=tk.X, pady=10)
        
        self.comparison_canvas = tk.Canvas(canvas_frame, width=300, height=40, bg='#1c7947', highlightthickness=0)
        self.comparison_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # Comparison label
        self.comparison_label = tk.Label(comparison_frame, text="Play: 0.0% | Fold: 0.0%", 
                                        font=('Arial', 10, 'bold'), 
                                        bg='#1c7947', fg='gold')
        self.comparison_label.pack(pady=5)
        
        # Decision label
        self.decision_label = tk.Label(comparison_frame, text="", font=('Arial', 12, 'bold'), 
                                     bg='#1c7947', fg='gold')
        self.decision_label.pack(pady=10)
    
    def create_control_frame(self):
        control_frame = tk.Frame(self.root, bg='#0a5c36', padx=10, pady=5)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Calculate button
        calculate_btn = tk.Button(
            control_frame, 
            text="Calculate", 
            command=self.calculate_odds,
            font=('Arial', 10, 'bold'),
            bg='#f0b400',
            fg='black',
            padx=15,
            pady=3,
            relief='raised',
            borderwidth=2
        )
        calculate_btn.pack(side=tk.LEFT, padx=10)
        
        # Add Call All-In button
        allin_btn = tk.Button(
            control_frame, 
            text="Call All-In", 
            command=self.call_all_in,
            font=('Arial', 10, 'bold'),
            bg='#ff4500',  # Orange color for emphasis
            fg='white',
            padx=15,
            pady=3,
            relief='raised',
            borderwidth=2
        )
        allin_btn.pack(side=tk.LEFT, padx=10)
        
        # Reset button
        reset_btn = tk.Button(
            control_frame, 
            text="Reset", 
            command=self.reset,
            font=('Arial', 10),
            bg='#a0a0a0',
            fg='black',
            padx=15,
            pady=3,
            relief='raised',
            borderwidth=2
        )
        reset_btn.pack(side=tk.RIGHT, padx=10)
    
    def call_all_in(self):
        """Set ante to 8 and calculate odds"""
        # Set ante to maximum value (8)
        self.ante_var.set(8)
        
        # Run calculation with new ante value
        self.calculate_odds()
    
    def load_card_images(self):
        """Generate card images for the UI (smaller size)"""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['s', 'h', 'd', 'c']
        
        # Create a blank card image for empty slots
        blank_img = Image.new('RGB', (60, 90), (40, 120, 70))
        blank_img_tk = ImageTk.PhotoImage(blank_img)
        self.card_images['blank'] = blank_img_tk
        self.image_references.append(blank_img_tk)  # Store reference
        
        # Create card images
        for suit in suits:
            for rank in ranks:
                card_code = f"{rank}{suit}"
                
                # Create card image
                img = Image.new('RGB', (60, 90), (255, 255, 255))
                
                # Add suit symbol and rank
                suit_symbol = SUIT_SYMBOLS[suit]
                color = 'red' if suit in ['h', 'd'] else 'black'
                
                # Draw rank and suit
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", 18)
                except:
                    font = ImageFont.load_default()
                
                # Top-left corner
                draw.text((8, 8), rank, fill=color, font=font)
                draw.text((8, 30), suit_symbol, fill=color, font=font)
                
                # Bottom-right corner - adjust position for 2-character ranks
                x_offset = 45
                if len(rank) == 2:  # For "10" card
                    x_offset = 38
                draw.text((x_offset, 60), rank, fill=color, font=font)
                draw.text((45, 80), suit_symbol, fill=color, font=font)
                
                # Convert to PhotoImage and store
                img_tk = ImageTk.PhotoImage(img)
                self.card_images[card_code] = img_tk
                self.image_references.append(img_tk)  # Store reference
    
    def init_card_displays(self):
        """Initialize card displays with blank images"""
        # Create a dedicated reference for each label's image
        for label in self.player_card_labels:
            img = self.card_images['blank']
            label.configure(image=img)
            label.image = img  # Store direct reference on the label
        
        for label in self.community_card_labels:
            img = self.card_images['blank']
            label.configure(image=img)
            label.image = img  # Store direct reference on the label
    
    def update_card_display(self, card_type, index):
        """Update card display based on dropdown selection"""
        if card_type == 'player':
            rank = self.player_rank_vars[index].get()
            suit_symbol = self.player_suit_vars[index].get()
            label = self.player_card_labels[index]
            
            # Convert suit symbol to letter
            suit_letter = ''
            if suit_symbol == '♠': suit_letter = 's'
            elif suit_symbol == '♥': suit_letter = 'h'
            elif suit_symbol == '♦': suit_letter = 'd'
            elif suit_symbol == '♣': suit_letter = 'c'
            
            if rank and suit_letter:
                card_code = f"{rank}{suit_letter}"
                img = self.card_images[card_code]
                label.configure(image=img)
                label.image = img  # Update direct reference
            else:
                img = self.card_images['blank']
                label.configure(image=img)
                label.image = img  # Update direct reference
        else:  # community
            rank = self.community_rank_vars[index].get()
            suit_symbol = self.community_suit_vars[index].get()
            label = self.community_card_labels[index]
            
            # Convert suit symbol to letter
            suit_letter = ''
            if suit_symbol == '♠': suit_letter = 's'
            elif suit_symbol == '♥': suit_letter = 'h'
            elif suit_symbol == '♦': suit_letter = 'd'
            elif suit_symbol == '♣': suit_letter = 'c'
            
            if rank and suit_letter:
                card_code = f"{rank}{suit_letter}"
                img = self.card_images[card_code]
                label.configure(image=img)
                label.image = img  # Update direct reference
            else:
                img = self.card_images['blank']
                label.configure(image=img)
                label.image = img  # Update direct reference
    
    def reset(self):
        """Reset all inputs to default values"""
        # Reset player cards
        for i in range(2):
            self.player_rank_vars[i].set('')
            self.player_suit_vars[i].set('')
            img = self.card_images['blank']
            self.player_card_labels[i].configure(image=img)
            self.player_card_labels[i].image = img  # Update reference
        
        # Reset community cards
        for i in range(5):
            self.community_rank_vars[i].set('')
            self.community_suit_vars[i].set('')
            img = self.card_images['blank']
            self.community_card_labels[i].configure(image=img)
            self.community_card_labels[i].image = img  # Update reference
        
        # Reset parameters
        self.opponents_var.set(3)
        self.simulations_var.set(1000)
        self.bid_var.set(1)
        self.ante_var.set(2)
        
        # Reset results
        self.win_bar['value'] = 0
        self.tie_bar['value'] = 0
        self.loss_bar['value'] = 0
        self.survival_bar['value'] = 0
        self.fold_bar['value'] = 0
        self.win_label.config(text="0.0%")
        self.tie_label.config(text="0.0%")
        self.loss_label.config(text="0.0%")
        self.survival_label.config(text="0.0%")
        self.fold_label.config(text="0.0%")
        self.comparison_label.config(text="Play: 0.0% | Fold: 0.0%")
        self.decision_label.config(text="")
        self.hand_label.config(text="")
        self.recommendation_label.config(text="")
        self.update_comparison_bar(0, 0)
    
    def update_comparison_bar(self, play_value, fold_value):
        """Update the survival vs fold comparison bar to show ratio with centered text"""
        self.comparison_canvas.delete("all")
        width = 300
        height = 40
        
        # Calculate total for ratio
        total = play_value + fold_value
        
        # Calculate bar lengths as ratio of total
        if total > 0:
            play_ratio = play_value / total
            fold_ratio = fold_value / total
            
            play_width = width * play_ratio
            fold_width = width * fold_ratio
        else:
            play_width = 0
            fold_width = 0
        
        # Draw play survival (green)
        self.comparison_canvas.create_rectangle(0, 0, play_width, height, fill="#4CAF50", outline="")
        
        # Draw fold survival (red) starting after play bar
        self.comparison_canvas.create_rectangle(play_width, 0, play_width + fold_width, height, fill="#F44336", outline="")
        
        # Draw centered text in each section
        if play_width > 0:
            # Center text in the play section
            play_center = play_width / 2
            self.comparison_canvas.create_text(play_center, height/2, text="PLAY", 
                                              fill="white", font=('Arial', 10, 'bold'))
        
        if fold_width > 0:
            # Center text in the fold section
            fold_center = play_width + (fold_width / 2)
            self.comparison_canvas.create_text(fold_center, height/2, text="FOLD", 
                                              fill="white", font=('Arial', 10, 'bold'))
        
        # Draw separation line if both values exist
        if play_width > 0 and fold_width > 0:
            self.comparison_canvas.create_line(play_width, 0, play_width, height, fill="white", width=2)
    
    def validate_inputs(self):
        """Validate user inputs before calculation"""
        # Check player cards
        player_cards = []
        for i in range(2):
            rank = self.player_rank_vars[i].get()
            suit_symbol = self.player_suit_vars[i].get()
            
            if not rank or not suit_symbol:
                messagebox.showerror("Input Error", "Please select both rank and suit for your hole cards.")
                return False
            
            # Convert suit symbol to letter
            suit_letter = ''
            if suit_symbol == '♠': suit_letter = 's'
            elif suit_symbol == '♥': suit_letter = 'h'
            elif suit_symbol == '♦': suit_letter = 'd'
            elif suit_symbol == '♣': suit_letter = 'c'
            
            card = f"{rank}{suit_letter}"
            player_cards.append(card)
        
        # Check for duplicate cards
        community_cards = []
        for i in range(5):
            rank = self.community_rank_vars[i].get()
            suit_symbol = self.community_suit_vars[i].get()
            
            if rank and suit_symbol:
                # Convert suit symbol to letter
                suit_letter = ''
                if suit_symbol == '♠': suit_letter = 's'
                elif suit_symbol == '♥': suit_letter = 'h'
                elif suit_symbol == '♦': suit_letter = 'd'
                elif suit_symbol == '♣': suit_letter = 'c'
                
                card = f"{rank}{suit_letter}"
                if card in player_cards or card in community_cards:
                    messagebox.showerror("Input Error", f"Duplicate card detected: {card}")
                    return False
                community_cards.append(card)
        
        # Check if there are enough cards for opponents
        num_opponents = self.opponents_var.get()
        # total_known_cards = len(player_cards) + len(community_cards)
        max_possible = 2 + 5 + num_opponents * 2
        
        if max_possible > 52:
            messagebox.showerror("Input Error", "Too many opponents for the number of cards.")
            return False
        
        # Validate ante and bid
        bid = self.bid_var.get()
        ante = self.ante_var.get()
        if ante < bid:
            messagebox.showerror("Input Error", "Ante must be at least as large as the current bid.")
            return False
        
        return True
    
    def calculate_odds(self):
        """Run the odds calculation and update the UI"""
        if not self.validate_inputs():
            return
        
        # Get player cards
        player_cards = []
        for i in range(2):
            rank = self.player_rank_vars[i].get()
            suit_symbol = self.player_suit_vars[i].get()
            
            # Convert suit symbol to letter
            suit_letter = ''
            if suit_symbol == '♠': suit_letter = 's'
            elif suit_symbol == '♥': suit_letter = 'h'
            elif suit_symbol == '♦': suit_letter = 'd'
            elif suit_symbol == '♣': suit_letter = 'c'
            
            player_cards.append(f"{rank}{suit_letter}")
        
        # Get community cards
        community_cards = []
        for i in range(5):
            rank = self.community_rank_vars[i].get()
            suit_symbol = self.community_suit_vars[i].get()
            
            if rank and suit_symbol:
                # Convert suit symbol to letter
                suit_letter = ''
                if suit_symbol == '♠': suit_letter = 's'
                elif suit_symbol == '♥': suit_letter = 'h'
                elif suit_symbol == '♦': suit_letter = 'd'
                elif suit_symbol == '♣': suit_letter = 'c'
                
                community_cards.append(f"{rank}{suit_letter}")
        
        # Get parameters
        num_opponents = self.opponents_var.get()
        simulations = self.simulations_var.get()
        bid = self.bid_var.get()
        ante = self.ante_var.get()
        
        # Evaluate current hand strength (works with any number of cards)
        all_cards = player_cards + community_cards
        if all_cards:
            hand_strength = self.evaluate_partial_hand(all_cards)
            self.hand_label.config(text=hand_strength)
        else:
            self.hand_label.config(text="No cards selected")
        
        # Run simulation
        win, tie, loss = self.calculate_probabilities(
            player_cards, community_cards, num_opponents, simulations
        )
        
        # Update results
        self.win_bar['value'] = win * 100
        self.tie_bar['value'] = tie * 100
        self.loss_bar['value'] = loss * 100
        self.win_label.config(text=f"{win*100:.1f}%")
        self.tie_label.config(text=f"{tie*100:.1f}%")
        self.loss_label.config(text=f"{loss*100:.1f}%")
        
        # Calculate survival chance for Liar's Poker
        play_survival = (1 - (loss * (ante / 8))) * 100
        self.survival_bar['value'] = play_survival
        self.survival_label.config(text=f"{play_survival:.1f}%")
        
        # Calculate fold survival
        fold_survival = (8 - bid) / 8 * 100
        self.fold_bar['value'] = fold_survival
        self.fold_label.config(text=f"{fold_survival:.1f}%")
        
        # Update comparison bar and label
        self.comparison_label.config(text=f"Play: {play_survival:.1f}% | Fold: {fold_survival:.1f}%")
        self.update_comparison_bar(play_survival, fold_survival)
        
        # Make recommendation
        if play_survival > fold_survival:
            rec_text = "Recommendation: PLAY (Higher survival chance)"
            decision_text = "PLAY"
            color = "#4CAF50"  # Green
        elif play_survival < fold_survival:
            rec_text = "Recommendation: FOLD (Higher survival chance)"
            decision_text = "FOLD"
            color = "#F44336"  # Red
        else:
            rec_text = "Recommendation: Either option has same survival"
            decision_text = "EITHER"
            color = "gold"
        
        self.recommendation_label.config(text=rec_text, fg=color)
        self.decision_label.config(text=decision_text, fg=color, font=('Arial', 14, 'bold'))
    
    def evaluate_partial_hand(self, cards):
        """Evaluate hand strength with any number of cards for Liar's Poker"""
        # Convert cards to numeric ranks
        ranks = []
        for card in cards:
            rank_str = card[:-1]
            ranks.append(RANK_MAP[rank_str])
        
        # Count rank occurrences
        rank_counts = Counter(ranks)
        sorted_counts = sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0]))
        
        # Check for pairs and sets
        pairs = []
        triples = []
        quads = []
        
        for rank, count in sorted_counts:
            if count == 4:
                quads.append(rank)
            elif count == 3:
                triples.append(rank)
            elif count == 2:
                pairs.append(rank)
        
        # Determine hand strength
        if quads:
            return f"Four of a Kind ({quads[0]}s)"
        elif triples and pairs:
            return f"Full House ({triples[0]}s full of {pairs[0]}s)"
        elif triples:
            return f"Three of a Kind ({triples[0]}s)"
        elif len(pairs) >= 2:
            return f"Two Pair ({pairs[0]}s and {pairs[1]}s)"
        elif pairs:
            return f"One Pair ({pairs[0]}s)"
        elif ranks:
            # Return high card
            max_rank = max(ranks)
            # Convert numeric rank back to card value
            rank_names = {v: k for k, v in RANK_MAP.items()}
            return f"High Card ({rank_names[max_rank]})"
        else:
            return "No cards"
    
    # Poker hand evaluation functions
    def generate_deck(self):
        """Generate a standard deck of 52 cards."""
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['s', 'h', 'd', 'c']
        return [r + s for r in ranks for s in suits]
    
    def evaluate_five_card_hand(self, cards):
        """
        Evaluate a 5-card hand and return its strength tuple.
        Strength tuple format: (hand_rank, primary, secondary, ...)
        Hand Ranks: 8=Straight Flush, 7=Four of a Kind, 6=Full House, 5=Flush,
                    4=Straight, 3=Three of a Kind, 2=Two Pair, 1=One Pair, 0=High Card
        """
        # Convert cards to numeric ranks and suits
        ranks = []
        for card in cards:
            # Extract rank (could be 1 or 2 characters)
            rank_str = card[:-1]
            ranks.append(RANK_MAP[rank_str])
        ranks = sorted(ranks, reverse=True)
        suits = [c[-1] for c in cards]
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = False
        if len(set(ranks)) == 5:
            # Standard straight
            if ranks[0] - ranks[4] == 4:
                is_straight = True
                high_rank = ranks[0]
            # Ace-low straight (A,2,3,4,5)
            elif ranks == [14, 5, 4, 3, 2]:
                is_straight = True
                high_rank = 5
        
        # Straight flush
        if is_flush and is_straight:
            return (8, high_rank)
        
        # Count rank occurrences
        rank_counts = Counter(ranks)
        sorted_counts = sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0]))
        
        # Four of a kind
        if sorted_counts[0][1] == 4:
            return (7, sorted_counts[0][0], sorted_counts[1][0])
        
        # Full house
        if sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
            return (6, sorted_counts[0][0], sorted_counts[1][0])
        
        # Flush
        if is_flush:
            return (5, *ranks)
        
        # Straight
        if is_straight:
            return (4, high_rank)
        
        # Three of a kind
        if sorted_counts[0][1] == 3:
            kickers = [rc[0] for rc in sorted_counts if rc[1] == 1]
            return (3, sorted_counts[0][0], *kickers)
        
        # Two pair
        if sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
            pairs = [rc[0] for rc in sorted_counts[:2]]
            kicker = sorted_counts[2][0]
            return (2, max(pairs), min(pairs), kicker)
        
        # One pair
        if sorted_counts[0][1] == 2:
            pair_rank = sorted_counts[0][0]
            kickers = [rc[0] for rc in sorted_counts if rc[1] == 1]
            return (1, pair_rank, *kickers)
        
        # High card
        return (0, *ranks)
    
    def evaluate_hand(self, cards):
        """
        Evaluate best 5-card hand from 5-7 cards.
        Returns strength tuple and best hand cards.
        """
        best_strength = None
        best_hand = None
        
        # Generate all 5-card combinations
        for combo in itertools.combinations(cards, 5):
            strength = self.evaluate_five_card_hand(combo)
            if best_strength is None or strength > best_strength:
                best_strength = strength
                best_hand = combo
        
        return best_strength, best_hand
    
    def calculate_probabilities(self, hero_cards, community_cards, num_opponents, simulations):
        """
        Calculate win/tie/loss probabilities using Monte Carlo simulation.
        Returns: (win_prob, tie_prob, loss_prob)
        """
        # Initialize counters
        wins = 0
        ties = 0
        losses = 0
        
        # Generate full deck
        deck = self.generate_deck()
        
        # Remove known cards (hero's hole cards and community cards)
        known_cards = hero_cards + community_cards
        for card in known_cards:
            if card in deck:
                deck.remove(card)
        
        # Number of community cards to draw
        needed_community = 5 - len(community_cards)
        
        # Run simulations
        for _ in range(simulations):
            # Shuffle remaining deck
            random.shuffle(deck)
            temp_deck = deck.copy()
            
            # Complete community cards
            new_community = community_cards + temp_deck[:needed_community]
            temp_deck = temp_deck[needed_community:]
            
            # Generate opponent cards
            opponents = []
            for _ in range(num_opponents):
                opponents.append(temp_deck[:2])
                temp_deck = temp_deck[2:]
            
            # Evaluate hero's hand
            hero_strength, _ = self.evaluate_hand(hero_cards + new_community)
            
            # Evaluate opponents' hands
            opponent_strengths = []
            for opp in opponents:
                opp_strength, _ = self.evaluate_hand(opp + new_community)
                opponent_strengths.append(opp_strength)
            
            # Find best opponent hand
            best_opp_strength = max(opponent_strengths) if opponent_strengths else None
            
            # Compare results
            if best_opp_strength is None:
                wins += 1  # No opponents
            else:
                if hero_strength > best_opp_strength:
                    wins += 1
                elif hero_strength < best_opp_strength:
                    losses += 1
                else:
                    ties += 1
        
        # Calculate probabilities
        win_prob = wins / simulations
        tie_prob = ties / simulations
        loss_prob = losses / simulations
        
        return win_prob, tie_prob, loss_prob

if __name__ == "__main__":
    root = tk.Tk()
    app = TexasHoldemCalculator(root)
    root.mainloop()