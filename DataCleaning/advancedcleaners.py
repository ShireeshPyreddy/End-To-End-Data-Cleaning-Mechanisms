import helpers
from string import punctuation
import re
from math import log
from formphrases import generate_phrases


class AdvancedTextCleaners:

    def __init__(self):
        self.word_cost = dict((k, log((i + 1) * log(len(helpers.vocab_information['vocab'])))) for i, k in enumerate(helpers.vocab_information['vocab']))
        self.max_word = max(len(x) for x in helpers.vocab_information['vocab'])

    @staticmethod
    def spelling_correction(text):  # todo
        return text

    @staticmethod
    def join_split_words(text):  # todo

        def check_word(s):
            if s.lower().strip() in helpers.vocab_information['vocab']:
                return True
            else:
                return False

        temp, joined_text = [], []
        for t in text.split():
            if t not in punctuation:
                if t.lower().rstrip(".").strip() not in helpers.vocab_information['vocab']:
                    print("not in:::", t)
                    temp.append(t)
                    flag = check_word("".join(temp))
                    if flag is True:
                        print("joined word:::::::", "".join(temp))
                        joined_text.append("".join(temp))
                        temp = []
                else:
                    temp.append(t)
                    flag = check_word("".join(temp))
                    if flag is True:
                        print("joined word:::::::", "".join(temp))
                        joined_text.append("".join(temp))
                        temp = []
                    # print("".join(temp))
                    # temp = []
                    # print("++++++++++", t)
                    # if len(t.rstrip(".").strip()) == 1:
                    #      temp.append(t)
                    # else:
                    #     joined_text.append(t)
            else:
                temp = []
                joined_text.append(t)

        return " ".join(joined_text)

    def split_joined_words(self, text):  # todo
        def split(s):
            # l = [_split(s)]
            _SPLIT_RE = re.compile("[^a-zA-Z0-9']+")
            l = [_split(x) for x in _SPLIT_RE.split(s)]
            return [item for sublist in l for item in sublist]

        def _split(s):
            out = []

            def best_match(i):
                candidates = enumerate(reversed(cost[max(0, i - self.max_word):i]))
                return min((c + self.word_cost.get(s[i - k - 1:i].lower(), 9e999), k + 1) for k, c in candidates)

            cost = [0]
            for i in range(1, len(s) + 1):
                c, k = best_match(i)
                cost.append(c)
            i = len(s)
            while i > 0:
                c, k = best_match(i)
                assert c == cost[i]
                new_token = True
                if not s[i - k:i] == "'":
                    if len(out) > 0:
                        if out[-1] == "'s" or (s[i - 1].isdigit() and out[-1][0].isdigit()):
                            out[-1] = s[i - k:i] + out[-1]
                            new_token = False
                if new_token:
                    out.append(s[i - k:i])
                i -= k
            # print("+++++++++", out)
            return reversed(out)

        split_text = ' '.join([w for word in text.split() for w in split(word)])
        # split_text = split(text.replace(" ", ""))
        return split_text

    @staticmethod
    def grammar_correction(text):  # todo
        return text

    @staticmethod
    def form_phrases(text):
        def check_phrase(phrase):
            # print(helpers.vocab_information['stopWords'])
            if phrase.strip() and phrase.lower().strip() not in helpers.vocab_information['stopWords'] + ['-pron-'] and not phrase.isnumeric() and ".com" not in phrase and "https" not in phrase:
                return phrase
            else:
                return ""

        phrases = [each_phrase.lower().strip().strip(punctuation).strip() for each_phrase in generate_phrases(text, helpers.vocab_information['stopWords']) if check_phrase(each_phrase).strip()]

        return phrases
