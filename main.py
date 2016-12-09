import click
import configparser
import html
import nltk
import os
import pymorphy2
import re
import string

from jinja2 import Environment, FileSystemLoader
from nltk.corpus import stopwords

from history_reader.skype import History, MSG_TYPES

config = configparser.ConfigParser()
config.read('config.ini')

more_stop_words = ['...', "''", '``', 'https', 'http']
unchanged_words = []
similar_unchanged_words = {
    # ('бабло', 'бабла'): 'бабло',
}


@click.command()
def main():
    history = History(db_path=config['SKYPE']['db_path'])
    messages = history.get_chat_history(config['SKYPE']['chat_id'])
    words_frequency(messages)
    # render(messages)


def render(messages):
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template('template.html')

    with open('index.html', 'w') as output:
        context = {
            'messages': messages,
            'MSG_TYPES': MSG_TYPES
        }
        output.write(template.render(**context))

    print('Open index.html to see result.')


def words_frequency(messages):
    TAG_RE = re.compile(r'<[^>]+>')
    TAG_QUOTE_RE = re.compile(r'<quote.*?>.*</quote>')
    stop_words = stopwords.words('russian')
    stop_words.extend(more_stop_words)
    fdist = nltk.FreqDist()
    morph = pymorphy2.MorphAnalyzer()

    with click.progressbar(messages) as data:
        for msg_obj in data:
            if not msg_obj['body_xml']:
                continue

            # FIXME: Remove URLs
            msg = TAG_QUOTE_RE.sub('', msg_obj['body_xml'].replace('\n', ''))
            msg = TAG_RE.sub('', msg)
            msg = html.unescape(msg)
            tokens = nltk.word_tokenize(msg)
            words = []

            for token in tokens:
                # skip punctuation
                if token in string.punctuation:
                    continue

                # combine similar worlds from custom dictionary
                if token in unchanged_words:
                    word = token
                    for key, value in similar_unchanged_words.items():
                        if token in key:
                            word = value
                            break
                else:
                    parsed = morph.parse(token)[0]
                    word = parsed.normal_form

                    if len(word) <= 2 or word in stop_words:
                        continue

                    if parsed.tag.POS in ('NPRO', 'PRCL', 'INTJ'):
                        continue

                words.append(word)

            fdist.update(words)

    for word, frequency in fdist.most_common(100):
        print(word, frequency)

if __name__ == '__main__':
    main()
