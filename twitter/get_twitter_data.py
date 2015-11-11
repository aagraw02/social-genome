#Author: Ashish Agrawal 
#Collects: tweet ID,timestamp of tweet, tweet,  retweet users, retweet timestamp


import tweepy
import csv
from requests.exceptions import ConnectionError, ReadTimeout, SSLError
from requests.packages.urllib3.exceptions import ReadTimeoutError, ProtocolError
from requests_oauthlib import OAuth1
import json
import requests
import socket
import ssl
import sys,argparse

#Twitter API credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
#wait if you get throtelled
api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)



def get_tweets(screen_name):
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	#Get the first 200 tweets
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	alltweets.extend(new_tweets)
	
	#use the oldest tweet Id in the above list to get next 200 tweets
	oldest = alltweets[-1].id - 1
	
	#Loop through to keep grabbing old tweets
	while len(new_tweets) > 0:
		#get next 200 tweets
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

	
	# Collect people who retweeted the tweet. The try except is to catch the time out exception. 
	outtweets = []
	for tweet in alltweets:
		try:
			rtids = []
			rttime = []
			for rt in api.retweets(tweet.id):
				rtids.append(rt.user.screen_name)
				rttime.append(str(rt.created_at))
			retweerts = '/'.join(rtids)
			retweettime = '/'.join(rttime)
			outtweets.append([tweet.id_str,tweet.created_at,tweet.text.encode("utf-8"),retweerts,retweettime,tweet.coordinates])
		except (ConnectionError, ProtocolError, ReadTimeout, ReadTimeoutError, SSLError, ssl.SSLError, socket.error) as e:
        	       	contiinue

	#write the csv	
	with open('%s_tweets.csv' % screen_name, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(["id","created_at","text","retweets","retweet_time"])
		writer.writerows(outtweets)
	
	pass



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('twitter_handle',action='store', help="Enter twitter handle with the '@' character as the only input param",type=str)
    inputs = parser.parse_args()
    user_name = inputs.twitter_handle
    get_tweets(user_name)


if __name__ == '__main__':
	main()
