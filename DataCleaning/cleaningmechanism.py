from cleaners import TextCleaners
from advancedcleaners import AdvancedTextCleaners


class CleaningMechanism:

    def __init__(self):
        self.text_cleaners = TextCleaners()
        self.advanced_text_cleaners = AdvancedTextCleaners()

    def cleaner_for_embeddings(self, text, perform_on_sentences, word_embeddings, phrase_embeddings):
        # todo: work on remove_noisy_text
        text = self.cleaner_for_common_tasks(text)
        text = self.text_cleaners.remove_noisy_text(text) if perform_on_sentences else text
        text = self.text_cleaners.replace_apostrophes_and_standardize_words(text)
        if word_embeddings and phrase_embeddings is False:
            text = self.text_cleaners.remove_stopwords(text)
        text = self.text_cleaners.replace_numbers(text.lower())
        text = self.text_cleaners.remove_bullets(text)
        text = self.text_cleaners.normalize_punctuations(text)
        text = self.text_cleaners.remove_punctuations_and_expressions(text)
        if phrase_embeddings:
            phrases = self.advanced_text_cleaners.form_phrases(text)
            if not phrases:
                phrases = [text]
            return phrases
        else:
            return text

    def cleaner_for_named_entity_recognition(self, text):
        text = self.cleaner_for_common_tasks(text)
        text = self.text_cleaners.remove_stopwords(text)
        return text

    def cleaner_for_text_summarization(self, text):
        text = self.cleaner_for_common_tasks(text.lower())
        text = self.text_cleaners.remove_text_inside_parenthesis(text)
        text = self.text_cleaners.replace_apostrophes_and_standardize_words(text)
        text = self.text_cleaners.remove_punctuations_and_expressions(text)
        text = self.text_cleaners.remove_stopwords(text)
        # Remove short words
        return text

    def cleaner_for_text_classification(self, text):
        text = self.cleaner_for_common_tasks(text.lower())
        text = self.text_cleaners.replace_numbers(text)
        text = self.text_cleaners.remove_stopwords(text)
        return text

    def cleaner_for_text_generation(self, text):
        text = self.cleaner_for_common_tasks(text)
        return text

    def cleaner_for_common_tasks(self, text):
        text = self.text_cleaners.escaping_html_chars(text)
        text = self.text_cleaners.decode_text(text)
        text = self.text_cleaners.split_joined_sentences(text)
        text = self.text_cleaners.replace_urls_emails(text)
        return text
