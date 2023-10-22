# coding: utf-8

from GTree import GTree, NB
s = {NB: "Normal Behavior"}


#ある単語に掛かり受けタグ上関係のある単語を再帰的に探し、リストを返す
def getDependingNodesRecursively(parent, words):
	depending_words_list = [[]]
	conjunction_branch = [[parent]]

	for word in words:
		if word['head'] == parent['id']:
			if word['text'].casefold() in ['and','or',',']:
				pass
			elif word['deprel'] == 'conj':
				conjunction_branch += getDependingNodesRecursively(word, words)
			else: 
				additional_words_list = getDependingNodesRecursively(word, words)			
				if additional_words_list is None:
					continue
				if parent['id'] < word['id'] and len(conjunction_branch) == 1:
					new_list = []
					for branch in conjunction_branch:
						if parent not in branch:
							continue
						for additional_words in additional_words_list:					
							new_list.append(branch + additional_words)
					conjunction_branch = new_list
				else:
					new_list = []
					for depending_words in depending_words_list:
						for additional_words in additional_words_list:
							new_list.append(depending_words + additional_words)
					depending_words_list = new_list

	return [depending_words + branch for depending_words in depending_words_list for branch in conjunction_branch]

#ある単語に関係する単語を探し、ゴールとして登録する
def getGoal(goal_top, words):
	depending_words_list = getDependingNodesRecursively(goal_top, words)

	goals = []
	for depending_words in depending_words_list:
		#print(depending_words)
		depending_words.sort(key = lambda x: x['id'])

		goal = ''
		for word in depending_words:
			goal += word['text'] + ' '

		goal = goal[:-1]
		goals.append(goal)
	
	return goals



"""
#Stanzaの使用
nlp = stanza.Pipeline(lang='en', processors= 'tokenize,mwt,pos,lemma,depparse')
doc = nlp("it should support subscriptions to e-journals, provide access to foreign digital libraries (under specific conditions), support e-mail communication between staff and users, enable bibliographical from anywhere at any time, and provide a Web-based interface e-seller comparison, selection, and order submission.")

#print(doc)
for	sent in doc.sentences:
	for word in sent.words:
		print(word)

goals = []
for	sent in doc.sentences:
	words = sent.to_dict()
	root = [word for word in words if word['head'] == 0][0]
	goals += getGoal(root, words)

for goal in goals:
	print(goal)
"""