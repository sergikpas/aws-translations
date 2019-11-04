import json
import csv
import hashlib
import sys


class JsonToDict:
    path = {}
    translation = {}

    # Parse tree with recursion
    def parse_json_tree(self, plabel, ptree):
        label = ""
        if plabel != "":
            label = plabel + "."
        for key, value in ptree.items():
            if type(ptree[key]) is dict:
                self.parse_json_tree(label + key, ptree[key])
            elif type(ptree[key]) is list:
                i = 0
                for value in ptree[key]:
                    self.path[hashlib.sha256(
                        (label + key + "." + str(i)).encode()).hexdigest()] = value
                    i += 1
            else:
                self.path[hashlib.sha256((label + key).encode()
                                         ).hexdigest()] = ptree[key]

    # parse tree with stack
    def parse_json_tree_stack(self, ptree):
        Queue = list()
        Queue.append((ptree, '.'))
        while len(Queue) > 0:
            item = Queue.pop()
            for key, item_value in item[0].items():
                if type(item_value) is dict:
                    Queue.append([item_value, item[1] + '.' + key])
                elif type(item_value) is list:
                    i = 0
                    for value in item_value:
                        self.path[hashlib.sha256(
                            (item[1] + '.' + key + "." + str(i)).encode()).hexdigest()] = value
                        #self.path[item[1] + '.' + key + "." + str(i)] = value
                        i += 1
                else:
                    self.path[hashlib.sha256(
                        (item[1] + '.' + key).encode()).hexdigest()] = item_value
                    #self.path[item[1] + '.' + key] = item_value
        return self.path

    # Translate JSON tree
    #   ptree - that needs to be translated
    #   ptranslation - translations of the tree
    def translate_tree(self, plabel, ptree, ptranslations):
        label = "."
        if plabel != "":
            label = plabel
        for key, value in ptree.items():
            if type(ptree[key]) is dict:
                ptree[key] = self.translate_tree(
                    label + "." + key, ptree[key], ptranslations)
            elif type(ptree[key]) is list:
                i = 0
                for value in ptree[key]:
                    idx = hashlib.sha256(
                        (label + "." + key + "." + str(i)).encode()).hexdigest()
                    if idx in ptranslations:
                        ptree[key][i] = ptranslations[idx]
                    i += 1
            else:
                idx = hashlib.sha256((label + "." + key).encode()).hexdigest()
                if idx in ptranslations:
                    ptree[key] = ptranslations[idx]
        return ptree

    # Save converted file to Tmp directory
    def create(self, pfile_from):
        try:
            self.path = {}
            with open(pfile_from, "r", encoding='utf-8') as file:
                data = json.load(file)

            self.parse_json_tree_stack(data)

            return self.path
        except:
            print(sys.exc_info()[0], "occured.")
            return False

        return True
