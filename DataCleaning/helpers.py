import re
import bson
import gzip

regex_mappings = {"website": re.compile('http\S+|www\S+'),
                  "duration": re.compile(
                      "(\d+\syears\sto\s\d+\syears|\d+[+]?\syear[s]?|\(\d+-\d+\)\syears|\(\d+\)\smonths|\d+\splus\syears|\d+\+\syears|\d+\syrs.\sto\s\d+\syrs.|\d+\s-\s\d+\syears|\d+\sto\s\d+\syears|\d+\s\+\syears|\d+-\d+\syear[s]?|\d+\s-\s\d+\syrs|\d+-\d+yrs|\d+to\s\d+\syrs|\d+\smonths\sto\s\d+\syear[s]?|\d+months\sto\s\d+years|\d+-\s\d+\syears|\d+\sto\s\d+\syrs|\d+-\d+\syrs|\d+yrs\sto\s\d+\syrs|\d+\sto\s\d+|\d+\+\syrs|\d+\smonths|\d+\s-\d+\syears|\d+\s-\s\d+yrs|\d+\s-\s\d+years)"),
                  "timings": re.compile("\d+.\d+\s(pm|am)\s(-|to)\s\d+.\d+\s?(pm|am)|\d+(pm|am)\s-\s(\d+(am|pm)|\d+\s:\s\d+(am|pm))|\d+\s+(:|-)\s+\d+(am|pm)\s(-|to)\s\d+(am|pm|\s:\s\d+(am|pm))|\d+.\d+(pm|am)\s-\s\d+(.\d+)?(pm|am)?|\d+.\d+\s-\s(pm|am)\s-\s\d+(pm|am)|(\d+.)?\d+(am|pm)(\s(-|to)\s)?(\d+.\d+(pm|am))?|\d+(.\d+)?\s-\s\d+.\d+(am|pm)|\d+.\d+\s-\s\d+(am|pm)|(\d+|\d+.\d+)\s(am|pm)"),
                  "money": re.compile("\$(\s)?\d+(\,\d+)?(\.\d+)?(k)?(\s(p.a|pa)|(\s)?(\+)?(\s)?(per|ph|plus|p|an)((\s/)?\s(hour|hr|h|annum))?|(\s)?(\s\-\s)?(\d+\s)?(billion|million|m)|\s\-\s\d+(k)?(\s\(\sper\sannum\s\))?|\s\,\s\d+(\.\d+)?|(\.\d+\s)?(billion|b)|\s\d+|\s\/\shr|'s)?", flags=re.IGNORECASE),
                  "phone": re.compile(
                      "\d{4}\s\d{2}\s\d{2}\s\d{2}|\d{2}\s\d{3}\s\d{4}|\+?\d{9,12}|\(\s\d{2}\s\)\s\d{3}\s\d{4}|\d{4}\s\d{3}\s\d{3}|\(\s\d{2}\s\)\s\d{3}\s\d{3}\s\d{3}|\d{3}\s\d{3}\s\d{3,4}|\d{3}-\d{3}-\d{4}|\d{3}\s\d{3}\s\d{4}|\d{3}.\d{3}.\d{4}|\(\d{3}\)\d{3}[\s.-]\d{4}|\(\s?\d{2,3}\s?\)\s\d{3}[\s.-]\d{3,4}|\d{3}\s\d{4}\s\d{3}|\d{3}[-.\s]\d{4,7}|\d{7}|\(\d{3}\)\d{7}|\(\s\d{2}\s\)\s\d{7}|\+\d{2}\s\d{1,2}\s\d{3}\s\d{4}|\+\d{2}\s\d{1,2}\s\d{7,8}|\d{2}\s\d{4}\s\d{3}|\+\d{2}\s\d{9}|\d{2}\s\d{7}|\+\d{2}\s-\s\d{1}\s-\s\d{3}\s\d{4}|\+\d{2}\s\d{2}\s\d{4}\s\d{3}|\d{2}\s-\s\d{3}\s-\s\d{4}|\+\d{2}\s\(\s\d{1}\s\)\s\d{1}\s\d{3}\s\d{4}|\d{5}\s\d{4}|\+1\(\d{3}\)\-\d{3}\-\d{4}"),
                  "bullets": re.compile("^\d+(.|\)|\*)(\s)?"),
                  "waste_words": re.compile("e\.g|i\.e|\d{2}x\d|\d{2}\s[/x]\s\d(\s/\s\d{3})?"),
                  "big_numbers": re.compile("\d{1,3}\s,\s\d{3}(\+)?"),
                  "days": re.compile("(\d{2}\s\,\s)?((\d\.)?\d{1,2}\s(-|and|or|to)\s)?\d+ day(s)?", flags=re.IGNORECASE),
                  "months": re.compile("(\d\s\-\s)?\d+\s?(\s\-\s)?month(s|ly)?", flags=re.IGNORECASE),
                  "years": re.compile("(\d\s(\-|to)\s)?\d+(\+)?\syear(s|'s)?|\d+\s\-\syear(s|'s)?", flags=re.IGNORECASE),
                  "hours": re.compile("(\d+(\.\d)?\s(\-|to)\s+)?(\d+\.)?\d+(\s)?(per\s)?h(ours|our|rs|r)(\s(per|a|p|/)?(\s)?(/)?(\s)?(week|w\s|fortnight|day))?(\sshift(s)?)?", flags=re.IGNORECASE),
                  "weeks": re.compile("(\d+\s\-\s)?\d+\s(\-\s)?((a|per)\s)?week(s)?(\s(per)\s(year))?", flags=re.IGNORECASE),
                  "percentages": re.compile("(\d+\.)?\d+(\s)?%(\+)?"),
                  "dates": re.compile("\d{2}\-\d{2}\-\d{4}|\d{2}\/\d{4}|(\d{1,2}(th|rd)?\s)?(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|aug|sep|oct|nov|dec)(\s|'|-)(\d{1,2}th\s)?\d{2,4}"),
                  "tags": re.compile('<.*?>')}

contraction_mapping = {"ain't": "is not", "aren't": "are not", "can't": "cannot", "'cause": "because", "could've": "could have", "couldn't": "could not",
                       "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not",
                       "he'd": "he would", "he'll": "he will", "he's": "he is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", "how's": "how is",
                       "I'd": "I would", "I'd've": "I would have", "I'll": "I will", "I'll've": "I will have", "I'm": "I am", "I've": "I have", "i'd": "i would",
                       "i'd've": "i would have", "i'll": "i will", "i'll've": "i will have", "i'm": "i am", "i've": "i have", "isn't": "is not", "it'd": "it would",
                       "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have", "it's": "it is", "let's": "let us", "ma'am": "madam",
                       "mayn't": "may not", "might've": "might have", "mightn't": "might not", "mightn't've": "might not have", "must've": "must have",
                       "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have", "o'clock": "of the clock",
                       "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have",
                       "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have", "she's": "she is",
                       "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have", "so's": "so as",
                       "this's": "this is", "that'd": "that would", "that'd've": "that would have", "that's": "that is", "there'd": "there would",
                       "there'd've": "there would have", "there's": "there is", "here's": "here is", "they'd": "they would", "they'd've": "they would have",
                       "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have", "to've": "to have",
                       "wasn't": "was not", "we'd": "we would", "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are",
                       "we've": "we have", "weren't": "were not", "what'll": "what will", "what'll've": "what will have", "what're": "what are",
                       "what's": "what is", "what've": "what have", "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is",
                       "where've": "where have", "who'll": "who will", "who'll've": "who will have", "who's": "who is", "who've": "who have",
                       "why's": "why is", "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have",
                       "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all",
                       "y'all'd": "you all would", "y'all'd've": "you all would have", "y'all're": "you all are", "y'all've": "you all have",
                       "you'd": "you would", "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have",
                       "you're": "you are", "you've": "you have"}

generator_vocab = bson.decode_file_iter(gzip.open("./vocab/words.bson.gz", 'rb'))

vocab_information = {"stopWords": [],
                     "standardWords": {},
                     "vocab": [],
                     "rootForm": {},
                     "months": [],
                     "days": []}

for vocab_json in generator_vocab:
    vocab_information['vocab'].append(vocab_json['word'])
    if 'wordType' in vocab_json:
        if "stopword" in vocab_json['wordType']:
            vocab_information['stopWords'].append(vocab_json['word'])
        if 'month' in vocab_json['wordType']:
            vocab_information['months'].append(vocab_json['word'])
        if 'day' in vocab_json['wordType']:
            vocab_information['days'].append(vocab_json['word'])
        if 'standardWord' in vocab_json and 'skill' not in vocab_json['wordType']:
            vocab_information['standardWords'][vocab_json['word']] = vocab_json['standardWord']
    if 'wordRootForm' in vocab_json:
        vocab_information['rootForm'][vocab_json['word']] = vocab_json['wordRootForm']
