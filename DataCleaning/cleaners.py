import helpers
import html.parser
from string import punctuation
import re


class TextCleaners:
    @staticmethod
    def escaping_html_chars(text):
        html_parser = html.parser.HTMLParser()
        parsed_text = html_parser.unescape(text)
        return parsed_text

    def remove_html_tags(self, text):
        cleantext = re.sub(helpers.regex_mappings['tags'], '', text)
        return cleantext

    @staticmethod
    def decode_text(text):
        decoded_text = text.encode('ascii', 'ignore').decode('utf-8')
        return str(decoded_text)

    @staticmethod
    def normalize_punctuations(text):
        for each_punctuation in punctuation:
            if each_punctuation not in ['.']:
                text = text.replace(each_punctuation, " " + each_punctuation + " ")
        text = re.sub(('\s\s+'), " ", text)
        return text

    @staticmethod
    def replace_apostrophes_and_standardize_words(text):
        temp = []
        for word in text.split():
            word = word.replace("’", "'")
            if word.strip().strip(punctuation).strip() in helpers.vocab_information['standardWords']:
                temp.append(helpers.vocab_information['standardWords'][word.strip().strip(punctuation).strip()])
            elif word.strip().strip(punctuation).strip() in helpers.contraction_mapping:
                temp.append(helpers.contraction_mapping[word.strip().strip(punctuation).strip()])
            else:
                temp.append(word)
        normalized_text = ' '.join(temp)
        normalized_text = normalized_text.replace("'s", "")
        return normalized_text

    @staticmethod
    def replace_urls_emails(text):
        urls_emails_removed_text = re.sub(helpers.regex_mappings['website'], "WEBSITE", text)
        urls_emails_removed_text = ' '.join([word if "@" not in word else "URL" for word in urls_emails_removed_text.split()])
        return urls_emails_removed_text

    @staticmethod
    def remove_punctuations_and_expressions(text):
        normalize_punctuations = ' '.join([word.lstrip(punctuation.replace(".", "")).rstrip(punctuation).strip() for word in text.split() if word not in punctuation])
        normalize_punctuations = ' '.join([re.sub("[{" + punctuation.replace("-", "").replace(".", "") + "}]", " ", word) for word in normalize_punctuations.split()])
        return normalize_punctuations

    @staticmethod
    def remove_text_inside_parenthesis(text):
        text = re.sub(r'\([^)]*\)', '', text)
        return text

    @staticmethod
    def normalize_slang_words(text):  # todo
        return text

    @staticmethod
    def remove_noisy_text(text):
        check_stop_word_count = [word for word in text.strip().split() if word in helpers.vocab_information['stopWords'] + ['-pron-']]
        check_stop_word_count_two = [word for word in text.strip().split(":")[-1].split() if word in helpers.vocab_information['stopWords'] + ['-pron-']]
        text = text if len(check_stop_word_count) > 0 and len(check_stop_word_count_two) > 0 and text.strip().split()[-1] not in helpers.vocab_information['stopWords'] + ['-pron-'] else ""
        text = text if text.strip() not in helpers.vocab_information['stopWords'] + ['-pron-'] else ""
        return text

    @staticmethod
    def remove_stopwords(text):
        # stopwords_removed_text = ' '.join([word for word in text.split() if word not in helpers.vocab_information['stopWords'] + ['-pron-']])
        stopwords_removed_text = ' '.join([word if word not in helpers.vocab_information['stopWords'] + ['-pron-'] else "STOPWORD" for word in text.split()])
        return stopwords_removed_text

    @staticmethod
    def root_word_transform(text):
        transformed_text = ' '.join([helpers.vocab_information['rootForm'][word.strip()] if word.strip() in helpers.vocab_information['rootForm'] else word for word in text.split()])
        return transformed_text

    @staticmethod
    def remove_bullets(text_bullets):
        bullets_removed = re.sub(helpers.regex_mappings['bullets'], "", text_bullets)
        return bullets_removed

    @staticmethod
    def replace_numbers(text):

        def remove_durations(text_yoe):
            durations_removed = text_yoe
            for each_match in re.findall(helpers.regex_mappings['duration'], text_yoe):
                if " " + each_match + " " in text_yoe.strip(punctuation).strip() + " ":
                    durations_removed = re.sub(helpers.regex_mappings['duration'], "DURATION", text_yoe)
            return durations_removed

        def remove_dates(text_date):
            dates_removed = re.sub(helpers.regex_mappings['dates'], "DATE", text_date)
            return dates_removed

        def remove_timing(text_time):
            jt_removed = re.sub(helpers.regex_mappings['timings'], "TIMINGS", text_time)
            return jt_removed

        def remove_money(text_money):
            # print(text_money)
            # print(re.findall(self.money_pattern, text_money))
            money_removed = re.sub(helpers.regex_mappings['money'], "MONEY", text_money)
            return money_removed

        def remove_days_years(text_days):
            temp = []
            temp_days = " ".join([w.strip().strip(punctuation).strip() if w not in punctuation else w for w in text_days.split()])
            for word_index, word in enumerate(text_days.split()):
                # print(word_index, word, word[0].isnumeric(), temp_days.lower().split()[word_index:word_index + 3], "+++", temp_days.lower().split()[:word_index][::-1][0:2])
                if word[0].isnumeric() and set(helpers.vocab_information['months']) & set(temp_days.lower().split()[word_index:word_index + 3]):
                    temp.append("MONTH")
                elif word[0].isnumeric() and set(helpers.vocab_information['months']) & set(temp_days.lower().split()[:word_index][::-1][0:2]):
                    temp.append("MONTH")
                else:
                    temp.append(word)
            return " ".join(temp)

        def remove_phone_num(text_pho_num):
            phone_num_removed = ""
            for each_match in re.findall(helpers.regex_mappings['phone'], text_pho_num):
                if " " + each_match in text_pho_num:
                    phone_num_removed = re.sub(helpers.regex_mappings['phone'], "PHONENUM", text_pho_num)
            extra_num_removed = phone_num_removed.split() if phone_num_removed else text_pho_num.split()
            for pnr_index, pnr in enumerate(extra_num_removed):
                if pnr[0].isnumeric() and ("PHONENUM" in extra_num_removed[pnr_index + 1:pnr_index + 3] or "PHONENUM" in extra_num_removed[:pnr_index][::-1][0:2]):
                    # extra_num_removed[pnr_index] = "extraphonenum"
                    extra_num_removed[pnr_index] = ""
                elif pnr != "PHONENUM" and pnr.startswith("PHONENUM"):
                    extra_num_removed[pnr_index] = ""

            # return " ".join(extra_num_removed).replace("phonenum", "")
            return " ".join(extra_num_removed)

        def remove_big_numbers(text_big_num):
            big_numbers_removed = re.sub(helpers.regex_mappings['big_numbers'], "BIGNUM", text_big_num)
            return big_numbers_removed

        def remove_percentages(text_percent):
            percentages_removed = re.sub(helpers.regex_mappings['percentages'], "PERCENTAGE", text_percent)
            return percentages_removed

        removed_numbers = remove_durations(text)
        removed_numbers = remove_timing(removed_numbers)
        removed_numbers = remove_money(removed_numbers)
        removed_numbers = remove_dates(removed_numbers)
        # removed_numbers = remove_days_years(removed_numbers) # todo: need to check
        removed_numbers = remove_phone_num(removed_numbers)
        removed_numbers = remove_big_numbers(removed_numbers)
        removed_numbers = remove_percentages(removed_numbers)

        # removed_numbers = ' '.join([word for word in text.split() if not word.strip(punctuation).strip().isnumeric()])
        # removed_numbers = re.sub('(\d\w+|\d+)', "", text)
        return removed_numbers

    def remove_dates(self, text):
        pass

    @staticmethod
    def split_joined_sentences(text):
        text_split = ' '.join([word.replace(".", ". ") if re.findall('([a-z]+\.[A-Z]+)', word) else word for word in text.split()])
        return text_split

    @staticmethod
    def remove_waste_words(text):
        waste_words_removed = re.sub(helpers.regex_mappings['waste_words'], "WASTEWORDS", text)
        return waste_words_removed


if __name__ == '__main__':
    obj = TextCleaners()

    print(obj.escaping_html_chars("""'<p>I\'m already &amp; familiar with repeating tasks every n seconds by using Java.util.Timer and Java.util.TimerTask. But lets say I want to print "Hello World" to the console every random seconds from 1-5. Unfortunately I\'m in a bit of a rush and don\'t have any code to show so far. Any help would be apriciated.  </p>'"""))
