import requests


class Amazon():
    def __init__(self):
        """ initialise the Amazon class default parameters """
        self.url = "https://www.amazon.com/"
        self.session = requests.session()

    def login(self, username, password):
        """ login to amazon.com with params username & password """
        print(self.url)
        home = self.session.get(self.url)
        print(home.text)


if __name__ == '__main__':
    a = Amazon()
    a.login('test', 'test')
