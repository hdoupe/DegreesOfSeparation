import cStringIO
import lxml.etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

browser = webdriver.Firefox()
f = open(file path goes here,'w')

def error(handle):
	try:
		browser.get('https://twitter.com/' + handle)
		time.sleep(3)
		followers = browser.find_element_by_xpath("//a[@href='" + handle + "/followers']")
		followers.click()
		time.sleep(2)
	except (NoSuchElementException):
		time.sleep(10)
		error(handle)		
		
def print_all(dict):
	for key in dict.keys():
		i = 0
		l = len(dict[key])
		for follower in dict[key]:
			if i == l - 1:
				f.write(follower.encode("ascii","ignore")+ '\n')
				continue
			f.write(follower.encode("ascii","ignore") + ',')
			i += 1

def incremental_print(followers):
	i = 0
	l = len(followers)
	for follower in followers:
		if i == l - 1:
			f.write(follower.encode("ascii","ignore")+ '\n')
			continue
		f.write(follower.encode("ascii","ignore") + ',')
		i += 1

def get_handles_from_source(followers):
	list = []
	for follower in followers:
		list.append(str(follower.a['href']))
	return list
	
def iterparse_html():
	list = []
	src = cStringIO.StringIO(browser.page_source.encode('ascii','ignore'))
	context = lxml.etree.iterparse(src,html=True,tag ='a')
	for element in context:
		if str(element[1].get('class')) == 'ProfileNameTruncated-link u-textInheritColor js-nav js-action-profile-name':
			list.append(element[1].get('href'))
		element = None
	return list

def scroll():
	while True:
		elemsCount = browser.execute_script("return document.querySelectorAll('.GridTimeline-items > .Grid').length")
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		try:
			WebDriverWait(browser, 20).until(
				lambda x: x.find_element_by_xpath(
					"//*[contains(@class,'GridTimeline-items')]/*[contains(@class,'Grid')]["+str(elemsCount+1)+"]"))
		except:
			break
	
def log_in():
	browser.get("https://twitter.com/")
	time.sleep(3)
	username = browser.find_element_by_xpath("//input[@class='text-input email-input']") 
 	username.send_keys("USERNAME")
	time.sleep(2)
	password = browser.find_element_by_xpath("//input[@class='text-input']")
	password.send_keys("PASSWORD")
 	password.send_keys(Keys.RETURN)

def get_followers(handle):
	browser.get('https://twitter.com/' + handle)
	try:
		followers = browser.find_element_by_xpath("//a[@href='" + handle + "/followers']")
		followers.click()
		time.sleep(2)
	except (NoSuchElementException):
		error(handle)
	scroll()
	return iterparse_html()

	
def get_second_degree(followers):
 	first = {}
	handle = ""
	me = True
	i = 0
 	for follower in followers:
 		i += 1
 		if me == True:
 			me = False
 			continue
 		first[follower] = get_followers(follower)
 		incremental_print(first[follower])
 		time.sleep(2)	
 	return first
	
def main():
	log_in()
	time.sleep(5)
	list = get_followers('')
	second = get_second_degree(list)

if __name__ == '__main__':
	main()
