import json
import os

#run pip3 install strsim
#lib found from https://pypi.org/project/strsim/#weighted-levenshtein
from similarity.weighted_levenshtein import WeightedLevenshtein
from similarity.weighted_levenshtein import CharacterSubstitutionInterface

#open dictionary


#class to change the weights of the
class CharacterSubstitution(CharacterSubstitutionInterface):
    def cost(self, c0, c1):
        if c0=='t' and c1=='r':
            return 1
        return 1

weighted_levenshtein = WeightedLevenshtein(CharacterSubstitution())


def getMatches(query, collection):
    with open(collection+'allTerms.dat') as json_file:
        allterms = json.load(json_file)

    # dict of terms
    best_matches = ['','','','','']
    best_matches_distances = [999,999,999,999,999]
    for term in allterms: #iterate through terms
        if term != "":
            if term[0] == query[0]: #people very rarely get the first letter wrong, limit the search to  words starting with the same letter
                distance = weighted_levenshtein.distance(query, term) #find weighted distance of the term and query

                for i in range(len(best_matches_distances)):#look too see if this term is a better match than any currently in the top 5
                    if distance < best_matches_distances[i] and term not in best_matches:
                        best_matches_distances[i] = distance
                        best_matches[i] = term
                        break

    return best_matches, best_matches_distances



















