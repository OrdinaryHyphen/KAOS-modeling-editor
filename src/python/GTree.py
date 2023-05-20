# coding: utf-8

import os
from graphviz import Digraph

class GNode:
    def __init__(self, spec, parent=None, children=None, aggrFlg=False, andFlag=True):
        self.__spec = spec
        self.__parent = parent
        self.__id = 0 #後で変更
        if not children:
            self.__children = dict()
            self.__children['NB'] = []
        else:
            self.__children = children
        self._style = {'style':'filled', 'shape':'box', 'fillcolor':'#d5ffff'}
        self.__cstyle = {'width':'0.2', 'style':'filled', 'shape':'circle', 'fillcolor':'#ffff00'}
        self.__aggrFlg = aggrFlg
        self.__about = None
        self.__andFlag = andFlag #__andFlag = False はORを表す

    def setSpec(self, spec):
        self.__spec = spec

    def setP(self, parent):
        self.__parent = parent

    def setC(self, child):
        self.__children[type(child).__name__].append(child)

    def setID(self, gid):
        self.__id = gid

    def setAndFlag(self):
        self.__andFlag = True

    def setOrFlag(self):
        self.__andFlag = False

    def isAndFlag(self):
        return self.__andFlag

    def setAbout(self, goal):
        self.__about = goal

    def getSpec(self):
        return self.__spec

    def getID(self):
        return self.__id

    def getDepth(self):
        if self.__parent is None: 
            return 0
        else:
            return self.__parent.getDepth() + 1

    def getP(self):
        return self.__parent

    def getC(self, idx, gtype):
        children = self.__children[gtype.__name__]
        if idx >= len(children):
            print('[ERROR] getC: Out of index')
            return None
        else:
            return children[idx]

    def getCs(self, gtype):
        return self.__children[gtype.__name__]
    
    def addMyTree2Dict(self, goals_dict):
        depth = self.getDepth() 
        if depth not in goals_dict:
            goals_dict[depth] = []
        goals_dict[depth].append(self)

        allchild = self.__children['NB']
        for child in allchild:
            child.addMyTree2Dict(goals_dict)
        
        return goals_dict

    def getTransaction(self, gtype):
        return [goal for goal in self.__children[gtype.__name__] if not goal.isAggregated()]

    def showCs(self):
        print('')
        print('')
        children = self.getCs(NB)
        print('     Children of the goal \'' + self.getSpec() + '\' are these.')
        for i, child in enumerate(children):
            print('      ', end='')
            if i == len(children)-1:
                print('┗', child.getSpec())
            else:
                print('┣', child.getSpec())
        else:
            print('')

    def removeCs(self, children, gtype):
        self.__children[gtype.__name__].remove(children)

    def removeAllCs(self, gtype):
        self.__children[gtype.__name__] = []

    def isLeaf(self):
        return (len(self.__children['NB'])) == 0

    def isAggregated(self):
        return self.__aggrFlg

    def setAggrFlg(self):
        self.__aggrFlg = True

    def resetAggrFlg(self):
        self.__aggrFlg = False

    def print(self, tab=''):
        print(tab + str( self.getDepth() ) + ', ' + self.__spec.replace('\n', ' '))
        allchild = self.__children['NB']
        for child in allchild:
            child.print(tab + '  ')

    def getDOT(self, graph, centerid):
        spec = self.__spec
        if self.__about:
            spec += '\n[' + self.__about.getSpec() + ']'
        if self.__aggrFlg:
            graph.node('g'+str(self.__id), spec,
                       {'style': 'filled', 'shape': 'parallelogram', 'fillcolor': 'white:#777777',
                        'gradientangle': '270'})
        else:
            splitLabel = spec.split('\\n')

            labeling = ('\n').join(splitLabel)
            graph.node('g'+str(self.__id), labeling, self._style)
        topid = self.__id
        ceid = centerid
        Cs = self.getCs(NB) #ANDとORについて
        if len(self.__children['NB']) != 0:
            if self.__andFlag == True:#親のフラッグがTrueなら黄玉、Falseならなし
                graph.node('c' + str(centerid), '', self.__cstyle)
                graph.edge('c' + str(centerid), 'g' + str(self.__id), arrowhead='normal', headport='s')

        for children in [self.__children['NB']]:
            for child in children:
                ceid += 1
                (chid, ceid) = child.getDOT(graph, ceid)
                #ここでandFlagを覗いてそれがTrueなら下の行、Falseなら('g'+ str(self.__id)とつなぐ）
                if self.__andFlag == False:
                    graph.edge('g' + str(chid), 'g' + str(self.__id), arrowhead='normal', headport='s')
                else:
                    graph.edge('g' + str(chid), 'c' + str(centerid), arrowhead='none', tailport='n')
        return (topid, ceid)

class NB(GNode):
    def __init__(self, spec, parent=None, children=None, aggrFlg=False, andFlag=True):
        super(NB, self).__init__(spec, parent=parent, children=children, aggrFlg=aggrFlg, andFlag=andFlag)
        self._style['fillcolor'] = '#d5ffff'


class GTree:
    def __init__(self, format):
        self.__root = NB('Root')
        self.__last = self.__root
        self.__lastNB = self.__root
        self.__numgoal = 0
        self.__goals = dict()
        self.__g = Digraph(format=format)
        self.__g.graph_attr['layout'] = 'dot'
        self.__g.graph_attr['rankdir'] = 'BT'
        self.__g.graph_attr['splines'] = 'line'
        self.__g.node_attr['fontname'] = 'MS UI Gothic'
        self.__g.edge_attr['style'] = 'solid'

    def formatGraph(self):
        self.__g = Digraph(format='png')
        self.__g.graph_attr['layout'] = 'dot'
        self.__g.graph_attr['rankdir'] = 'BT'#BT
        self.__g.graph_attr['splines'] = 'line'
        self.__g.node_attr['fontname'] = 'MS UI Gothic'
        self.__g.edge_attr['style'] = 'solid'

    def getRoot(self):
        return self.__root

    def incrementNumgoal(self):
        self.__numgoal = self.__numgoal + 1

    def getNumgoal(self):
        return self.__numgoal

    def isFirstGoal(self):
        return self.__numgoal == 1
    
    def getGoal(self, spec):
        return self.__goals.get(spec)

    def addGoal(self, ngoal, parent=None):
        if not ngoal:
            print('[ERROR] addGoal: No goal is to be added')
            return
        
        self.__goals[ngoal.getSpec()] = ngoal 
        self.__numgoal += 1
        ngoal.setID(self.__numgoal)
        if parent:
            ngoal.setP(parent)#ngoalの親にparentを配置し
            parent.setC(ngoal)#parentの子にngoalを配置する
        #else:#3つ目の引数がないときは親がないので、Rootの下に新しい親として配置する
            #ngoal.setP(self.__root)
            #self.__root.setC(ngoal)
        self.__last = ngoal
        if type(ngoal) == NB:
            self.__lastNB = ngoal

    def getLastAddedGoal(self):
        return self.__last
    
    def resetHistory(self):
        self.__last = self.__root

    def isGoalsInclude(self, spec):
        return spec in self.__goals

    def print(self):
        self.__root.print()

    def getGoalsDict(self):
        return self.__root.addMyTree2Dict(dict())

    def render(self):
        self.__root.getDOT(self.__g, 0)
        print(self.__g.source)
        return self.__g.source