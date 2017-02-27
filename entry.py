def readin(filename):
    f = open(filename, 'r')
    o = f.readlines()
    entries = []
    for line in o:
        name, reactID, url, event = Entry.parseLine(line)
        entries.append(Entry(name, reactID,url,event))
    return entries

class Entry(object):
    def __init__(self, name, reactID, url, eventSummary):
        self.name = name
        self.reactID = reactID
        self.url = url
        self.eventSummary = eventSummary

    @staticmethod
    def parseLine(line):
        line = line.strip()
        line = line.split('\t')
        return line[0], line[1], line[2], line[3]

class Gene(object):
    def __init__(self, name):
        self.name = name.strip()
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)
