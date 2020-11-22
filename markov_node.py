import random
from string import ascii_letters, digits

class MarkovNode:

	valid_text = ascii_letters + digits + "'’%"
	valid_symbols = "?!.,-"
	valid_everything = valid_text + valid_symbols + ' '
	_node_map = {}

	def __new__(cls, word):
		if word not in MarkovNode._node_map:
			tmp = super(MarkovNode, cls).__new__(cls)
			MarkovNode._node_map[word] = tmp
			return tmp
		else:
			return MarkovNode._node_map[word]

	def __init__(self, word):
		try:
			self.next
		except AttributeError:
			self.word = word
			self.next = {}

	def get_sentence(self, limit = 50):
		word_arr = []
		curr_node = self._pick_next()
		while curr_node.word != "" and limit > 0:
			if len(word_arr) != 0 and not (word_arr[-1][0] in self.valid_text and curr_node.word[0] in self.valid_symbols):
				word_arr.append(" ")
			word_arr.append(curr_node.word)
			curr_node = curr_node._pick_next()
			limit -= 1

		return "".join(word_arr)

	def add_word_array(self, word_arr):
		curr_node = self
		for word in word_arr:
			assert(word != "" and word != " ")
			curr_node = curr_node._add_word(word)
		curr_node._add_word("")

	def _add_word(self, word):
		if word not in self.next:
			self.next[word] = 1
		else:
			self.next[word] += 1
		return MarkovNode(word)

	def _pick_next(self):
		if len(self.next) == 0:
			self._add_word("")

		assert(len(self.next) != 0)
		tmp = 0
		for word in self.next:
			tmp += self.next[word]
		rand_num = random.randrange(0, tmp)
		for word in self.next:
			rand_num -= self.next[word]
			if rand_num <= 0:
				return MarkovNode(word)

		assert(false)
	
	def __str__(self):
		return str(self.next)

	@staticmethod
	def get_root():
		return MarkovNode(" ")

	@staticmethod
	def debug_print():
		pass

