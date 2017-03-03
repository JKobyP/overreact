from neo4j.v1 import GraphDatabase, basic_auth
from collections import deque

class EventNode(object):
    session = GraphDatabase.driver("bolt://localhost:7687",
                auth=basic_auth("neo4j","1234")).session()
    def __init__(self, stid):
        self.stid = stid
    def setDisplayName(self, name):
        self.name = name
    def getSubPaths(self):
        try:
            if EventNode.session.connection.closed == True:
                EventNode.session = EventNode.newSession()
            spathsCmd = """
                 MATCH (pathway:Pathway{stId:{stId}})-[:hasEvent]-> (sp:Pathway)
                RETURN sp.stId"""
            spaths = EventNode.session.run(spathsCmd, {"stId":self.stid})
            sps = []
            for sp in spaths:
                sps.append(EventNode(sp["sp.stId"]))
            return sps
        except:
            return self.getSubPaths()
    def getParents(self):
        try:
            if EventNode.session.connection.closed == True:
                EventNode.session = EventNode.newSession()
            parentCmd = """
                MATCH (p:Pathway{stId:{stId}})<-[:hasEvent]-(sp:Pathway)
                RETURN sp.stId AS SuperPathway """
            parent = EventNode.session.run(parentCmd, {"stId":self.stid})
            parents = []
            for p in parent:
                parents.append(EventNode(p["SuperPathway"]))
            return parents
        except:
            return self.getParents()
    @staticmethod
    def exampleNode():
        return EventNode("R-HSA-1236975")
    @staticmethod
    def newSession():
        return GraphDatabase.driver("bolt://localhost:7687",
                auth=basic_auth("neo4j","1234")).session()

def BFS(start, depth, goallist):
    levelnum = 0
    olist = deque([[start]])
    while len(olist[0]) > 0 and levelnum <= depth:
        level = olist.popleft()
        successors = []
        for n in level:
            for goal in goallist:
                if n.stid == goal.stid:
                    return levelnum
            else:
                successors.extend(n.getSubPaths())
                successors.extend(n.getParents())
        olist.append(successors)
        levelnum = levelnum + 1
