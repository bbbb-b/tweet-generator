#!/usr/bin/python3
import twitter
import json
import validators
import traceback
import time
import sys
from markov_node import MarkovNode

def init_args():
	global config_file, account_name, tweet_interval
	if len(sys.argv) != 4:
		sys.exit(f"{sys.argv[0]} <account-name> <config-file> <tweet-interval>")
	account_name = sys.argv[1]
	config_file = sys.argv[2]
	try:
		tweet_interval = float(sys.argv[3])
	except ValueError:
		sys.exit(f"'{sys.argv[3]}' cannot be parsed as a float")

def connect():
	try:
		config = json.load(open(config_file))
	except:
		sys.exit(f"Cannot parse config file ${config_file}")
	try:
		api = twitter.Api(**config)
		api.GetFriends()
		return api
	except:
		sys.exit(f"Invalid credentials")

def filter_text(tweet_text): # array of arrays of valid
	valid_text = MarkovNode.valid_text
	valid_symbols = MarkovNode.valid_symbols
	valid_everything = MarkovNode.valid_everything

	tweet_text = "".join(filter(lambda x : x not in "…*()\"", tweet_text))
	tweet_text = " ".join(map(lambda x : x if (not validators.url(x) and len(x) != 0 and x[0] != '@') else "",
		tweet_text.split(" ")))
	
	if not all([i in valid_everything for i in tweet_text]):
		return None

	CHAR_ANY = 0
	CHAR_TEXT = 1
	CHAR_SYMBOL = 2

	char_state = CHAR_ANY

	last_word = []
	answer_words = []
	for ch in tweet_text:
		if ch == ' ':
			if len(last_word) != 0:
				answer_words.append("".join(last_word))
				del last_word[:]
			char_state = CHAR_ANY
			continue
		if ch in valid_text:
			if char_state == CHAR_SYMBOL:
				answer_words.append("".join(last_word))
				del last_word[:]
			last_word.append(ch)
			char_state = CHAR_TEXT
			continue
		if ch in valid_symbols:
			if char_state == CHAR_TEXT:
				answer_words.append("".join(last_word))
				del last_word[:]
			last_word.append(ch)
			char_state = CHAR_SYMBOL
			continue
		assert(False)
	if len(last_word) != 0:
		answer_words.append("".join(last_word))
	if len(answer_words) == 0:
		return None
	#answer_text = list(filter(lambda x : x != [], answer_text))
	#answer_text = list(map(lambda x : "".join(x), answer_text)) # delete this
	return answer_words



def get_tweets(real_count, screen_name):
	global api
	tweets = []
	last_id = None
	while real_count > 0:
		new_tweets = api.GetUserTimeline(screen_name = screen_name, count = real_count, include_rts = False, max_id = last_id)
		if len(new_tweets) == 0:
			break
		last_id = new_tweets[-1].id - 1
		sys.stderr.write(f"last_id = {last_id}\n")
		tweets += new_tweets
		real_count -= len(new_tweets)
	return tweets

def main():
	init_args()
	global api
	api = connect()
	sys.stderr.write("Getting tweets...\n")
	tweets = get_tweets(20000, account_name)
	sys.stderr.write("Processing tweets...\n")
	for tweet in tweets:
		tmp = filter_text(tweet.text)
		if tmp != None:
			MarkovNode.get_root().add_word_array(tmp)
		else:
			sys.stderr.write("FAILED TO USE TWEET:\n")
			sys.stderr.write(f"{tweet.text}\n")
			sys.stderr.write("=" * 30 + "\n")
	sys.stderr.write(f"Starting with {len(tweets)} tweets processed.\n")
	while True:
		text = MarkovNode.get_root().get_sentence()
		if text == "":
			continue
		try:
			api.PostUpdate(text)
			sys.stderr.write(f"New tweet:\n{text}\n")
		except twitter.error.TwitterError:
			sys.stderr.write(f"Failed to tweet:\n{text}\n")
			sys.stderr.write(traceback.format_exc() + "\n")
			time.sleep(2.0)
			continue
		time.sleep(max(tweet_interval, 2.0))
	return 0



if __name__ == "__main__":
	main()
