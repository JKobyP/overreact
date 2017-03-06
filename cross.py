''' performs cross validation '''
import operator
import entry
import sys
from os import path, mkdir
from graph import EventNode, BFS
from math import inf

class Model(object):
    def __init__(self, dbData, knownset):
        self.data = dict()
        for entr in dbData:
            self.data[entry.Gene(entr.name)] = entr
        self.populate(knownset)

    def populate(self, knownset):
        self.knownset = knownset
        self.eventWeight = dict()
        for entr in self.data.values():
            for gene in self.knownset:
                event = self.gene_to_event(gene)
                if entr.reactID == event:
                    if event not in self.eventWeight:
                        self.eventWeight[event] = 1
                    else:
                        self.eventWeight[event] += 1

    def score(self, gene, branchfactor):
        event = EventNode(self.gene_to_event(gene))
        knownEvents = list(map(lambda x: EventNode(self.gene_to_event(x)),
            self.knownset))
        score, nearestKnown = BFS(event,branchfactor,knownEvents)
        if score is None:
            return inf
        score = score + 1
        if not nearestKnown is None and nearestKnown in self.eventWeight:
            score = score / self.eventWeight[nearestKnown]
        return round(score,5)

    def gene_to_event(self, gene):
        if gene not in self.data:
            #print("{0} not in the dataset".format(gene))
            return ""
        return self.data[gene].reactID

# 'effort' is a parameter which increases the time spent
# for the analysis of the score
def ValidateOne(data, knownset, unknownset, effort):
    m = Model(data, knownset)
    scores = []
    for i, gene in enumerate(unknownset):
        print("Scoring gene {0}: {1}".format(i,gene))
        scores.append((gene,m.score(gene, effort)))
    scores = sorted(scores, key=operator.itemgetter(1))
    return scores, m

def Validate(data, knownset, unknownset, effort):
    experiments = []
    for test in knownset:
        kset = knownset.copy()
        kset.remove(test)
        unknownset.append(test)
        experiments.append((ValidateOne(data, kset, unknownset, effort),test))
        unknownset.remove(test)
    return experiments


def main():
    # process args
    if len(sys.argv) != 6:
        print("wrong number of args")
        return
    name, dbFile, knownGeneF, unknownF, effort = sys.argv[1:]
    effort = int(effort)

    # Process input
    indir = path.join("input", "known")
    knownGeneF = path.join(indir, knownGeneF)
    unknownF = path.join("input", unknownF)

    # process data from files
    data = entry.readin(dbFile)
    knownlist = []
    for gene in open(knownGeneF, 'r').readlines():
        knownlist.append(entry.Gene(gene))
    unknownlist = []
    for gene in open(unknownF, 'r').readlines():
        unknownlist.append(entry.Gene(gene))

    # Run validation
    experiments =  Validate(data, knownlist, unknownlist, effort)

    # Process output
    outdir = "out"
    if not path.exists(outdir):
        mkdir(outdir)
    for i, ((rank, m), test) in enumerate(experiments):
        knownOut = open(path.join(outdir,'{0}Known{1}.out'.format(name,i)),'w')
        rankedOut = open(path.join(outdir,'{0}Ranked{1}.out'.format(name,i)),'w')
        for g in knownlist:
            if g not in m.data:
                knownOut.write("{0}\tNone\tNone\n".format(g.name))
                continue
            entr = m.data[g]
            knownOut.write("{0}\t{1}\t{2}\n".format(entr.name, entr.reactID,
                entr.eventSummary))
        for (g, score) in rank:
            if g not in m.data:
                rankedOut.write("{0}\tNone\tNone\tNone\n".format(g.name))
                continue
            if g == test:
                entr = m.data[g]
                rankedOut.write("{0}\t{1}\t{2}\t{3}\ttest\n".format(entr.name, entr.reactID,
                    entr.eventSummary, score))
                continue
            entr = m.data[g]
            rankedOut.write("{0}\t{1}\t{2}\t{3}\n".format(entr.name, entr.reactID,
                entr.eventSummary, score))
        knownOut.close()
        rankedOut.close()
    #for g, s in rank:
    #    print("({0}: {1})\t".format(g,s))
    EventNode.session.close()

if __name__ == "__main__":
    main()
