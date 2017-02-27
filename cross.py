''' performs cross validation '''
import operator
import entry
import sys

class Model(object):
    def __init__(self, dbData, knownset):
        self.data = dict()
        for entr in dbData:
            self.data[entry.Gene(entr.name)] = entr
        self.pathwayTemp = dict()
        self.populate(knownset)

    def populate(self, knownset):
        self.knownset = knownset
        for gene in self.knownset:
            event = self.gene_to_event(gene)
            if event not in self.pathwayTemp:
                self.pathwayTemp[event] = 1
            else:
                self.pathwayTemp[event] += 1

    def score(self, gene):
        event = self.gene_to_event(gene)
        if event in self.pathwayTemp:
            return self.pathwayTemp[event]
        return 0

    def gene_to_event(self, gene):
        if gene not in self.data:
            print("{0} not in the dataset".format(gene))
            return ""
        return self.data[gene].reactID


def Validate(data, knownset, unknownset):
    test = knownset.pop()
    unknownset.append(test)
    m = Model(data, knownset)
    scores = []
    for gene in unknownset:
        scores.append((gene,m.score(gene)))
    scores = sorted(scores, key=operator.itemgetter(1))
    return scores

def main():
    # process args
    if len(sys.argv) != 4:
        print("wrong number of args")
        return
    dbFile, knownGeneF, unknownF = sys.argv[1:]
    # process data from files
    data = entry.readin(dbFile)
    knownlist = []
    for gene in open(knownGeneF, 'r').readlines():
        knownlist.append(entry.Gene(gene))
    unknownlist = []
    for gene in open(unknownF, 'r').readlines():
        unknownlist.append(entry.Gene(gene))
    rank = Validate(data, knownlist, unknownlist)
    for g, s in rank:
        print("({0}: {1})\t".format(g,s))

if __name__ == "__main__":
    main()
