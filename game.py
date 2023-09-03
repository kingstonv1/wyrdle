from random import choice


class Game:
	def __init__(self):
		# Extract our list of wordle words into a set from the text file
		# (credit to https://raw.githubusercontent.com/charlesreid1/five-letter-words/master/sgb-words.txt)
		# not the ACTUAL wordle wordlist, but I don't want to curate the solutions (like nyt does)
		# and lots of those words are weird!
		with open("./wordle_words.txt", "r") as wordlist:
			self.words = wordlist.read().split()
		
		self.solution = None
		self.grid = None
		self.current_row = 0
		
		self.start_new_game()
		
	def start_new_game(self):
		self.solution = choice(self.words)
		self.grid = [["" for _ in range(5)] for _ in range(6)]
		self.current_row = 0
	
	def enter_letter(self, letter: str):
		for i, space in enumerate(self.grid[self.current_row]):
			if space == "":
				self.grid[self.current_row][i] = letter
				return
			
	def remove_letter(self):
		for i, space in reversed(list(enumerate(self.grid[self.current_row]))):
			if space != "":
				self.grid[self.current_row][i] = ""
				return
		
	def submit_word(self):
		word = "".join(self.grid[self.current_row]).lower()
		colors = [""] * 5
		
		# [] is used as a falsy value instead of returning False, because we return our colors if the word is valid.
		if len(word) != 5:
			return []
		
		if word not in self.words:
			return []
		
		# A dict with each letter in the word and how many times it occurs.
		solution_occurrences = {letter: self.solution.count(letter) for letter in set(self.solution)}
		correct = [False for _ in range(5)]
		
		# Correctly placed letters need to be passed over first so that letters aren't marked as yellow and then
		# green later on.
		for i in range(5):
			user_letter = word[i]
			solution_letter = self.solution[i]
			
			# Right Place, Right Letter
			if user_letter == solution_letter:
				correct[i] = True
				
		for i in range(5):
			user_letter = word[i]
			
			if correct[i]:
				colors[i] = "green"
				solution_occurrences[user_letter] -= 1
				
			elif user_letter in self.solution:
				if solution_occurrences[user_letter] > 0:
					colors[i] = "yellow"
					solution_occurrences[user_letter] -= 1
				
				else:
					colors[i] = "grey"
			
			else:
				colors[i] = "grey"
		
		return colors