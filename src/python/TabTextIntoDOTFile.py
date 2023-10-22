# coding: utf-8

import re
import stanza
from GTree import GTree, NB
from StanzaSeparateConj import getGoal
s = {NB: 'Normal Behavior'}


#要求記述解析を行うクラスの本体。
class GoalModelConstructor:
	def __init__(self, format='png', logfile=None, blur=None):
		self.goalmodel = GTree(format)
		self.__log = logfile
		#self.__effect = blur
		
		self.logs = [] #ログのリスト。ここにログを保存し、writeLog()の処理で外部ファイルに出力する。
		self.goal_node = None #今扱っているゴールモデルの頂点。

	def analyzeSpecification(self, text):
		self.goalmodel.formatGraph()

		for line in text.splitlines():
			if not re.match(r'[G|0-9].*', line):
				continue
			self.addGoal(line)

		return self.goalmodel.render()

	def addGoal(self, line):
		print(line)
		#print(line.split(' ')[1])
		goal_id = '.' + line.split(' ')[0].replace('Goal ', '')
		goal = ' '.join(line.split(' ')[1:])
		goals = []
		print(line.split(' '))
		print(goal)

		if ' and ' in goal.casefold() or ' or ' in goal.casefold():
			doc = nlp(goal)
			for	sent in doc.sentences:
				words = sent.to_dict()
				root = [word for word in words if word['head'] == 0][0]
				goals += getGoal(root, words)
		else:
			goals = [goal]

		for goal in goals:
			self.goal_node = NB('')
			self.goal_node.setSpec(self.markOffWithNewLine(goal))

			parent = self.goalmodel.getLastAddedGoal()
			while parent is not None:
				print(parent.getNote(), goal_id, goal_id.startswith(parent.getNote()) and goal_id != parent.getNote())
				if goal_id.startswith(parent.getNote()) and goal_id != parent.getNote():
					self.goalmodel.addGoal(self.goal_node, parent)
					self.goal_node.setNote(goal_id)
					break 
				else:
					parent = parent.getP()
					print(parent.getNote())

	#文をN単語ごとに改行で区切る
	def markOffWithNewLine(self, sentence):
		words = sentence.split()
		new_sentence = ''

		while words != []:
			new_sentence += ' '.join(words[0:3]) + '\\n'
			words = words[3:]
		
		return new_sentence.replace('\\n.','.')


	def writeLog(self):
		with open(self.__log, 'a') as f:
			logs = ''

			for log in self.logs:
				logs += log + '\n'
			f.write(logs)


nlp = stanza.Pipeline(lang='en', processors= 'tokenize,mwt,pos,lemma,depparse')