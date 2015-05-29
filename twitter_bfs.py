from datetime import datetime
import sys
import cStringIO
import lxml.etree
from lxml.html import fromstring,tostring
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

#  We use a breadth first search to collect all of the usernames (handles in the Twitter world)
#  within a specified degree of separation of the starting point of the search.
class twitter_bfs:
	def __init__(self,username,password,relationship,browser):
		self.username = username
		self.password = password
		self.relationship = '/' + relationship
		self.browser = browser
		self.log_in()
		time.sleep(2)

# 	do a breadth first search from the starting point until the (depth + 1) of a user 
# 	is equal to the desired depth
# 	bfs(starting point, desired depth, file to print handles)
	def bfs(self, start, depth, print_file):
# 		list of tuples (depth where this user was found, the user's twitter handle)
		queue = []
# 		dictionary where the key is the user's twitter handle and the value is the list
# 		of the people who follow the user or people that the user follows
		network = {}
# 		list to keep track of people who have already been searched
		visited = []
#	 	keep track of how deep we are in the search
		current_depth = 0
# 		get followers/following for starting point
		network[start] = self.get_handles(start)
		queue.append((current_depth,start))
		while len(queue) > 0:
			current = queue.pop(0)
			current_depth = current[0]
# 			reached desired depth
			if current_depth == depth:
				break
# 			add all handles in the user's list to the bfs queue that are not 
# 			in the visited list
			for handle in network[current[1]]:
				if handle not in visited:
					visited.append(handle)
#	 				increase current_depth since these are all one degree of sep from 'current'
					queue.append((current_depth+1,handle))
					network[handle] = self.get_handles(handle)
# 					the defaut setting is that we print one user at a time,
# 					but we could wait until the end to print, too.
					self.incremental_print(print_file,network[handle])
		return network

#	go to user's twitter page then scroll to the bottom of the page
# 	return a list of users		
	def get_handles(self,handle):
# 	twitter goes to the wrong page if we try "https://www.twitter.com/my_handle/relationship"
		if handle == ('/' + self.username):
			handle = ''
		self.browser.get('https://twitter.com' + handle + self.relationship)
		time.sleep(1)
		self.scroll()
		time.sleep(1)
		return self.iterparse_html()	

# 	use lxml to extract the usernames
	def iterparse_html(self):
		list = []
# 		lxml needs a file-like object
		src = cStringIO.StringIO(self.browser.page_source.encode('ascii','ignore'))
		context = lxml.etree.iterparse(src,html=True,tag ='a')
		for (event,element) in context:
			if str(element.get('class')) == 'ProfileNameTruncated-link u-textInheritColor js-nav js-action-profile-name':
				list.append(element.get('href'))
			element.clear()
			while element.getprevious() != None:
				del element.getparent()[0]
		del src
		del context
		return list

#   execute java script to scroll to the bottom of page until there aren't anymore new 
# 	elements
	def scroll(self):
		while True:
# 		execute java script
			elemsCount = self.browser.execute_script("return document.querySelectorAll('.GridTimeline-items > .Grid').length")
			self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# 			wait for elements to load
			try:
				WebDriverWait(self.browser,2).until(
					lambda x: x.find_element_by_xpath(
						"//*[contains(@class,'GridTimeline-items')]/*[contains(@class,'Grid')]["+str(elemsCount+1)+"]"))
			except:
# 			wait one more time to make sure there are not any more elements loading
				try :
					WebDriverWait(self.browser,3).until(
						lambda x: x.find_element_by_xpath(
							"//*[contains(@class,'GridTimeline-items')]/*[contains(@class,'Grid')]["+str(elemsCount+1)+"]"))
				except:
					break

# 	login to twitter profile	
	def log_in(self):
		self.browser.get("https://twitter.com/")
		time.sleep(3)
		username = self.browser.find_element_by_xpath("//input[@class='text-input email-input']") 
		username.send_keys(self.username)
		time.sleep(2)
		password = self.browser.find_element_by_xpath("//input[@class='text-input']")
		password.send_keys(self.password)
		password.send_keys(Keys.RETURN)
		
# 	print entire dictionary
	def print_all(self,f,dict):
		for key in dict.keys():
			i = 0
			l = len(dict[key])
			for follower in dict[key]:
				if i == l - 1:
					f.write(follower.encode("ascii","ignore")+ '\n')
					continue
				f.write(follower.encode("ascii","ignore") + ',')
				i += 1

# 	print one user at a time
	def incremental_print(self,f,followers):
		i = 0
		l = len(followers)
		for follower in followers:
			if i == l - 1:
				f.write(follower.encode("ascii","ignore")+ '\n')
				continue
			f.write(follower.encode("ascii","ignore") + ',')
			i += 1

def main():
	browser = webdriver.Firefox()
	username = 'your username'
	password = 'your password'
# 	either 'following' or 'followers'
	relationship = 'following'
	t = twitter_bfs(username,password,relationship,browser)
	file_path = 'file path'
	f = open(file_path,'w')
# 	degrees of separation
	depth = 2
	network = t.bfs('/' + username, depth, f)

if __name__ == '__main__':
	main()
	
