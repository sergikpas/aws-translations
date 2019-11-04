from difflib import SequenceMatcher
import json


class SimilarTranslation:
    def load(self, psource, ptranslate):
        for idx, sentence in ptranslate.items():

        return False

    def calc_similarity(self, p_source, p_sentence):
        max_ratio = 0
        line, i = -1, 0
        for sentence in p_source:

            similarity = SequenceMatcher(
                lambda x: x in " \t", sentence, p_sentence)

            if max_ratio < similarity.ratio():
                max_ratio = similarity.ratio()
                line = i
            i += 1
        return (max_ratio, line)
