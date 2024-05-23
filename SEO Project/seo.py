import requests
from bs4 import BeautifulSoup
from collections import Counter
from tkinter import *
import re
from xlsxwriter import *
import matplotlib.pyplot as plt
import numpy as np

ROOT = Tk()
ROOT.title("Search Engine Optimization Tool")

# URL AND ITS VALIDITY
def isValidURL(str):
    regex = (
        "((http|https)://)(www.)?"
        + "[a-zA-Z0-9@:%._\\+~#?&//=]"
        + "{2,256}\\.[a-z]"
        + "{2,6}\\b([-a-zA-Z0-9@:%"
        + "._\\+~#?&//=]*)"
    )
    p = re.compile(regex)
    if str == None:
        return False
    if re.search(p, str):
        return True
    else:
        return False

url_Input = Entry(ROOT, width=200)
url_Input.pack()
url_Input.insert(0, "Enter the URL here.")
def url_Validity():
	if(not isValidURL(url_Input.get())):
		url_Input.delete(first=0, last=END)
		url_Input.insert(0, "The entered URL is not valid. Please recheck and enter a correct one.")
	else:
		my_URL = url_Input.get()
		url_Input.delete(first=0, last=END)
		url_Input.insert(0, "Entered URL is valid. You may proceed. No need to again click the 'Proceed with this URL' button.")
		start(my_URL)

url_Button = Button(ROOT, text="Proceed with this URL", command=url_Validity)
url_Button.pack()

# REMOVING UNWANTED WORDS AND SYMBOLS AND GETTING THE 5 TOP FREQUENT WORDS AND THE FREQUENCY OF THE WORDS THE USER IS SEARCHING FOR
def start(url):
	# IGNORE WORDS
	ignore_Words = Entry(ROOT, width=150) 
	ignore_Words.pack()
	ignore_Words.insert(0, "Enter all the words you want to ignore from the webpage, separated by spaces. Then click on 'Ignore these words' button.")
	ignore_Them = []
	def get_Ignores():
		list_Of_Ignore_Words = list(ignore_Words.get().split(" "))
		for w in list_Of_Ignore_Words:
			ignore_Them.append(w)
		ignore_Words.delete(first=0, last=END)
		ignore_Words.insert(0, "They have been stored. You may proceed.")
		wordlist = []
		source_code = requests.get(url).text
		source_code = source_code.replace("\n", " ")
		soup = BeautifulSoup(source_code, 'html.parser')
		for each_text in soup.findAll(['div', 'p', 'h1', 'h2', 'h3', 'span', 'body', 'footer', 'ul', 'li']):
			content = each_text.text.strip()
			words = content.lower().split(" ")
			for each_word in words:
				wordlist.append(each_word)
		clean_wordlist(wordlist, ignore_Them)
	
	# IGNORE BUTTON
	ignore_Button = Button(ROOT, text="Ignore these words", command=get_Ignores)
	ignore_Button.pack()

def clean_wordlist(wordlist, ignore_Them):
	clean_list = []
	for word in wordlist:
		symbols = "!@#$%^&*()_-+={[}]|\;:\"<>?/., "
		for i in range(len(symbols)):
			word = word.replace(symbols[i], '')
		if len(word) > 0:
			clean_list.append(word)
			for w in ignore_Them:
				if(w == word):
					clean_list.pop()
					break
	create_dictionary(clean_list)

def create_dictionary(clean_list):
	# PREFERENCE WORDS
	prefer_Words = Entry(ROOT, width=150)
	prefer_Words.pack()
	prefer_Words.insert(0, "Enter all the words of your preference separated by spaces. Then click on the 'Prefer these words' button.")
	preferred_Words = []
	prefer_Words_X_Axis = []
	prefer_Words_Y_Axis = []
	top_Five_X_Axis = []
	top_Five_Y_Axis = []
	def get_Preferred():
		list_Of_Preferred_Words = list(prefer_Words.get().split(" "))
		for w in list_Of_Preferred_Words:
			preferred_Words.append(w)
		# WILL DELETE NOW
		prefer_Words.delete(first=0, last=END)
		prefer_Words.insert(0, "The words have been stored. You may proceed. Press on the 'Quit' button now.")
		word_count = {}
		for word in clean_list:
			if word in word_count:
				word_count[word] += 1
			else:
				word_count[word] = 1
		c = Counter(word_count)
		wb = Workbook('SEO.xlsx')
		ws = wb.add_worksheet()
		row = 0
		column = 0
		ws.write(row, column, "Preferred")
		ws.write(row, column + 1, "Frequency")
		ws.write(row, column + 2, "Density")
		row = row + 1
		total_Words = 0
		for value in word_count.values():
			total_Words += value
		for w in preferred_Words:
			ws.write(row, column, w)
			prefer_Words_X_Axis.append(w)
			try:
				ws.write(row, column + 1, word_count[w])
				ws.write(row, column + 2, (word_count[w]/total_Words))
				prefer_Words_Y_Axis.append(word_count[w])
			except KeyError:
				ws.write(row, column + 1, 0)
				ws.write(row, column + 2, 0)
				prefer_Words_Y_Axis.append(0)
			row += 1
		row += 1
		ws.write(row, column, "Rank")
		ws.write(row, column + 1, "Word")
		ws.write(row, column + 2, "Frequency")
		ws.write(row, column + 3, "Density")
		top_Five = c.most_common(5)
		rank = 1
		row += 1
		for tup in top_Five:
			ws.write(row, column, rank)
			ws.write(row, column + 1, tup[0])
			ws.write(row, column + 2, tup[1])
			ws.write(row, column + 3, (tup[1]/total_Words))
			top_Five_X_Axis.append(tup[0])
			top_Five_Y_Axis.append(tup[1])
			row += 1
			rank += 1
		wb.close()
		x = np.array(prefer_Words_X_Axis)
		y = np.array(prefer_Words_Y_Axis)
		plt.figure(1)
		plt.title('Preferred Words')
		plt.bar(x, y)
		plt.savefig('Preferred_Words_Bar_Graph')
		x = np.array(top_Five_X_Axis)
		y = np.array(top_Five_Y_Axis)
		plt.figure(2)
		plt.title('Top 5 Words')
		plt.bar(x, y)
		plt.savefig('Top_5_Words_Bar_Graph')
		plt.show()

	# PREFERENCE WORDS BUTTON
	prefer_Button = Button(ROOT, text="Prefer these words", command=get_Preferred)
	prefer_Button.pack()

	# QUIT BUTTON
	quit_Button = Button(ROOT, text="Quit", command=ROOT.quit)
	quit_Button.pack()

ROOT.mainloop()
