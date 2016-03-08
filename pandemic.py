# For Python 2.7.3
# A non-graphic take on Pandemic the Board Game by Matt Leacock. 
# Code written by Shay Culpepper, 2015-2016

from random import randint
from random import shuffle
import copy

current_infection = set([])
player_cards = []
player_discard = {}
events_discard = {}
infection_cards = []
infection_discard = []
research_stations = {}
cities = {}
the_team = {}
players = []
infection_rate = [2,2,2,3,3,4,4]
enders = {'epidemics': 0, 'outbreaks': 0}
oqn = {'on': False}
the_cubes = {
  'blue': {'left': 24, 'cities': {}, 'eradicated': False, 'cured': False},
  'yellow': {'left': 24, 'cities': {}, 'eradicated': False, 'cured':  False},
  'red': {'left': 24, 'cities': {}, 'eradicated': False, 'cured': False},
  'black': {'left': 24, 'cities': {}, 'eradicated': False, 'cured': False}
}
roles = {
  'Researcher': "as an action you may give (or a player can take) any City card from your hand. You must both be in the same city. The card does not have to match the city you are in.",
  'Scientist': "you need only 4 cards of the same color to discover a cure instead of five.",
  'Medic': "you can remove all cubes of one color when doing treat disease. If a disease is cured, you will automatically remove all cubes from any city you are in.",
  'Contingency Planner': "as an action, rake any discarded Event card and store it on your card (max 1 at a time). Once you've played it, it will be removed from the game",
  'Quarantine Specialist': "you will prevent disease cube placements (and outbreaks) in the city you are in and all cities connected to it.",
  'Dispatcher': "move another player's pawn as if it were yours. As an action, move any pawn to a city with another pawn. (Get permission before moving another player's pawn.",
  'Operations Expert': "as an action, you can build a research station in the city you are in (no City card needed). Once per turn as an action, move from a research station to any city by discarding any city card."
}
levels = {'Introductory': 4, 'Standard': 5, 'Heroic': 6}
event_powers = {
	'Forecast': "see and rearrange the next six cities to be infected.",
	'Airlift': "move any player to any city. (Get permission!)",
	'Government Grant': 'add one research station to any city',
	'Resilient Population': 'remove any city from the game, keeping it from further infection. You may play this betern the Infet and intensify steps of an epidemic',
	'One Quiet Night': "no cities will be infected tonight (after one player's turn"
}

def next():
	raw_input(
	'(press enter)')

class City(object):
  def __init__(self, name, population = 0, std_disease = 'blue', neighbor_list = []):
    self.name = name
    self.population = population
    self.disease = {
      "blue": {"cubes": 0, 'default': False, 'name': "blue"}, 
      "yellow": {"cubes": 0, "default": False, "name": "yellow"}, 
      "red": {"cubes": 0, "default": False, "name": "red"}, 
      "black": {"cubes": 0, "default": False, 'name': 'black'}
    }
    self.default = std_disease
    self.disease[std_disease]["default"] = 1
    the_cubes[std_disease]['cities'][self.name] = self
    self.research_station = False
    player_cards.append(self)
    infection_cards.append(self)
    cities[name] = self
    self.neighbor_list = neighbor_list
    self.neighbors = {}

  def cube_count(self):
    total = self.disease['blue']['cubes'] + self.disease['yellow']['cubes'] + self.disease['red']['cubes'] + self.disease['black']['cubes']
    return total 
    
  # Give current disease status of cities
  def current_status(self): 
    print "%s:" % (self.name),
    for color in ['blue','red','yellow','black']:
      if self.disease[color]['cubes'] != 0:
      	print "%s %s." % (color.capitalize(), self.disease[color]['cubes']),
    print "\n"
    # print "Blue: %s, Red: %s, Black: %s, Yellow: %s" % (self.disease['blue']['cubes'], self.disease['red']['cubes'], self.disease['black']['cubes'], self.disease['yellow']['cubes'])
    
  # Add Neighbors
  def add_neighbors(self, all_neighbors):
    for neighbor in all_neighbors:
      self.neighbors[neighbor.name] = neighbor
  
  # Get infected
  def infect(self, cubes = 1, color = None, initial = True, setup = False):
    if color == None:
      color = self.default
    if initial:
      current_infection.clear()
    if the_cubes[color]['eradicated'] != True and self not in current_infection:
      if medic.city == self and the_cubes[color]['cured'] and 'Medic' in the_team:
        print "%s has been saved by the Medic from being infected" % (self.name)
      elif (quarantine_specialist.city == self or self.name in quarantine_specialist.city.neighbors) and not setup and 'Quarantine Specialist' in the_team:
        print "%s has been saved by the Quarantine Specialist from being infected" % (self.name)
      else:
        current_infection.add(self)
        self.disease[color]['cubes'] += cubes
        the_cubes[color]['left'] -= cubes
        if self.disease[color]['cubes'] > 3:
          self.disease[color]['cubes'] = 3
          print "%s has been infected! %s infection level: %s" % (self.name, self.disease[color]['name'].capitalize(), self.disease[color]['cubes'])
          self.outbreak(color)
        else:
          print "%s has been infected! %s infection level: %s" % (self.name, self.disease[color]['name'].capitalize(), self.disease[color]['cubes'])
  
  # Outbreak!
  def outbreak(self, color):
    print "There has been an outbreak!"
    enders['outbreaks'] += 1
    for victim in self.neighbors:
        cities[victim].infect(1, color, False)
          
  # Get treated
  def be_treated(self, treat_color, medic = False):
    print "%s's %s infection level has been reduced from level %s" % (self.name, treat_color, self.disease[treat_color]['cubes'] ),
    if the_cubes[treat_color]['cured'] == True or medic:
      the_cubes[treat_color]['left'] += self.disease[treat_color]['cubes']
      self.disease[treat_color]['cubes'] = 0
    elif self.disease[treat_color]['cubes'] > 0:
      self.disease[treat_color]['cubes'] -= 1
      the_cubes[treat_color]['left'] += 1
    else: 
      pass 
    print  "to %s" %  (self.disease[treat_color]['cubes'])
    if the_cubes[treat_color]['left'] == 24 and the_cubes[treat_color]['cured']:
      print "Congratulations! You have eradicated %s disease" % (treat_color)
      the_cubes[treat_color]['eradicated'] = True
      
  # Add research station to board
  def add_research_station(self):
    self.research_station = True
    research_stations[self.name] = self
  
  # Go to this city
  def go_to_option(self):
    print "Go to", self.name,"(",
    for color in self.disease:
      if self.disease[color]['cubes'] != 0:
        print "%s %s" % (self.disease[color]['cubes'], self.disease[color]['name']), 
    print ")"

# Blue Cities created
City("San Francisco", 5864000, "blue", ['Chicago', 'Los Angeles', 'Tokyo'])
City("Essen", 575000, "blue", ['London', 'Paris', 'Milan', 'St. Petersburg'])
City("St. Petersburg", 4879000, "blue", ['Essen', 'Moscow', 'Istanbul'])
City("Milan", 5232000, "blue", ['Paris', 'Essen', 'Istanbul'])
City("Montreal", 3429000 , "blue", ['New York', 'Washington', 'Chicago'])
City("New York", 20464000 , "blue", ['Montreal', 'Washington', 'London', 'Madrid'])
City("Chicago", 9121000, "blue", ['Atlanta', 'Montreal', 'San Francisco', 'Mexico City', 'Los Angeles'])
City("Madrid", 5427000 , "blue", ['Algiers', 'Paris', 'London', 'New York'])
City("Paris", 10755000, "blue", ['Essen', 'Milan', 'Algiers', 'London', 'Madrid'])
City("London", 856000, "blue", ['Essen', 'Paris', 'Madrid', 'New York'])
City("Washington", 4679000, "blue", ['New York', 'Montreal', 'Atlanta', 'Miami'])
City("Atlanta", 4715000, "blue", ['Chicago', 'Washington', 'Miami'])

# Yellow Cities Created
City("Mexico City", 19463000, "yellow", ['Los Angeles', 'Chicago', 'Miami', 'Bogota', 'Lima'])
City("Buenos Aires", 13669000, "yellow", ['Bogota', 'Sao Paulo']) 
City("Sao Paulo", 20186000, "yellow", ['Madrid', 'Lagos', 'Bogota', 'Buenos Aires'])
City("Santiago", 6015000, "yellow", ['Lima'])
City("Kinshasa", 9046000, "yellow", ['Khartoum', 'Johannesburg', 'Lagos'])
City("Miami" , 5582000, "yellow", ['Atlanta', 'Washington', 'Bogota', 'Mexico City'])
City("Los Angeles", 14900000, "yellow", ['San Francisco', 'Mexico City', 'Sydney'])
City("Lima", 9121000, "yellow", ['Mexico City', 'Bogota', 'Santiago'])
City("Khartoum", 4887000, "yellow", ['Cairo', 'Lagos', 'Kinshasa', 'Johannesburg'])
City("Lagos", 11547000, "yellow",['Khartoum', 'Kinshasa', 'Sao Paulo'])
City("Bogota", 8702000, "yellow", ['Miami', 'Mexico City', 'Lima', 'Buenos Aires', 'Sao Paulo'])
City("Johannesburg", 3888000, "yellow", ['Khartoum', 'Kinshasa'])

# Black Cities Created 
City("Istanbul", 13576000, "black",['St. Petersburg', 'Milan', 'Algiers', 'Cairo', 'Baghdad', 'Moscow'])
City("Delhi", 22242000, "black", ['Tehran', 'Karachi', 'Mumbai', 'Chennai', 'Kolkata'])
City("Cairo", 14718000, "black", ['Algiers', 'Istanbul', 'Baghdad', 'Riyadh', 'Khartoum'])
City("Baghdad", 6204000, "black", ['Istanbul', 'Cairo', 'Riyadh', 'Karachi', 'Tehran'])
City("Chennai", 8865000, "black", ['Mumbai', 'Delhi', 'Kolkata', 'Bangkok', 'Jakarta'])
City("Tehran", 7419000, "black", ['Moscow', 'Baghdad', 'Karachi', 'Delhi'])
City("Kolkata", 14374000, "black", ['Delhi', 'Chennai', 'Bangkok', 'Hong Kong'])
City("Riyadh", 5037000, "black", ['Cairo', 'Baghdad', 'Karachi'])
City("Moscow", 15512000, "black", ['St. Petersburg', 'Istanbul', 'Tehran'])
City("Karachi", 20711000, "black", ['Tehran', 'Baghdad', 'Riyadh', 'Delhi', 'Mumbai'])
City("Mumbai", 16910000, "black", ['Karachi', 'Delhi', 'Chennai'])
City("Algiers", 2946000, "black", ['Madrid', 'Paris', 'Istanbul', 'Cairo'])

# Red Cities Created
City("Jakarta", 26063000, "red", ['Chennai', 'Bangkok', 'Ho Chi Minh City', 'Sydney'])
City("Taipei", 8338000 , "red", ['Osaka', 'Shanghai', 'Hong Kong', 'Manila'])
City("Sydney", 3785000, "red", ['Los Angeles', 'Manila', 'Jakarta'])
City("Osaka", 2871000, "red", ['Tokyo', 'Taipei'])
City("Beijing", 17311000, "red", ['Seoul', 'Shanghai'])
City("Ho Chi Minh City", 8314000, "red", ['Jakarta', 'Bangkok', 'Hong Kong', 'Manila'])
City("Manila", 20767000, "red", ['San Francisco', 'Sydney', 'Ho Chi Minh City', 'Hong Kong', 'Taipei'])
City("Bangkok", 7151000, "red", ['Kolkata', 'Hong Kong', 'Ho Chi Minh City', 'Jakarta', 'Chennai'])
City("Shanghai", 13482000, "red", ['Beijing', 'Seoul', 'Tokyo', 'Taipei', 'Hong Kong'])
City("Tokyo", 13189000, "red", ['San Francisco', 'Seoul', 'Osaka','Shanghai'])
City("Hong Kong", 7106000, "red", ['Shanghai', 'Taipei', 'Manila', 'Ho Chi Minh City', 'Bangkok', 'Kolkata'])
City("Seoul", 22574000, "red", ['Beijing', 'Shanghai', 'Tokyo'])

for city in cities:
  for neighbor in cities[city].neighbor_list:
    cities[city].neighbors[neighbor] = cities[neighbor]

# Create all player cards
the_players = []
class Player(object):
  def __init__(self, name, color, needed_cards = 5): 
    self.name  = name
    self.color = color
    self.hand  = {}
    self.cp_hand = {}
    self.action_options = {}
    self.needed_cards = needed_cards
    self.max_pop = 0
    self.city = cities['Atlanta']
    self.role = roles[name]
    self.hand_title = "** %s " % (name.upper())
    while len(self.hand_title) < 30:
      self.hand_title += "*"
    the_players.append(self)
    
  # Add card to hand
  def add_to_hand(self, card):
    self.hand[card.name] = card
    if self.hand[card.name].default != 'event':
      self.max_pop = max(self.max_pop, self.hand[card.name].population)
    while len(self.hand) > 7:
      self.current_hand()
      self.discard(self.get_answer(self.hand, prompt = "\nYou have too many cards. Please choose one to discard"))
  
  # Discard 
  def discard(self, card):
    if card.name in self.hand:
      if card.default == 'event':
        discard = self.hand.pop(card.name)
        events_discard[card.name] = discard
      else:
        discard = self.hand.pop(card.name)
        player_discard[card.name] = discard
      print "You have discarded", card.name
    elif card.name in self.cp_hand:
      self.cp_hand.pop(card.name)
      print "%s has been removed from the game" % card.name
    else: 
      print "There was a problem discarding"
  
  # Give card to another player
  def give_card(self, card, friend):
    given_card = self.hand.pop(card.name)
    print self.name, "has given", card.name, "to", friend.name
    friend.add_to_hand(card)
    
  # Check current hand
  def current_hand(self, what = 'all'):
    print "\n ", self.hand_title
    print "  ** Current hand:"
    '''    if what == 'all' or what == 'colors':
      for color in ["blue", "yellow", "red", "black"]:
        print "\n* %s:" % (self.city.disease[color]['name']),
        for card in self.hand:
          if self.hand[card].default == color:
            print "%s." % (card),
    '''
    if what == 'all' or what == 'colors':
      for card in self.hand:
        print "  ** %s (%s)" % (card,self.hand[card].default)
    if what == 'events':
      for card in self.hand:
        if self.hand[card].default == 'event':
          print "\n* Event: %s" % (card)
    '''
    if what == 'all' or what == 'events':
      for card in self.hand:
        if self.hand[card].default == 'event':
          print "\n* Event: %s" % (card),
    '''
    if self == contingency_planner:
      for card in self.cp_hand:
        print "\n* Event Stored:", card

    print "  ******************************"
        
  # Check for errors and get a good response       
  def get_answer(self, list, repeat = None, dict = True, strings = False, prompt = "", back = True, args = None, all_lower = False):
    if repeat == None:
      repeat = self.new_action
    print prompt
    while True:
      try: 
      	if all_lower == True: 
      		answer = raw_input().lower()
        else:
        	answer = raw_input()
        if dict: 
          intended_object = list[answer]
        elif strings :
          intended_object = answer
        else:
          for x in list:
            if answer == x.name:
              new_answer = x
          intended_object = list[list.index(new_answer)]
        return intended_object
        break
      except (ValueError, NameError, KeyError):
        if back == True:
          if answer == "back":
            repeat(args)
            break
          elif answer == "Event":
            self.play_event_card()
            break
          else: 
            print "Please give a valid response"
        else:
          if answer == "Event":
            self.play_event_card()
            repeat(args)
            break
          else: 
            print "Please give a valid response"
  
  # Define Go To Cities
  def go_to_cities(self, list):
    for city in list:
      if city in cities and city != self.city.name:
        cities[city].go_to_option()
          
  # Define Drive
  def drive(self, being_dispatched = None):  
    # Print all options
    print "\nTo what city would you like to drive or ferry?"
    self.go_to_cities(self.city.neighbors)
    new_city = self.get_answer(self.city.neighbors, args = being_dispatched)
    if new_city != None:
      self.city =  new_city
      print "You have been moved to the neighbor city %s." % (self.city.name)    
    
  # Define Direct Flight
  def direct(self, being_dispatched = None):
    print "\nTo what city would you like to take a direct flight? (Discard choice from hand)"
    if being_dispatched:
      the_hand = dispatcher.hand
    else:
      the_hand = self.hand
    self.go_to_cities(the_hand)
    new_city = self.get_answer(the_hand, args = being_dispatched)
    if new_city != None:
      self.city = new_city
      if being_dispatched:
        dispatcher.discard(self.city)
      else:
        self.discard(self.city)
      print "You have have taken a direct flight to %s." % (self.city.name)
 
  # Define Charter Flight
  def charter(self, being_dispatched = None):
    print "\nWhere would you like your charter flight to take you (Discard %s)?" % (self.city.name)
    self.go_to_cities(cities)
    new_city = self.get_answer(cities, args = being_dispatched)
    if new_city != None:
      self.discard(self.city)
      self.city = new_city
      print "You have taken a charter flight to %s." % (self.city.name)
    
  # Define Shuttle Flight
  def shuttle(self, being_dispatched = None):
    print "\nWhere would you like your shuttle flight to go? (By research station)"
    self.go_to_cities(research_stations)
    new_city = self.get_answer(research_stations, args = being_dispatched)
    if new_city != None:
      self.city = new_city
      print "You have been moved to the %s research station." % (self.city.name)
    
  # Define Treat Disease
  def treat(self, args = False):
    cc = {}
    for color in the_cubes:
      if self.city.disease[color]['cubes'] > 0:
        cc[color] = color
        chosen = color
    if len(cc) > 1:
      print "Which disease would you like to treat?"
      self.city.current_status()
      chosen = self.get_answer(cc, all_lower = True)
    if chosen != None:
      if self == medic:
        self.city.be_treated(chosen,  medic = True)
      else:
        self.city.be_treated(chosen)
    
  # Define Build Research Station
  def build_research_station(self, args = False):
    self.city.add_research_station()
    if self != operations_expert:
      self.discard(self.city)
    print "You have built a research station in", self.city.name
    print "You can build up to %s more research stations." % (6 - len(research_stations))
  
  # Define Give knowledge
  def give_knowledge(self, args = False): 
    friends = {}
    print "Who would you like to share knowledge with?"
    for each in players:
      if each == self:
        continue
      elif each.city == self.city:
        friends[each.name] = each
        print "Share knowledge with %s" % (each.name)
    friend = self.get_answer(friends)
    if friends != None:
      self.give_card(self.city, friend)
    
  # Define Take knowledge
  def take_knowledge(self, args = False):
    for each in players:
      if each != self and each.city == self.city and self.city.name in each.hand:
        each.give_card(self.city, self)
  
  # Define Research
  def research(self, args = False):
    friends = {}
    print "Who would you like to do research with?"
    for each in players:
      if each == self:
        continue
      elif each.city == self.city:
        friends[each.name] = each
        print "\tMedicResearch with %s" % (each.name)
    friend = self.get_answer(friends)
    if friend != None:
      direction = self.get_answer(['Take', 'Give'], dict = False, strings = True, prompt = "Would you like to give or take knowledge?")
      if direction != None:
        if direction == 'Take':
          print "What information would you like to take?"
          card_options = {}
          for card in friend.hand:  
            if friend.hand[card].default != 'event':
              print "\t", card
              card_options[card] = friend.hand[card]
          card_to_take  = self.get_answer(card_options)
          if card_to_take != None:
            friend.give_card(card_to_take, self)
        
        elif direction == 'Give':
          print "What information would you like to give?"
          card_options = {}
          for card in self.hand:  
            if self.hand[card].default != 'event':
              print "\t", card
              card_options[card] = self.hand[card]
          card_to_take  = self.get_answer(card_options)
          if card_to_take != None:
            self.give_card(card_to_take, friend)

  # Define Discover Cure 
  def discover_cure(self, args = False):
    counts = {"blue": 0, "yellow": 0, "red": 0, "black": 0}
    for color in counts:
      for card in self.hand:
        if self.hand[card].default == color:
          counts[color] += 1
      if counts[color] == self.needed_cards:
        print "Congratulations! You have found a cure for %s disease!" % (color)
        science = {}
        for card in self.hand:
          if self.hand[card].default == color:
            science[card] = self.hand[card]
        for card in science:
            self.discard(self.hand[card])
        the_cubes[color]['cured'] = True
      elif counts[color] > self.needed_cards: 
        print "Which information would you like to submit for the cure?"
        science = {}
        for card in self.hand:
          if self.hand[card].default == color:
            print self.hand[card].name       
            science[card] = self.hand[card]
        choices = []
        counter = 1
        while len(choices) < self.needed_cards:
          print "Card %s:" % (counter)
          card = self.get_answer(science, self.discover_cure)
          if card != None:
            choices.append(card)
            counter += 1
        if card != None:
          for options in choices:
            self.discard(options)
          print "Congratulations! You have found a cure for %s disease!" % (color)
          the_cubes[color]['cured'] = True

  # function for each new action
  def new_action(self, being_dispatched = False): 
    self.action_options.clear()
    print "%s, you are in %s." % (self.name, self.city.name)
    if not being_dispatched:
      self.current_hand()
    print "\nWhat would you like to do?"
  ### STANDARD ACTIONS ###
    
    # Drive
    print "\tDrive: Drive or ferry to a neighbor."
    self.action_options['Drive']  = self.drive
    
    # Direct
    if len(self.hand) > 0:
      print "\tDirect: Take a direct flight to a city in my hand."
      self.action_options['Direct'] = self.direct 
      
    # Charter Flight
    if (self.city.name in self.hand and not being_dispatched) or (self.city.name in dispatcher.hand and being_dispatched):
      print "\tCharter: Charter flight anywhere (Discard current city)"
      self.action_options['Charter'] = self.charter
    
    # Shuttle Flight
    if self.city.research_station and len(research_stations) > 1:
      print "\tShuttle: Shuttle flight from one research station to another."
      self.action_options['Shuttle'] = self.shuttle

    # Share Knowledge  
    for friend in players:
      if friend == self or being_dispatched: 
        continue
      elif friend.city == self.city and self == researcher:
        print "\tResearch: Share knowledge with %s (take or share any card)" % (friend.name)
        self.action_options['Research'] = self.research 
      elif friend.city == self.city and friend.city.name in friend.hand:
        print "\tTake: Share konwledge (take card from %s)" % (friend.name)
        self.action_options['Take'] = self.take_knowledge
      elif friend.city == self.city and self.city.name in self.hand:
        print "\tGive: Share knowledge (give care to %s)" % (friend.name)
        self.action_options['Give'] = self.give_knowledge

    # Treat disease
    if self.city.cube_count() > 0 and not being_dispatched:
      print "\tTreat: Treat disease."
      self.action_options['Treat'] = self.treat
    
    # Build Research Station
    if len(research_stations) < 6:
      if not self.city.research_station and self == operations_expert:
        print "\tBuild: Build reaserch station in current city (as operations expert)"
        self.action_options['Build'] = self.build_research_station      
      elif not self.city.research_station and self.city.name in self.hand and not being_dispatched:
        print "\tBuild: Build reaserch station in current city (discard current city)"
        self.action_options['Build'] = self.build_research_station
        
    # Discover Cure
    counts = {"blue": 0, "yellow": 0, "red": 0, "black": 0}
    for color in counts:
      for card in self.hand:
        if self.hand[card].default == color:
          counts[color] += 1
      if counts[color] >= self.needed_cards and self.city.research_station and not being_dispatched:
        print "\tCure: Discover cure for %s disease" % (color)
      self.action_options['Cure'] = self.discover_cure
      
    # Event Card
    for player in players:
      for card in player.hand:
        if player.hand[card].default == 'Event':
        	print "'Event': %s (%s)" % (card, player.first_name)
        	  
  ### PLAYER SPECIAL ACTIONS ###
  
    # Dispatcher
    if self.name == 'Dispatcher':
      print "\tDispatch: Move someone else's pawn as your own or move any pawn to another team member's current location."
      self.action_options['Dispatch'] = self.dispatcher
      
    # Being_Dispatched
    if being_dispatched:
      print "\tJoin Team Member: Move to another team member's city"
      self.action_options['Join Team Member'] = self.dispatched
    
    # Store Card for Contingency Planner
    if self == contingency_planner and len(self.cp_hand) < 1 and len(events_discard) > 0:
      print "\tStore: Store an event card from the discard pile (no more than one). "
      self.action_options ['Store'] = self.contingency_store
    
    if being_dispatched: 
      my_args = "True"
    else:
      my_args = None
      
    action_choice = self.get_answer(self.action_options, back = False, args = my_args)
    if action_choice != None:
      if self == medic and self.city.cube_count() > 0:
        for color in the_cubes:
          if the_cubes[color]['cured'] == True and self.city.disease[color]['cubes'] > 0:
            self.city.be_treated(color)
      action_choice(my_args)
      if self == medic and self.city.cube_count() > 0:
        for color in the_cubes:
          if the_cubes[color]['cured'] == True and self.city.disease[color]['cubes'] > 0:
            self.city.be_treated(color)
      
  def dispatcher(self, args = False):
    for each in the_team:
      print "\t%s is in %s" % (each, the_team[each].city.name)
    friend = self.get_answer(the_team, prompt = "Who would you like to move?")
    if friend != None:
      print "Please choose an action for", friend.name
      friend.new_action(True)      
  
  def dispatched(self):
    print "Move to any city with another player"
    for each in the_team:
      if each != self.name:
        print  "\t%s is in %s" % (each, the_team[each].city.name)
    friend = self.get_answer(the_team, prompt = "Who would you like to go see?", args = True)
    if friend != None:
      self.city = friend.city
      print "You have been moved to %s with the %s." % (self.city.name, friend.name)
  
  def contingency_store(self, args = False):
    if len(self.cp_hand) < 1:
      print "Available event cards:"
      for card in events_discard:
         print "\t", card
      if len(events_discard) == 0:
        print "There are no cards to store." 
        self.new_action()
      else:
        new_card = self.get_answer(events_discard, prompt = "Which card would you like to store?")
        if new_card != None:
          self.cp_hand[new_card.name] = events_discard.pop(new_card.name)
      
  def turn(self):
    print "\nCalling %s, the %s! How would you like to fight the pandemic?" % (self.first_name, self.name)
    for action_number in range(1,5):
      print "ACTION %s:" % (action_number)
      self.new_action()
      if enders['outbreaks'] > 8:
        print "You have had too many outbreaks. Game Over!"
        return "Game Over"
        break
      elif len(player_cards) == 0:
        return "Game Over"
        print "You have run out of time! Game Over!"
        break
      elif ( the_cubes['blue']['left'] == 0 
          or the_cubes['red']['left'] == 0  
          or the_cubes['yellow']['left'] == 0
          or the_cubes['black']['left'] == 0 ):
        return 
        print "The pandemic has gotten out of control! Game Over"
        break
      else: 
        continue

      
  def draw_cards(self, number): 
    print "\nHere are %s cards for you!" % (number)
    for x in range(0,number):
      new_card = player_cards.pop()
      if new_card == 'Epidemic':
        epidemic()
        # return 'epidemic'
      else: 
        self.add_to_hand(new_card)
        if new_card.default == 'event':
        	print "You now can play the %s card at any time. This card allows you to %s" % (new_card.name, event_powers[new_card.name])
    self.current_hand()
    print "\n"

  def play_event_card(self): 
    hero = self.get_answer(the_team, prompt = "Who would like to play their event card?")
    hero.current_hand('events')
    hero.events = {}
    for card in hero.hand:
      if hero.hand[card].default == 'event':
        hero.events[card] = hero.hand[card]
    for card in hero.cp_hand:
      if hero.cp_hand[card].default == 'event':
        hero.events[card] = hero.cp_hand[card]
    chosen_event = self.get_answer(hero.events, prompt = "\nWhat event would you like to play?", repeat = "play_event_card")
    if chosen_event != None:
      event_completion = chosen_event.action(self)
      if event_completion != None:
        hero.discard(chosen_event)
        print "Now back to the %s's action\n  " % (self.name)



events = {}
class Event(object):
  def __init__(self, name, special_event):
    self.name = name
    events[name] = self
    player_cards.append(self)
    self.default = 'event'
    self.action = special_event

def event_oqn(player):
  # One Quiet Night, skip the next infect cities step
  oqn['on'] = True
  return "Complete"

def event_airlift(player):
  # Move any pawn to any city.
  the_moved = player.get_answer(the_team, prompt = "Who would you like to move?")
  if the_moved != 0:
    print "%s is currently in %s. Where would you like to move your teammate?" % (the_moved.name, the_moved.city.name)
    moved_to = player.get_answer(cities)
    if moved_to != 0:
      print "You have moved the %s to %s" % (the_moved.name, moved_to.name)
      the_moved.city = moved_to
      return "Complete"
    else: 
      return None
  else:
    return None
  
def event_forecast(player):
  print "Here are the top six cards from the infection deck for you to rearrange:"
  rearrangement = []
  for x in range (1,7):
    rearrangement.append(infection_cards[len(infection_cards) - x])
    print rearrangement[x - 1].name,
    if x < 7:
      print ",",
  print "\nStarting with the last card and ending with the first (which would be the next draw),",
  print "what order would you prefer?"
  for x in range (1,7):
    card = player.get_answer(rearrangement, dict = False, repeat = player.new_action)
    if card != None:
      rearrangement.remove(card)
      infection_cards.remove(card)
      infection_cards.append(card)
      if x == 6:
        print "Well done! The top six cards have been rearranged to your liking. The next infected city will be %s." % (card.name)
      return "Complete"
    elif card == None:
      return None
      break
  
def event_resilient_population(player):
  for x in infection_discard:
    print x.name
  resilient = player.get_answer(infection_discard, dict = False, prompt =  "Which city would you like to make resilient?")
  if resilient != None:  
    infection_discard.pop(infection_discard.index(resilient))
    print "%s is now resilient against any new infections" % (resilient.name)
    return "Complete"
    
def event_government_grant(player):
  print "Add one research station to any city"
  print "Where would you like to build?"
  city = player.get_answer(cities)
  if city != None:
    city.add_research_station()
    print "You have built a research station in", city.name
    return "Complete"
  else: 
    return None
 
one_quiet_night = Event("One Quiet Night", event_oqn)
airlift = Event("Airlift", event_airlift)
forecast = Event("Forecast", event_forecast)
resilient_population = Event("Resilient Population", event_resilient_population)
government_grant = Event("Government Grant", event_government_grant)


def epidemic():
  print """
  ****************************
  ********* EPIDEMIC *********
  ****************************
  """
  new_infected_city = infection_cards.pop(0)
  infection_discard.append(new_infected_city)
  new_infected_city.infect(3)
  shuffle(infection_discard)
  shuffle(infection_discard)
  infection_cards.extend(infection_discard)
  del infection_discard[:]
  enders['epidemics'] += 1
  print "The infection rate is now %s cities per turn." % (infection_rate[enders['epidemics']])

def get_all_status():
  print "\n@@@@@@@@@  PANDEMIC STATUS  @@@@@@@@@@"
  print "Outbreaks left: %s" % (8 - enders['outbreaks'])
  print "Global infection levels:"
  print "\tBlue: %s" % (24 - the_cubes['blue']['left'])
  print "\tRed: %s" % (24 - the_cubes['red']['left'])
  print "\tBlack: %s" % (24 - the_cubes['black']['left'])
  print "\tYellow: %s" % (24 - the_cubes['yellow']['left'])
  print "Current infected cities:"
  for city in cities: 
    if cities[city].cube_count() != 0:
			cities[city].current_status()
  print "Current infection rate: %s" % (infection_rate[enders['epidemics']])
	
			
			
				

##########################################################
## PLAY TIME!
##########################################################

# Infect new cities 
def infect_cities():
  if not oqn['on']:
    for x in range(0,infection_rate[enders['epidemics']]):
      infected_city = infection_cards.pop()
      infection_discard.append(infected_city)
      infected_city.infect(1)
      next()
  else: 
    print "No infections tonight... things are quiet!"
    oqn['on'] = False


def play():
#  
  game_over = False
  while (game_over == False): 
    for PLAYER in players:
      play = PLAYER.turn()
      if play != 'Game Over':
        PLAYER.draw_cards(2)
        and_then = PLAYER.get_answer(['Yes'], prompt = "Continue? (type 'Yes' or 'Event')", back = "False", dict = False, strings = True)
        if and_then == "Yes":
          infect_cities()
        get_all_status()
      else:
        game_over = True
# Select roles, deal hands, and choose who goes first

researcher = Player("Researcher", "brown")
scientist = Player("Scientist", "white", needed_cards = 4)
medic = Player("Medic", "orange")
contingency_planner = Player("Contingency Planner", "blue")
quarantine_specialist = Player("Quarantine Specialist", "green")
dispatcher = Player("Dispatcher", "purple")
operations_expert = Player("Operations Expert", "lime")

shuffle(the_players)
shuffle(infection_cards)
shuffle(player_cards)

# Test Setup
'''
the_team = {"Operations Expert": operations_expert, "Scientist": scientist, "Medic": medic}
players = [operations_expert, scientist, medic]
turn_order = players
for place in [washington, new_york, chicago,  madrid, london,  airlift, resilient_population]:
  operations_expert.hand[place.name] = place
for place in [atlanta, algiers, cairo, jakarta, delhi, mumbai]:
  scientist.hand[place.name] = place
for place in [beijing, chennai, kinshasa, lima, government_grant, one_quiet_night]:
  medic.hand[place.name] = place
  
for x in beijing, chicago, atlanta, chennai:
  infected_city = infection_cards.pop(infection_cards.index(x))
  infection_discard.append(infected_city)
  infected_city.infect(3)
'''



def setup():
	# Instructions
  print "\nDo you have what it takes to save humanity? "
  print "You and your companions are highly skilled members of a disease-fighting team",
  print "waging a battle against four deadly diseases. "
  print "Your team will travel across the globe, stemming the tide of",
  print "infection and developing the resources you'll need to discover the cures."
  print "You must work together, using your individual strengths to destroy the diseases",
  print "before they overtake the world."
  print "The clock is ticking as outbreaks and epidemics accelerate the spread of the plague."
  print "Will you find the cures in time? The fate of humanity is in your hands!",
  next()
  
  print "\nYour primary goal is to find cures to the four disease: Black, Red, Yellow, and Blue",
  next()
  print "\nYou will do this by travelling the globe, collecting and swapping cards,"
  print "   and building research stations."
  print "A disease is cured when you submit five cards of the same color at a research station.",
  next()
  
  print "\nEach of you will start out with a few cards. ",
  print "City cards can be used to go places, build research stations, and cure diseases."
  print "Event cards can be played at any time."
  print "You will draw two cards at the end of each turn"
  print "You will not be allowed to have more than seven cards at a time. So save wisely!"
  next()
  
  print "\nEach member of your team will have four actions per turn",
  next()
  
  print "For each action, you will choose from the following options:"
  print "  Drive/Ferry to a connected city. (Example: Move from Atlanta to Washington)"
  print "\n  If you have city cards in your hand:"
  print "    Take a direct flight to a city by discarding that city card in your hand"
  print "\n  If you have the city card that matches your current city:"
  print "    Take a charter flight to any city by discarding the card that matches your current city"
  print "    Build a research station by discarding the city card that matches your current city."
  print "\n  If you are in a city with a research station:"
  print "    Take a shuttle flight from one research staion to another."
  print "\n  If you are in a city with a disease: "
  print "    Treat disease in your current city and downgrade the level by one. If the disease is cured, you can downgrade the disease level to zero in one action."
  print "\n  If you are in the same city as another player and one of you has your current city card:"
  print "    Share knowledge by either giving the card that matches your current city to another player or by taking the card that matches your current city from another player. (Get permission!)"
  print "\n  If you have five city cards of the same color:"
  print "    Discover a cure when you are at a research station by discarding five city cards of the same color."
  print "  Each player will also have a special skill to use." 
  print "  Don't worry too much, we'll show your options for each action!",
  next()
  
  print "\nWhile this may seem simple enough, a few forces are working against you."
  print "First of all, after every turn by a team member, more cities will be infected"
  print "Early in the game, it will be two cities per turn, ",
  print "but each epidemic will increase the infection rate.",
  next()
  print "\nWhen you draw two cards after your turn, there could be an epidemic."
  print "This means that a new city will be infected at disease level three." 
  print "This also means that all cities that have been infected since the last epidemic "
  print "will now be at the top of the list to randomly be selected for the next infections."
  next()
  print "\nBe careful because many of these cities will already be infected!"
  print "If a city is infected when it already has an infection level of three,"
  print "then there will be an outbreak."
  print "In an outbreak, all touching cities will beinfected with the disease, "
  print "increasing their infection level by one."
  next()
  print "\nIf you reach 8 outbreaks before all diseases are cured, your game will be over."
  print "If your team runs out of cards, your game will be over."
  print "If any one disease has spread too far, your game will be over"
  next()
  
  print "Your entire team will start in Atlanta. This is the location of the only research station until your team builds more. "
  print "Best of luck to you. The world needs you."
  print "(Also, I would highly suggest googling to find a pandemic map image to aid you.)"

  number = 0  
  while (number != 2 and number != 4 and number != 3):
    number = input("\nHow many players will be saving the world today (2-4)?")
  else:
    for i in range(0, number):
      assignment = the_players.pop()
      players.append(assignment)
      players[i].city = cities['Atlanta']
      players[i].first_name = raw_input('What is your name, Player %s? (type your name and press enter)' % (i + 1))
      print "\nOkay, %s. You will be the %s token, taking a role as %s" % (players[i].first_name, players[i].color, players[i].name)
      print "As %s, %s" % (players[i].name, players[i].role)
      number_of_initial_cards = {2: 4, 3: 3, 4: 2}
      the_team[assignment.name] = assignment
      players[i].draw_cards(number_of_initial_cards[number])
    players.sort(key = lambda player: player.max_pop)
    print "The order of play will be: "
    for player in players:
      print "\t%s" % (player.first_name)
    difficulty = raw_input("How difficult would you like your game to be? ('Introductory', 'Standard', 'Heroic')")
    while difficulty != 'Introductory' and difficulty != 'Heroic' and difficulty != 'Standard':
      print "Please give a valid response"
      difficulty = raw_input("How difficult would you like your game to be? ('Introductory', 'Standard', 'Heroic')")
    else:
      epidemic_cards = levels[difficulty]
      section = len(player_cards)/epidemic_cards
      for x in range(epidemic_cards, 0, -1):
        player_cards.insert(randint((x - 1) * section, x * section), 'Epidemic')
      print "\nYou will experience %s epidemics. Prepare yourselves.\n" % (epidemic_cards) 
  
  cities['Atlanta'].add_research_station()
  player_cards.append('Epidemic')
  cities['Atlanta'].disease['yellow']['cubes'] = 1
  cities['Atlanta'].disease['red']['cubes'] = 1
  for x in range(0,9):
    infected_city = infection_cards.pop(x)
    infection_discard.append(infected_city)
    intensity = [3,3,3,2,2,2,1,1,1]
    infected_city.infect(intensity[x], setup = True)
                   
setup()
play()

