from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

client = MongoClient()
db = client.test
#db.tweets.remove()
tweets = db.tweets


access_token = "777222101556076544-Bji7W4PDJUetIYQUMvAwAfDse2n8STq"
access_token_secret = "gxJNRMTF4xFuwt95uzw4g2bEQFs19tyJmsepdLjSCo1C3"
consumer_key ="5x5j9zymoR9AMLbWSocviZ32J"
consumer_secret = "HPPrlY2pLFxJjJ5zbxbjP9leH1fhyxE312Wa4NO80XZQX8gJ73"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


@app.route('/',methods=['GET'])
def hello():
	return jsonify({'hello':'world'})

@app.route('/triggertweets',methods=['POST'])
def triggertweets():
	key = request.json['keyword']
	max_tweets = request.json.get('max_tweets','20')
	#print(key)
	l = StdOutListener(key,max_tweets)
	stream = Stream(auth, l)
	stream.filter(track=[key], async=True)
	return jsonify({"trigger":"started"})

@app.route('/gettweets', methods=['POST'])
def getTweets():
	key = request.json['keyword']
	s = []
	for tweet in tweets.find({"keyword":key}):
		s.append(tweet['text'])
	return jsonify(s)

class StdOutListener(StreamListener):
	
	count = 0
	keyword = ""
	max_tweets = 0

	def __init__(self,key, max_tweets):
		self.max_tweets = max_tweets
		self.count = 0
		self.keyword += key

	def on_data(self,data):
		obj = json.loads(data)
		obj['keyword'] = self.keyword
		tweets.insert_one(obj)
		print("Success")
		self.count += 1
		if self.count == self.max_tweets:
			del self
			return False
		return True

	def on_error(self,status):
		print("Failed - Error: ",status)



if __name__ == '__main__':
	app.run(port=5000,use_reloader=True)