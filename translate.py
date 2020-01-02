import sys
import argparse
from JsonDict import JsonToDict
from difflib import SequenceMatcher
import boto3
import json

# TODO:
# 1. add functionality -> if no translation in dest - > add it there (? maybe consider it as additional parameter)
# 2. one more parameter -> where to save file with translation
# 3. create output files -> one more parameter for checking translation


def calc_similarity(psource, psentence, pidx):
    max_ratio = 0
    max_idx = ''
    line, i = -1, 0
    for idx, sentence in psource.items():
        if pidx == idx:
            continue
        similarity = SequenceMatcher(
            lambda x: x in " \t", sentence, psentence)

        if max_ratio < similarity.ratio():
            max_ratio = similarity.ratio()
            max_idx = idx
            line = i
        i += 1
    return (max_ratio, line, max_idx)


parser = argparse.ArgumentParser(prog='translate')
parser.add_argument('--from',
                    help='JSON file that needs to be translated', required=True)
parser.add_argument('--to',
                    help='JSON file where should be saved translation', required=True)
parser.add_argument('--language',
                    help='language code (sv, en, ru, es etc.)', required=True)
parser.add_argument('--profile',
                    help='AWS profile that will be used for translation')

args = vars(parser.parse_args(sys.argv[1:]))

json_dict_from = JsonToDict()
json_dict_to = JsonToDict()

# Create temporal CSV for source
source = json_dict_from.create(args['from'])

# Create temporal CSV for dest
dest = json_dict_to.create(args['to'])


# find sentences that needs to be translated
for_translation = {}
for idx in source.keys():
    if idx not in dest.keys() or len(dest[idx]) == 0:
        for_translation[idx] = source[idx]

# calculate similarity
i = 0
delete = []
for idx, sentence in for_translation.items():
    res = calc_similarity(source, sentence, idx)
    if res[0] >= 0.97 and res[2] in dest.keys() and len(dest[res[2]]) > 0:
        dest[idx] = dest[res[2]]
        delete.append(idx)

for idx in delete:
    del for_translation[idx]

# start translation
session = boto3.Session(profile_name=args['profile'])
translate = session.client('translate')

for idx, sentence in for_translation.items():
    text = translate.translate_text(
        Text=sentence, SourceLanguageCode='en', TargetLanguageCode=args['language']
    )
    for_translation[idx] = text['TranslatedText']
    dest[idx] = text['TranslatedText']

'''
with open('source.json', 'w', encoding='utf-8') as fsource:
    for idx, sentence in source.items():
        fsource.write('%s:"%s"\n' % (idx, sentence))
    fsource.close()
'''

with open(args['to'], "r", encoding='utf-8') as file:
    data = json.load(file)
with open(args['to'], 'w', encoding='utf-8') as fnew_tree:
    translation = json_dict_to.translate_tree("", data, dest)
    json.dump(translation, fnew_tree, ensure_ascii=False, indent=4)
