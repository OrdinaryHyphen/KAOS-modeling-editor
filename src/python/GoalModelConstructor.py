# coding: utf-8

from reprlib import recursive_repr
import sys
import os
import copy
import pdb
import stanza
import random
import re
from GoalSentenceExtractor import GoalSentenceExtractor
from GTree import GTree, NB
s = {NB: 'Normal Behavior'}



#要求記述解析を行うクラスの本体。
class GoalModelConstructor:
	def __init__(self, format='png', logfile=None, blur=None):
		self.goalmodel = GTree(format)
		self.__effect = blur
		self.__log = logfile

		#ログのリスト。ここにログを保存し、writeLog()の処理で外部ファイルに出力する。
		self.logs = []

		self.words = None #今読み込んでいる文章の解析結果。

		#ゴールのリスト。ここにゴールと、それに含まれている単語を記録する。
		self.goals = dict()

		#今扱っている文章に含まれるゴールのリスト。ここにゴールと、それに含まれている単語を一時的に記録する。
		self.tmp_goals = dict()

		self.goal_node = None #今扱っているゴールモデルの頂点。
		
		#あるゴールに含まれる名詞のリスト。
		self.np_lemmas_dict = {'Root': set()}

	def analyzeSpecification(self, text):
		self.goalmodel.formatGraph()

		extractor = GoalSentenceExtractor()
		goal_sentences = extractor.analyzeSpecification(text)

		for sentence in goal_sentences:
			if sentence is None :
				self.goalmodel.resetHistory()
				continue

			self.goal_node = NB('')
			self.constructGoalModel(sentence)


		self.goalmodel.formatGraph()
		return self.goalmodel.render()

	def readSpecification(self, openfilename):
		openfile = openfilename + '.txt'

		with open(openfile, 'r', encoding='utf-8') as f:
			text = f.read()

		return text

	def constructGoalModel(self, sentence):
		print('\n' + sentence.text)

		self.extractWordsFrom(sentence)
		self.findGoalsByDependency()

		self.goals.update(self.tmp_goals)
		self.tmp_goals.clear()

	def extractWordsFrom(self, sentence):
		root = {'id': 0, 'text': '(root)', 'upos': '', 'xpos': '',  'feats': '', 'head': 0, 'deprel': ''}  

		self.words = sentence.to_dict()
		self.words = [root] + self.words

		#元の文章に具体化のフレーズが含まれていれば、それを示すマーカーを入れる
		if self.isIncludesEmbodyingPhrase(sentence):
			print('>>>>>>>>include embodyment')
			embodying = {'id': len(self.words), 'text': '(embodying)', 'upos': '', 'xpos': '',  'feats': '', 'head': 0, 'deprel': ''}
			self.words = self.words + [embodying]

	#for exampleやin particularなど、前の文章を具体化するようなフレーズを正規表現で除去する
	def isIncludesEmbodyingPhrase(self, sentence):
		embodyingPhrase = re.compile(r'^(especially|specifically|in particular|for example|for instance)', re.IGNORECASE)
		print(re.search(embodyingPhrase, sentence.text))
		return re.search(embodyingPhrase, sentence.text) is not None

	def findGoalsByDependency(self):
		for word in self.words:
			head = self.words[word['head']]

			if word['deprel'] == 'aux':
				if word['text'].casefold() in ['may', 'will', 'must', 'should']:
					self.addGoal2Tree(head)

			if word['deprel'].startswith('obl'):
				if head['xpos'] in ['VB', 'VBN', 'VBZ']:
					self.addGoal2Tree(head, word)
				
			if word['deprel'] == 'advcl':
				if head['xpos'] == 'VB':
					self.addGoal2Tree(word, head)
				if head['xpos'] == 'VBN':
					self.addGoal2Tree(word)

			if word['deprel'] == 'conj':
				self.addGoal2Tree(head)
				self.addGoal2Tree(word)

			if word['deprel'] == 'xcomp':
				if head['xpos'] in ['VB', 'VBN']:
					self.addGoal2Tree(word)
	
	def addGoal2Tree(self, word, child=None):
		embodyingPhrase = re.compile(r'^(especially|specifically|in particular|for example|for instance) *$', re.IGNORECASE)
		node = self.getGoalNode(word)

		#ゴールとして抽出されたフレーズが特定のフレーズでない場合、ゴールをゴールモデルに追加する
		if re.search(embodyingPhrase, node.getSpec()) is None:
			self.goalmodel.addGoal(node)
		
		if child is not None:
			#子が別のゴールに含まれる場合、子を含むゴールを作らない
			if self.isTempGoalIncludes(child):
				return

			child_node = self.getChildNode(child)
			if re.search(embodyingPhrase, child_node.getSpec()) is None:
				print(f"{word['text']}, {child['text']}")
				self.goalmodel.addGoal(child_node, node)
	
	def getGoalNode(self, word):
		goal = self.getTempGoalIncludes(word)

		if goal is not None:
			return self.goalmodel.getGoal(goal)
		else:
			node = self.makeGoalNode(word)
			self.findParentAndLink(node)
			return node

	def getChildNode(self, word):
		goal = self.getTempGoalIncludes(word)

		if goal is not None:
			return self.goalmodel.getGoal(goal)
		else:
			node = self.makeGoalNode(word)
			return node

	def makeGoalNode(self, word):
		goal = self.getGoal(word)
		goal_node = NB(goal)
		return goal_node

	def isTempGoalIncludes(self, word):
		for goal in self.tmp_goals:
			if word in self.tmp_goals[goal]:
				return True

		return False

	def getTempGoalIncludes(self, word):
		for goal in self.tmp_goals:
			if word in self.tmp_goals[goal]:
				return goal

		return None

	#ある単語に関係する単語を探し、ゴールとして登録する
	def getGoal(self, goal_top):
		depending_words = self.getDependingNodesRecursively(goal_top)
		depending_words.sort(key = lambda x: x['id'])

		goal = ''
		for word in depending_words:
			goal += word['text'] + ' '

		goal = goal[:-1]
		goal = self.markOffWithNewLine(goal)		
		self.tmp_goals[goal] = depending_words
		#self.logs.append(goal.replace('\n', ' '))
		self.np_lemmas_dict[goal] = self.extractNPLemmas(depending_words)
		print('>>> [' + goal_top['text'] + ' : ' + goal_top['deprel'] + ']')
		print('>>> ' + goal)
		return goal

	#ある単語に掛かり受けタグ上関係のある単語を再帰的に探し、リストを返す
	def getDependingNodesRecursively(self, parent):
		#既に別のゴールに含まれる単語は取得しない
		if self.isTempGoalIncludes(parent):
			return []

		depending_words = [parent]

		for word in self.words:
			if (word['head'] == parent['id']
					and self.isWordDependent(word)
					and not self.isTempGoalIncludes(word)):
				depending_words += self.getDependingNodesRecursively(word)

		return depending_words
	
	#ある単語に掛かり受けタグ上関係のある単語かどうかを返す
	def isWordDependent(self, word):
		return  (( word['deprel'] not in ['advcl', 'xcomp', 'punct', 'conj', 'cc']
					and not word['deprel'].startswith('obl'))
					or (not word['xpos'].startswith('VB') and word['deprel'] in ['conj', 'cc']))

	#文をN単語ごとに改行で区切る
	def markOffWithNewLine(self, sentence):
		words = sentence.split()
		new_sentence = ''

		while words != []:
			new_sentence += ' '.join(words[0:3]) + '\n'
			words = words[3:]
		
		return new_sentence

	#ある単語の群に含まれる名詞の原型を返す
	def extractNPLemmas(self, words):
		np_lemmas = set()

		for word in words:
			if word['upos'] == 'NOUN':
				np_lemmas.add(word['lemma'])
		
		return np_lemmas

	#ゴールツリーのノードを適当な親とくっつける
	def findParentAndLink(self, node):
		parent_node = self.findParent(node)
		self.linkNodes(parent_node, node)

	#ゴールツリーのノードの親をみつける
	#条件によって再帰する
	#訳あってfindWordIDInParentNodeByDependencyの中身を丸コピしています
	#不便ならfindWordIDInParentNodeByDependency（＝下の関数）を消して下さい
	def findParent(self, node):
		print(node.getSpec())
		words_in_goal = self.tmp_goals[node.getSpec()]

		isRecursive = False
		head_id = 0
		head = words_in_goal[0]

		while head is not None:
			isRecursive = head['deprel'] == 'conj'
			print(f"{head['id']}, {head['text']}, {head['head']}, {head['deprel']}, {isRecursive}")
			head_id = head['head']
			head = next(filter(lambda x:x['id'] == head_id, words_in_goal), None)

		parent_node = self.findParentNodeFromSentence(head_id)
		if parent_node is None:
			parent_node = self.findParentNodeFromTree(node)
		if isRecursive:
			parent_node = parent_node.getP() or self.findParent(parent_node)
			print(f"recursion: {parent_node.getSpec()}")
		return parent_node

	#ゴールノードの親ノードらしきノードに含まれる単語のIDを依存関係から探す
	def findWordIDInParentNodeByDependency(self, node):
		words_in_goal = self.tmp_goals[node.getSpec()]

		head_id = 0
		head = words_in_goal[0]

		while head is not None:
			print(f"{head['id']}, {head['text']}, {head['head']}")
			head_id = head['head']
			head = next(filter(lambda x:x['id'] == head_id, words_in_goal), None)

		print('exiting words_in_goal')
		return head_id


	#あるIDの単語を含むゴールを、同じ文章のゴールから探し、あればノードを返す
	def findParentNodeFromSentence(self, head_id):
		for goal in self.tmp_goals:
			head = next(filter(lambda x:x['id'] == head_id, self.tmp_goals[goal]), None)
			if head is not None and 0 < head_id:
				print(f"{head['id']}, {head['text']}, {head['head']}")
				print(self.goalmodel.getGoal(goal).getSpec().replace('\n',' '))
				return self.goalmodel.getGoal(goal)
		
		return None
	
	#あるゴールノードの親をゴールツリーから探す
	def findParentNodeFromTree(self, node):
		if next(filter(lambda x:x['text'] == '(embodying)', self.words), None) is not None:
			print('>>>>>>>>found embodyment')
			return self.goalmodel.getLastAddedGoal()

		tmp_parent_node = self.goalmodel.getLastAddedGoal()
		lemma_intersect = self.getLemmaIntersect(node, tmp_parent_node)

		while tmp_parent_node.getP() is not None:
			next_parent_node = tmp_parent_node.getP()
			next_lemma_intersect = self.getLemmaIntersect(node, next_parent_node)
			if lemma_intersect <= next_lemma_intersect:
				tmp_parent_node = next_parent_node
				lemma_intersect = next_lemma_intersect
			else:
				break
		
		return tmp_parent_node
	
	def getLemmaIntersect(self, node, parent_node):
		node_np_lemma = self.np_lemmas_dict[node.getSpec()]
		parent_node_np_lemma = self.np_lemmas_dict[parent_node.getSpec()]
		return node_np_lemma & parent_node_np_lemma

	#ゴールツリーのノードとノードを繋ぐ
	def linkNodes(self, parent_node, child_node):
		print('[parent]: ' + parent_node.getSpec().replace('\n',' '))
		print('[child]: ' + child_node.getSpec().replace('\n',' '))
		if parent_node == child_node:
			print('\n\n\n<<<<<<<<<<<<<<<< Loop Detected!!!! >>>>>>>>>>>>>>>>')
			print('\n\n')
		
		parent_node.setC(child_node) #parentの子にchildを配置する
		child_node.setP(parent_node) #childの親にparentを配置する

	
	def showEachGoalImportance(self, goals_ranking):
		max_score = max(goals_ranking.keys())

		for rank in goals_ranking:
			for goal in goals_ranking[rank]:
				goal_text = goal.getSpec().replace('\n', ' ')
				print(f'{rank}, {goal_text}')
				self.logs.append(f'{rank}, {goal_text}')



from datetime import datetime
import time

if __name__ == '__main__':
	args = sys.argv
	openfilename = args[1]

	time = datetime.now().strftime('%Y-%m-%d-%H%M%S')

	constructor = GoalModelConstructor(format='png', logfile=logfile)
	text = GoalModelConstructor.readSpecification(openfilename)
	constructor.analyzeSpecification(text)