import configparser
import os

from jinja2 import Environment, FileSystemLoader

from history_reader.skype import History, MSG_TYPES

config = configparser.ConfigParser()
config.read('config.ini')


def main():
    history = History(db_path=config['SKYPE']['db_path'])
    messages = history.get_chat_history(config['SKYPE']['chat_id'])
    render(messages)


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

if __name__ == '__main__':
    main()
