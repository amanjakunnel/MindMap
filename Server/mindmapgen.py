import os
import docx
import PyPDF2
import spacy
import RAKE
import operator
from collections import Counter
from string import punctuation
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download  ('omw-1.4')
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from rake_nltk import Rake

def extract(filepath):
    file_ext = os.path.splitext(filepath)[1]
    if file_ext == '.docx':
        doc = docx.Document(filepath)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)
    if file_ext == '.pdf':
        pdfFileObj = open(filepath, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        n = pdfReader.numPages
        text = ''
        for i in range(n):
            pageObj = pdfReader.getPage(i)
            text += pageObj.extractText()
        pdfFileObj.close()
        return text
    if file_ext == '.txt':
        myfile = open(filepath, "rt")
        contents = myfile.read() 
        myfile.close()
        return contents

def paras(text):
    p = []
    for line in text.split('\n'):
        if line.count('. ') > 1:
            p.append(line)
    return '\n'.join(p)

def prenlp(string):
    text = ''
    for c in string:
        if c.isalpha() or c == ' ' or c == '\n':
            text += c
        else:
            text += ' '
    paras = text.split('\n')
    output = ""
    for para in paras:
        output += ' '.join(para.split()) + '\n'
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(output)
    lemmatizer = WordNetLemmatizer()
    filtered_sentence = ' '.join([lemmatizer.lemmatize(w.lower(), get_wordnet_pos((w))) for w in word_tokens if w.lower() not in stop_words])
    return filtered_sentence

def get_wordnet_pos(word):
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def penn2morphy(penntag):
    morphy_tag = {'NN':'n', 'JJ':'a', 'VB':'v', 'RB':'r'}
    try:
        return morphy_tag[penntag[:2]]
    except:
        return 'n' 

def spacy_extraction(text):
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(text)
    return doc.ents

def rake_nltk_extraction(text):
    rake_nltk_var = Rake()
    rake_nltk_var.extract_keywords_from_text(text)
    keyword_extracted = rake_nltk_var.get_ranked_phrases()
    return keyword_extracted

def rake_extraction(text):
    stop_dir = 'StopWords.txt'
    rake_object = RAKE.Rake(stop_dir)
    keywords = Sort_Tuple(rake_object.run(text))[-10:]
    keyphrases = [x[0] for x in keywords]
    return keyphrases

def Sort_Tuple(tup):
    tup.sort(key = lambda x: x[1])
    return tup

def spacy_extraction_alt(text):
    nlp = spacy.load("en_core_web_lg")
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text.lower())
    for token in doc:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)
    output = [(x[0]) for x in Counter(result).most_common(5)]
    return output

def text_summarization(text):
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1
    sentences = sent_tokenize(text)
    sentenceValue = dict()
    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq
    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    average = int(sumValues / len(sentenceValue))
    summary = ""
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
    return summary

def keyphrase_extraction(text, keywords):
    d = {}
    for key in keywords:
        d[key] = []
    for line in text.split('\n'):
        freq = {}
        max = 0
        curr = keywords[0]
        for key in keywords:
            occur = line.split().count(key)
            freq[key] = occur
            if occur > max:
                max = occur
                curr = key
        if max != 0:
            d[curr].append(line)
    phrased = {}
    for key in keywords:
        subdoc = '\n'.join(d[key])
        subdoc_rem = ' '.join([w for w in subdoc.split() if w != key])
        phrased[key] = rake_extraction((subdoc_rem))
    return phrased

def nodes(title, d):
    l = {"1": {"id": 1, "label": title}}
    id = 2
    for key in d:
        curr = id
        l[str(curr)] = {"id": curr, "label": key, "parent": 1}
        id += 1
        for phrase in d[key]:
            l[str(id)] = ({"id": id, "label": phrase, "parent": curr})
            id += 1
    return l

#print(prenlp(paras(extract("smash.docx"))))
title = extract("smash.docx").split('\n')[0]
text = prenlp(paras(extract("smash.docx")))
keywords = spacy_extraction_alt(text)
phrases = keyphrase_extraction(text, keywords)
print(nodes(title, phrases))


'''
print(spacy_extraction_alt(prenlp(paras(extract("smash.docx")))))

print(prenlp(extract("mitochondria.txt")))

text = extract("mitochondria.txt")
print(spacy_extraction_alt(text))

text = extract("mitochondria.txt")
title = text.split('\n', 1)[0]
ll = [{"id": 1, "label": "Interests"}]
curr = 1
d = {}
p = paras(text)
prep = prenlp(text)
summary = text_summarization(p)
keywords = spacy_extraction(summary)
p = p.replace('.\n\n', '. ')
p = p.replace('.\n', '. ')
sentences = p.split('. ')
for sent in sentences:
    for key in keywords[:len(keywords)//3]:
        curr += 1
        if key not in d:
            d[key] = curr
            ll.append({"id": curr, "label": key, "parent": 1})
        if key in sent:
            curr += 1
            ll.append({"id": curr, "label": sent, "parent": d[key]})

print(ll)'''