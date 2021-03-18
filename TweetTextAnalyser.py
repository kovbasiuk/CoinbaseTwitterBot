from nltk import ngrams
from nltk.tokenize import sent_tokenize

from strsimpy import SIFT4
import logging as logger

# used for analysing the tweet in comparison the valid questions/strings
class TweetTextAnalyser:

    def analyse(self, tweet_text, valid_questions, currency_keywords):

        tweet_text = self.removed_currency_keywords(tweet_text, currency_keywords)
        # tokenization
        sent_tokens = sent_tokenize(tweet_text)
        logger.info(f'Analysing tweet: {tweet_text}')
        for i in sent_tokens:
            for j in valid_questions:
                print(f'sent_tokens: {i}')
                print(f'valid_questions: {j}')

                # num of words in the valid question
                num_of_words = len(j.split())
                token_ngrams = self.ngram(num_of_words, i)
                for x in token_ngrams:
                    # print(compare_text(tweet_text,valid_questions[j]))
                    filtered_x = self.removed_symbols(x)
                    if self.compare_text(filtered_x.lower(), j.lower()):
                        print('Match found!')
                        return True

        return False

    # compares the similarity of two texts currently using sift4 algorithm
    def compare_text(self, temp, valid_question):
        s = SIFT4()
        result = s.distance(temp, valid_question)
        max_difference = 10
        return result < max_difference

    # gets ngrams based on a certain length, in this case the length of the comparison text
    def ngram(self, n: int, sentence: str):

        grams = ngrams(sentence.split(), n)

        sentences = []
        for gram in grams:
            #print(f'gram: {gram}')
            sentences.append(' '.join(gram))

        return sentences

    #move to a custom utils class
    def removed_symbols(self, text):

        # checks ascii values then joins if char satisfies condition
        return ''.join(i if ord(i) < 33 or ord(i) > 65 and ord(i) < 122 else '' for i in text).replace('\n', '')

    # filter out any currency keywords as this is comparing the question/query which may contain multiple currency keywords
    def removed_currency_keywords(self, text, currency_keywords):
        text_words = text.split()
        resultwords = [word for word in text_words if word.lower() not in currency_keywords]
        return ' '.join(resultwords)
