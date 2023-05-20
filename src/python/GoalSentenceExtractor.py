# coding: utf-8

import sys
import os
import copy
import pdb
import stanza
from stanza.models.common.doc import Sentence
import random
import re

from GTree import GTree, NB
s = {NB: 'Normal Behavior'}


#文章解析用
nlp = stanza.Pipeline(lang='en', processors= 'tokenize,pos,lemma,depparse,constituency')


class GoalSentenceExtractor:
	logs = []
	sentences = []
	goal_sentences = []
	noun_dict = dict()

	how_to_judge_goals =(
		'self.is_after_epoch'
	)
	how_to_judge_epoch =(
		'epoch_word is not None and 10 <= np_importance'
	)
	how_to_judge_anti_epoch =(
		'anti_epoch_word is not None and 10 <= np_importance'
	)

	def __init__(self, format='png', logfile=None, blur=None):
		self.goalmodel = GTree(format)
		self.__effect = blur
		self.__log = logfile


	def analyzeSpecification(self, text):
		self.sentences = []
		self.goal_sentences = []
		self.noun_dict = dict()

		lines = text.splitlines()		
		for line in lines:
			if line == '':
				self.sentences.append(None)
				continue

			sentence = nlp(line).sentences[0]
			self.sentences.append(sentence)
			self.resisterNounAppearance(sentence)

		print()
		print()

		passed_epoch = False
		for sentence in self.sentences:
			if sentence is None:
				passed_epoch = False
				print('\nsentence is None\n')
				self.goal_sentences.append(None)
				continue

			max_importance = 0
			tree = sentence.constituency
			npList = self.searchNPRecursively(tree)

			for np in npList:
				epoch_found, anti_epoch_found, np_importance = self.checkNP(np)
				print(f'epoch_found= {epoch_found}')
				passed_epoch = (passed_epoch or epoch_found) and not anti_epoch_found
				print(f'passed_epoch = {passed_epoch}')
				max_importance = max(max_importance, np_importance)

			if passed_epoch:
				self.goal_sentences.append(sentence)

			if_VP_exists = self.ifVPExistsIn(tree)
			passed_epoch = passed_epoch and if_VP_exists
			print('VP Existance: ' + str(if_VP_exists) + '\n')
				
		return self.goal_sentences
	
	def searchNPRecursively(self, tree):
		npList = []

		for	child in tree.children:
			if type(child) is str :
				continue

			if child.label == 'NP':
				leaves = child.leaf_labels()
				npList.append(' '.join(leaves))
			else:
				npList.extend(self.searchNPRecursively(child))
		
		return npList

	def checkNP(self, np):
		epoch_word = self.checkEpochWords(np)
		anti_epoch_word = self.checkAntiEpochWords(np)
		np_importance = self.NPNounImportance(np)
		print('[' + str(np) + '] ' + str(epoch_word) + ', ' + str(anti_epoch_word) + ', ' + str(np_importance))
		#str() は epoch_wordがNoneのときに効果を持つ

		return [eval(self.how_to_judge_epoch), eval(self.how_to_judge_anti_epoch), np_importance]

	def checkEpochWords(self, sentence):
		sentence_casefold = sentence.casefold()
		keywords = [
			'new ',
			'upcoming ',
			'envisioned ',
			' to be designed',
			' to be made'
		]
		
		for keyword in keywords:
			if keyword in sentence_casefold:
				return keyword

		return None
	
	def checkAntiEpochWords(self, sentence):
		sentence_casefold = sentence.casefold()
		keywords = [
			'current ',
			'existing '
		]
		
		for keyword in keywords:
			if keyword in sentence_casefold:
				return keyword

		return None

	def resisterNounAppearance(self, sentence):
		for word in sentence.words:
			if(word.upos=='NOUN' or word.upos=='PROPN'):
				if(word.lemma not in self.noun_dict):
					self.noun_dict[word.lemma] = 0
				self.noun_dict[word.lemma] += 1

	def NPNounImportance(self, np):
		sentence = nlp(np).sentences[0]
		np_importance = 0

		for word in sentence.words:
			if(word.upos=='NOUN' or word.upos=='PROPN'):
				noun_importance = self.getNounImportance(word.lemma)
				np_importance = max(np_importance, noun_importance)
		
		return np_importance

	def getNounImportance(self, noun):
		default_nouns = ['system', 'software']
		
		if noun not in self.noun_dict and noun not in default_nouns:
			return 0

		noun_importance = self.noun_dict[noun]
		if noun in default_nouns and noun_importance < 15:
			noun_importance = 15

		return noun_importance

	def ifVPExistsIn(self, tree):
		if_VP_exists = False

		for	child in tree.children:
			if type(child) is str :
				continue

			if child.label == 'VP':
				if_VP_exists = True
				break
			
			if_VP_exists = self.ifVPExistsIn(child)
			if if_VP_exists:
				break
		
		return if_VP_exists

	def printLog(self, log):
		print(log)
		self.logs.append(log)


	def writeLog(self):
		with open(self.__log, 'a') as f:
			logs = ''

			for log in self.logs:
				logs += log + '\n'
			f.write(logs)

	def readSpecification(self, openfilename):
		openfile = "../input/" + openfilename + ".txt"

		with open(openfile, "r", encoding="utf-8") as f:
			text = f.read()
			#textには空行が含まれていないのがよい
		
		#print(text)
		doc = nlp(text)
		return doc

from datetime import datetime
import time

if __name__ == "__main__":
	args = sys.argv
	openfilename = args[1]

	ltime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
	logFile = "../Log/log_{}-{}.csv".format(ltime, openfilename)
	
	stanza.download("en")

	extractor = GoalSentenceExtractor(format="png", logfile=logFile)

	text = extractor.readSpecification(openfilename)
	extractor.analyzeSpecification(text)