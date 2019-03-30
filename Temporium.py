# -*- coding: utf-8 -*-
"""
Jamison Moody
Temporium Game Simulator
3/26/2019
"""
import numpy as np

class Player:
    def __init__(self, player_num, game_object, ishuman = False):
        self.player_num = player_num
        self.hand = []
        self.resources_count = {game_object.resources[i] : 0 for i in range(len(game_object.resources))}
        self.ishuman = ishuman
        self.actions = []
        self.ship_parts = []
        self.bought_rogue = False
        self.pol = "random"
        
        
    def get_actions(self, game_object, result_of_attack = False, must_discard = False, attacking_space = 0, defending = False, from_asteroid = False, first_time_defense = False):
        """
        Gets all available actions for the player in any situation. Adds extra actions for a human player.
        """
        self.actions = [] # Refreshes the action options
        if must_discard: # Special scenario where we are forced to discard
            if result_of_attack and not from_asteroid:
                self.actions = ["Give attacker {}".format(i) for i in self.hand]
            else:
                self.actions = list(set(["Discard {}".format(i) for i in self.hand]))
        elif game_object.round == 0: # Start of the game
            for i in range(1,game_object.present+1): 
                if game_object.board[i-1][0] == 0:
                    self.actions.append("Claim Space {0} and collect {1} {2} resource(s)".format(i, game_object.present-i+1, game_object.board[i-1][1]))
        elif result_of_attack and not must_discard: # These are options for the attacker or defender
            if not defending: # Attacking
                if attacking_space in self.hand:
                    self.actions.append("Attack Space {0} again with a {1}".format(attacking_space, attacking_space))
                elif 0 in self.hand:
                    self.actions.append("Attack Space {0} again with a 0".format(attacking_space))
                self.actions.append("Stop Attacking")
            else: # Defending
                if attacking_space in self.hand:
                    if not first_time_defense:
                        self.actions.append("Defend Space {0} again with a {1}".format(attacking_space, attacking_space))
                    else:
                        self.actions.append("Defend Space {0} with a {1}".format(attacking_space, attacking_space))
                if 0 in self.hand:
                    if not first_time_defense:
                        self.actions.append("Defend Space {0} again with a 0".format(attacking_space))
                    else:
                        self.actions.append("Defend Space {0} with a 0".format(attacking_space)) 
                self.actions.append("Surrender Space")
        else:
            # Checks to see the actions we can take on the board
            # General actions not triggered in a special situation
            for i in range(1,game_object.present+1):
                if game_object.board[i-1][0] != self.player_num: 
                    if game_object.board[i-1][0] != 0:
                        if i in self.hand:
                            self.actions.append("Attack Space {0} with card {1}".format(i, i))
                        if 0 in self.hand:
                            self.actions.append("Attack Space {0} with card 0".format(i))
                    elif game_object.board[i-1][0] == 0:
                        if i in self.hand:
                            self.actions.append("Takeover Space {0} with card {1}".format(i, i))
                        if 0 in self.hand:
                            self.actions.append("Takeover Space {0} with card 0".format(i))
                
            for i in range(game_object.present+1, game_object.board_size+1):
                if i in self.hand:
                    self.actions.append("Collect a {2} resource from Space {0} with card {1}".format(i, i, game_object.board[i-1][1]))
                if 0 in self.hand:
                    self.actions.append("Collect a {1} resource from Space {0} with card 0".format(i, game_object.board[i-1][1]))
                   
            # Checks to see if we can buy a rogue
            for resource in game_object.resources:
                n = self.resources_count[resource]
                if n >= game_object.rogue_cost and not self.bought_rogue:
                    self.actions.append("Buy rogue with {0} {1}".format(game_object.rogue_cost, resource))
            
            # Checks to see if we can buy a ship part
            for ship_part in game_object.ship_part_costs.keys():
                can_buy = True
                for resource in self.resources_count.keys():
                    if self.resources_count[resource] < game_object.ship_part_costs[ship_part].count(resource):
                        can_buy = False
                        break
                if ship_part not in self.ship_parts and can_buy:
                    self.actions.append("Buy ship part {}".format(ship_part))
                    
            self.actions.append("End turn")
                    
        if self.ishuman: # Extra actions for humans only
            self.actions.append("View board")
            self.actions.append("View ship part costs")
            self.actions.append("View your resources")
            self.actions.append("View your ship parts")
            self.actions.append("View your cards")
            
    
    def policy(self):
        """
        Makes a decision based on a policy
        """
        if self.ishuman:
            while True:
                try:
                    choice = int(input("Select an action (0-{}):".format(len(self.actions)-1)))
                    action = self.actions[choice]
                    break
                except TypeError("Invalid Input."):
                    continue
                break
        else:
            if self.pol == "random":
                action_chosen = False
                for a in self.actions:
                    if "Buy ship part" in a: # If we can buy a ship part, do it
                        action = a
                        action_chosen = True
                        break
                if not action_chosen:
                    action = np.random.choice(self.actions)
        return action

    
    def check_for_discard(self, game_object):
        """
        Checks to see if we are forced to discard
        """
        number_discarded = 0
        discarded = False
        while game_object.hand_limit < len(self.hand):
            self.get_actions(game_object, result_of_attack = False, must_discard = True)
            if self.ishuman:
                self.print_actions()
            action = self.policy()
            if "Discard" in action:
                card = int(action[-1])
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                number_discarded += 1
                discarded = True
                continue
            if self.ishuman: # These actions are taken by humans only
                if action == "View your cards":
                    self.hand = sorted(self.hand)
                    print(self.hand)
                elif action == "View board":
                    game_object.view_board()
                elif action == "View ship part costs":
                    print(game_object.ship_part_costs)
                elif action == "View your resources":
                    print(self.resources_count)
                elif action == "View your ship parts":
                    print(self.ship_parts)
        self.get_actions(game_object) # Resets the game options
        if game_object.verbose and discarded:
            print("Player {0} discarded {1} card(s).".format(self.player_num, number_discarded))
        
    def force_discard(self, game_object, number_to_discard, result_of_attack = False):
        i = 0
        cards_discarded = list()
        while i < number_to_discard:
            self.get_actions(game_object, result_of_attack, must_discard = True)
            if self.ishuman:
                self.print_actions()
            action = self.policy()
            if "Discard" in action:
                card = int(action[-1])
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                cards_discarded.append(card)
                i += 1
                continue
            elif "Give" in action: # Involves giving the cards to another player
                card = int(action[-1])
                self.hand.remove(card)
                cards_discarded.append(card) # Cards will be given to other player 
                i += 1
                continue

            if self.ishuman: # These actions are taken by humans only
                if action == "View your cards":
                    print(self.hand)
                elif action == "View board":
                    game_object.view_board()
                elif action == "View ship part costs":
                    print(game_object.ship_part_costs)
                elif action == "View your resources":
                    print(self.resources_count)
                elif action == "View your ship parts":
                    print(self.ship_parts)
        if game_object.verbose and not result_of_attack:
            print("Player {0} discarded {1} cards.".format(self.player_num, number_to_discard))
        return cards_discarded
                    
    def print_actions(self):
        print("Your actions are:")
        for i, action in enumerate(self.actions):
            print(i, action)
        
    def take_actions(self, game_object):
        """
        A function for handling regular actions a player takes on their turn.
        """
        while True:
            self.check_for_discard(game_object) # Checks for discard and resets game options
            if self.ishuman:
                self.print_actions()
            action = self.policy()
            if game_object.verbose:
                print("Player {0} chose: {1}".format(self.player_num, action))
                print()
            if self.ishuman: # These actions are taken by humans only
                if action == "View your cards":
                    print(self.hand)
                elif action == "View board":
                    game_object.view_board()
                elif action == "View ship part costs":
                    print(game_object.ship_part_costs)
                elif action == "View your resources":
                    print(self.resources_count)
                elif action == "View your ship parts":
                    print(self.ship_parts)
                    
            if "Buy rogue" in action:
                resource = action[-1]
                # Removes the resources
                self.resources_count[resource] -= game_object.rogue_cost
                self.hand.append(0)
                self.check_for_discard(game_object)
                self.bought_rogue = True
            elif "Buy ship part" in action:
                ship_part = int(action[-1])
                cost = game_object.ship_part_costs[ship_part]
                for resource in cost:
                    self.resources_count[resource] -= 1
                self.ship_parts.append(ship_part)
                if len(self.ship_parts) == 3:
                    game_over = True
                    return game_over
            elif "Claim" in action:
                l = action.split()
                space = int(l[2])
                number = int(l[5])
                resource_type = l[6]
                # Adds to the players resource supply and takes over spot on board
                game_object.board[space-1][0] = self.player_num
                self.resources_count[resource_type] += number
                # self.force_discard(game_object, number-1)       # Forces the player to an amount equal to the number of resources minus one
                if self.player_num in game_object.sad_players:  # Before this player was without a home
                    game_object.sad_players.remove(self.player_num)
                return False
            elif "Collect" in action:
                l = action.split()
                card = int(l[9])
                space = int(l[6])
                resource_type = game_object.board[space-1][1]
                self.resources_count[resource_type] += 1
                self.hand.remove(card)                          # Removes the card from the player's hand
                if card != 0:                                   # Card is not a rogue
                    game_object.discard_pile.append(card)
                return False                                    # Action ends turn
            elif "Attack" in action:
                l = action.split()
                card = int(l[-1])
                space = int(l[2])
                defender_num = game_object.board[space-1][0]
                resource_type = game_object.board[space-1][1]
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                winner_num = game_object.attack_sequence(self.player_num, defender_num, space) # Carries out an attack sequence
                if winner_num == defender_num:
                    if game_object.verbose:
                        print("The attack has been thwarted by the defender.")
                    return False # Attack has been thwarted and the turn ends
                else: # Attack was a success
                    amount = game_object.present - space + 1
                    loser = game_object.players[defender_num]
                    resource_number, card_list = loser.loses(game_object, amount, resource_type) # Loser loses a certain amount of things
                    if game_object.verbose:
                        print("The attacker takes over space {}.".format(space))
                        print("As a reward, they recieve {0} {1} resources and {2} cards.".format(resource_number, resource_type, len(card_list)))
                    if self.ishuman:
                        print("Player {0}, you collected the following cards: {1}".format(self.player_num, str(card_list)))
                    self.gains(game_object, resource_type, resource_number, card_list)   # Winner reaps their spoils
                    game_object.board[space-1][0] = self.player_num         # The player that won now takes over the spot
                    if defender_num not in {game_object.board[i][0] for i in range(game_object.board_size)}: # If player not anywhere else on board
                        game_object.sad_players.append(defender_num)     # The losing player is now outcast
                    if self.player_num in game_object.sad_players:  # Before this player was without a home. Now they have one.
                        game_object.sad_players.remove(self.player_num)
                    return False
            elif "Takeover" in action:
                l = action.split()
                card = int(l[-1])
                space = int(l[2])
                game_object.board[space-1][0] = self.player_num
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                if self.player_num in game_object.sad_players:  # Before this player was without a home. Now they have one.
                    game_object.sad_players.remove(self.player_num)
                return False
            elif action == "End turn":
                return False
            
    def gains(self, game_object, resource_type, resource_number, card_list):
        self.resources_count[resource_type] += resource_number
        self.hand += card_list
        if len(self.hand) > game_object.hand_limit:
            number_to_discard = len(self.hand) - game_object.hand_limit
            self.force_discard(game_object, number_to_discard)
            
            
    def loses(self, game_object, amount_lost, resource_type, from_asteroid = False):
        currently_have = self.resources_count[resource_type]
        difference = currently_have - amount_lost
        
        if difference >= 0:
            self.resources_count[resource_type] -= amount_lost
            resource_number = amount_lost
            card_list = []
        else:
            self.resources_count[resource_type] -= currently_have
            resource_number = currently_have
            num_cards = abs(difference) // 2 + 1 # Pay the rest as cards (2 for 1) rounded up
            if num_cards > len(self.hand):
                num_cards = len(self.hand) # Gives up rest of cards 
            if not from_asteroid:
                card_list = self.force_discard(game_object, num_cards, result_of_attack = True)
            else:
                card_list = self.force_discard(game_object, num_cards)
                
        return resource_number, card_list
    
    def continue_attacking(self, game_object, space):
        while True:
            if game_object.verbose:
                print()
                print("Player {}, you are attacking".format(self.player_num))
            self.get_actions(game_object, result_of_attack = True, attacking_space = space)
            if self.ishuman:
                self.print_actions()
            action = self.policy()
            if "again" in action:
                card = int(action[-1])
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                if game_object.verbose:
                    print("Player {0} launches another attack with a {1}!".format(self.player_num, card))
                return True
            elif "Stop" in action:
                if game_object.verbose:
                    print("Player {} decides to withdraw.".format(self.player_num))
                return False
            
            if self.ishuman: # These actions are taken by humans only
                if action == "View your cards":
                    print(self.hand)
                elif action == "View board":
                    game_object.view_board()
                elif action == "View ship part costs":
                    print(game_object.ship_part_costs)
                elif action == "View your resources":
                    print(self.resources_count)
                elif action == "View your ship parts":
                    print(self.ship_parts)
                    
    def defend(self, game_object, space, from_asteroid = False, first_time_defense = False):
        while True:
            if game_object.verbose and self.ishuman:
                print()
                print("Player {}, you are defending".format(self.player_num))
            self.get_actions(game_object, result_of_attack = True, attacking_space = space, defending = True, from_asteroid = from_asteroid, first_time_defense = first_time_defense)
            if self.ishuman:
                self.print_actions()
            action = self.policy()
            if "Defend" in action:
                card = int(action[-1])
                self.hand.remove(card)
                if card != 0:
                    game_object.discard_pile.append(card)
                if game_object.verbose:
                    if not from_asteroid:
                        print("Player {0} blocks the attack with a {1}!".format(self.player_num, card))
                    else:
                        print("Player {0} blocks the asteroid with a {1}!".format(self.player_num, card))
                return True
            elif "Surrender" in action:
                if game_object.verbose:
                    if not from_asteroid:
                        print("Player {0} surrenders space {1}.".format(self.player_num, space))
                    else:
                        print("Player {0} is destroyed by an asteroid on space {1}!".format(self.player_num, space))
                return False
            
            if self.ishuman: # These actions are taken by humans only
                if action == "View your cards":
                    print(self.hand)
                elif action == "View board":
                    game_object.view_board()
                elif action == "View ship part costs":
                    print(game_object.ship_part_costs)
                elif action == "View your resources":
                    print(self.resources_count)
                elif action == "View your ship parts":
                    print(self.ship_parts)
        
        
            
                    
class TemporiumGame:
    def __init__(self, num_players, num_humans = 0, verbose = True):
        
        self.num_players = num_players
        self.num_humans = num_humans
        assert self.num_humans <= self.num_players
        self.get_highest_card = {2: 6, 3: 7, 4: 9}
        self.dice = [1,2,3,4,5,6]
        self.draw_pile = [i for i in range(1,self.get_highest_card[self.num_players]+1)]*9
        self.discard_pile = []
        self.resources = ["R", "B", "K", "Y"]
        self.board_size = self.get_highest_card[self.num_players]
        self.board = []
        self.present = num_players
        self.players = dict()
        self.curr_round = 1
        self.starting_hand_size = 6
        self.hand_limit = 7
        self.ship_part_cost_size = 4
        self.num_ship_parts = 3
        self.ship_part_costs = {i : [np.random.choice(self.resources) for i in range(self.ship_part_cost_size)] for i in range(1,self.num_ship_parts+1)}
        self.verbose = verbose
        self.round = 0 # Number for the starting round
        self.get_death_round = {2: 13, 3: 15, 4: 19}
        self.death_round = self.get_death_round[self.num_players]
        self.sad_players = []
        self.rogue_cost = 3
        self.starting_player_order = []
        
    def view_board(self):
        print("Space:          ", end = '')
        for i, element in enumerate(self.board):
            print("  {0}   ".format(i + 1), end = '')
        print()
        print("Controlled by: |", end = '')
        for i, element in enumerate(self.board):
            print("  {0}  |".format(element[0]), end = '')
        print()
        print("Resource Type: |", end = '')
        for i, element in enumerate(self.board):
            print("  {0}  |".format(element[1]), end = '')
        print()
        print("Number:        |", end = '')
        for i, element in enumerate(self.board):
            print("  {0}  |".format(element[2]), end = '')
        print()
        print()
            
    def attack_sequence(self, attacker_num, defender_num, space, from_asteroid = False):
        
        if self.verbose:
            if attacker_num == 0:
                print("An asteroid hits Player {0} on space {1}!".format(defender_num, space))
           
        if attacker_num != 0:
            attacker = self.players[attacker_num] # Get the attacker and defender player objects
        defender = self.players[defender_num]
        
        first_time = True
        while True:
            defended = defender.defend(self, space, from_asteroid = from_asteroid, first_time_defense = first_time)
            first_time = False
            if defended:
                if attacker_num != 0:
                    continue_attacking = attacker.continue_attacking(self, space)
                    if continue_attacking:
                        continue
                    else:
                        winner = defender_num
                        break
                else: # Attack was from an asteroid
                    winner = defender_num
                    break
            else:
                winner = attacker_num
                break
        return winner
        
    def generate_board(self):
        resources_left = list(self.resources)
        resources_added = {i : 0 for i in self.resources}
        for i in range(self.board_size):
            resource = np.random.choice(self.resources)
            self.board.append([0, resource, 0])
            resources_added[resource] += 1
            try:
                resources_left.remove(resource)
            except ValueError:
                pass
        
        for i in reversed(range(self.board_size)):
            # Handles the case where all the resources didn't get on the board
            if len(resources_left) == 0:
                break
            else:
                resource2 = self.board[i][1]
                if resources_added[resource2] > 1:
                    resource1 = resources_left.pop()
                    resources_added[resource2] -= 1
                    resources_added[resource1] += 1
                    self.board[i][1] = resource1
                
    def roll(self):
        """
        Rolls the dice.
        """
        return np.random.choice(self.dice)
    
    def draw(self):
        """
        Draws a card from the draw pile.
        """
        if len(self.draw_pile) == 0:
            self.draw_pile = self.discard_pile
            np.random.shuffle(self.draw_pile)
        return self.draw_pile.pop()
    
    def draw_resource(self):
        """
        Draws a resource.
        """
        return np.random.choice(self.resources)
    
    def discard(self, card_num):
        """
        Discards a card.
        """
        self.discard.append(card_num)
        
    def deal(self):
        """
        Deals to players at beginning of game.
        """
        for i in range(self.starting_hand_size):
            for player in self.players.values():
                player.hand.append(self.draw())
                
    def set_player_order(self):
        """
        Sets the player order for the current round.
        """
        self.player_order = [i for i in range(self.num_players)]
        
    def run_setup(self):
        if self.verbose:
            print("Players are:")
        for i in range(1,self.num_humans+1):
            self.players[i] = Player(i, self, True)
            if self.verbose:
                print("Player {} (Human)".format(i))
        for j in range(self.num_humans+1, self.num_players+1):
            self.players[j] = Player(j, self)
            if self.verbose:
                print("Player {} (AI)".format(j))
        if self.verbose:
            print()
        
        # Deals the hands
        np.random.shuffle(self.draw_pile)
        self.deal()
        self.player_order = [i for i in range(1, self.num_players+1)] # Sets player order for the first round randomly
        np.random.shuffle(self.player_order)
        
        # Generates the board
        self.generate_board()
        for i in range(self.present):
            self.board[i][2] = self.roll() # Updates the board to include numbers on spaces
        
        # Players start by choosing starting positions and discarding cards
        if self.verbose:
            print("SETUP:")
            print("Randomly chosen player order is:", self.player_order)
        while self.player_order:
            curr_player = self.players[self.player_order.pop(0)]
            if self.verbose:
                print("It's Player {}'s turn.".format(curr_player.player_num))
                input("Hit Enter...")
                print("The board is:")
                self.view_board()
                print("The ship part costs are:")
                print(self.ship_part_costs)
                print()
                print("Your hand is:")
                curr_player.hand = sorted(curr_player.hand)
                print(curr_player.hand)
                print("Your resources are:")
                print(curr_player.resources_count)
            curr_player.take_actions(self)
            
            
    def new_round(self):
        if self.round == 0: # Start of game
            self.round = 2*self.num_players - 1
            if self.verbose:
                print()
                print("WELCOME TO ROUND {}:".format(self.round - 2*(self.num_players-1)))
                print()
            for i in range(self.present):
                self.player_order.append(self.board[i][0])
                self.starting_player_order = list(self.player_order)
        else:
            self.round += 1
            if self.verbose:
                print()
                print("WELCOME TO ROUND {}:".format(self.round - 2*(self.num_players-1)))
                print()
            if self.round == self.death_round:
                if self.verbose:
                    print("Asteroids and a gravity well destroy the planet. Unfortunately everyone dies.")
                return True
            else:
                 # Players collect resources
                for space in self.board:
                    if space[0] != 0:
                        resource = space[1]
                        lucky_player = self.players[space[0]] # Gets the player who has played on current space
                        lucky_player.resources_count[resource] += 1 # Gives the player their resource
                        if self.verbose:
                            print("Player {0} gets a {1}".format(lucky_player.player_num, space[1]))
                 
                # Asteroid hits or we go to a new round
                if self.round%2 == 0:
                    asteroid = self.roll()
                    spaces_players = list()
                    for i in range(self.present):
                        if asteroid == self.board[i][2] and self.board[i][0] != 0:
                            spaces_players.append([i+1, self.board[i][0]])
                    if self.verbose:
                        print()
                        print("The asteroid roll was:", asteroid)
                        print("Spaces hit:")
                        print([element[0] for element in spaces_players])
                        print("Players hurt:")
                        print([element[1] for element in spaces_players if element[1] != 0])
                        print()
                    for space, player_num in spaces_players:
                        # Handles case for getting hit by an asteroid
                        winner = self.attack_sequence(attacker_num = 0, defender_num = player_num, space = space, from_asteroid = True) # By denoting the attacker was Player 0, this is an asteroid
                        if winner == 0:
                            amount = self.present - space + 1
                            loser = self.players[player_num]
                            resource_type = self.board[space-1][1]
                            resource_number, card_list = loser.loses(self, amount, resource_type, from_asteroid = True) # Loser loses a certain amount of things
                            if self.verbose:
                                print("Unfortunately, Player {3} loses {0} {1} resources and {2} cards.".format(resource_number, resource_type, len(card_list), player_num))
                                print()
                            self.board[space-1][0] = 0         # The player that won now takes over the spot
                            if loser.player_num not in {self.board[i][0] for i in range(self.board_size)}: # If player not anywhere else on board
                                self.sad_players.append(player_num)     # The losing player is now outcast
                            
                else:
                    num = self.roll()
                    i = (self.round-1)//2
                    self.board[i][2] = num
                    self.present += 1
                    if self.verbose:
                        print("Added the number {0} to board space {1}".format(num, i+1))
                        print("It is now year", self.present)
                        
                # Determines Player Order
                for space in self.board:
                    if space[0] != 0:
                        if space[0] not in self.player_order:
                            self.player_order.append(space[0])
                if len(self.sad_players) > 0:
                    for i in self.sad_players:
                        if i not in self.player_order:
                            self.player_order.append(i)
                
                if self.verbose:
                    print("Based on the board, the player order is:", self.player_order)
                    print()
                        
                        
    def start_game(self, verbose=False):
        """
        Starts and runs through the game.
        """
        game_over = False
        if self.verbose:
            print("--------------")
            print("| START GAME |")
            print("--------------")
            
        self.run_setup()
        while not game_over:
            try:
                curr_player = self.players[self.player_order.pop(0)]
            except IndexError:
                game_over = self.new_round() # Starts a new round if all players have gone
                if game_over:
                    break
                curr_player = self.players[self.player_order.pop(0)]
            
            drawn_card = self.draw()
            curr_player.hand.append(drawn_card)
            curr_player.bought_rogue = False
            if curr_player.ishuman: # Handles case where player is human
                print("Player {}, it's your turn.".format(curr_player.player_num))
                input("Hit Enter...")
                print("The board is:")
                self.view_board()
                print("The ship part costs are:")
                print(self.ship_part_costs)
                print()
                print("You drew a {}.".format(drawn_card))
                print("Your hand is:")
                curr_player.hand = sorted(curr_player.hand)
                print(curr_player.hand)
                print("Your resources are:")
                print(curr_player.resources_count)
            elif self.verbose: # Player is not human
                print("It's Player {}'s turn. (AI)".format(curr_player.player_num))
                input("Hit Enter...")
                print("The board is:")
                self.view_board()
                print("The ship part costs are:")
                print(self.ship_part_costs)
                print()
                print("They drew a {}.".format(drawn_card))
                print("Their hand is:")
                curr_player.hand = sorted(curr_player.hand)
                print(curr_player.hand)
                print("Their resources are:")
                print(curr_player.resources_count)
                print("Their ship parts are:")
                print(curr_player.ship_parts)
                
            game_over = curr_player.take_actions(self)
        
        if self.round != self.death_round:
            # print("Player {} won!".format(curr_player.player_num))
            return self.starting_player_order, curr_player.player_num
        else:
            return self.starting_player_order, 0
                
                        
                    
                
    
        
        
                    
                        
        

