import json
import os
from time import sleep
from urllib.request import urlopen, urlretrieve

class Fetcher(object):
    """The main class of the image fetcher"""
    def __init__(self, board="wg"):
        self.board = board 
        self.threads = []
    
    def json_parser(self, url):
        response = urlopen(url)
        data = response.read().decode("utf-8")
        parsed = json.loads(data)
        return parsed
    
    def get_threads(self): 
        """Gets all of the thread ID's from the board"""
        threads_json = "http://a.4cdn.org/{}/threads.json".format(self.board)
        parsed = self.json_parser(threads_json)
        for page in parsed:
            for thread in page["threads"]:
                # Reads thread ID from official 4chan api
                self.threads.append(thread["no"])

    def thread_analyzer(self):
        """Analyzes all of the threads"""
        thread_json = "http://a.4cdn.org/{}/thread/{}.json"
        for thread in self.threads:
            # Reads thread info from official 4chan API
            parsed = self.json_parser(thread_json.format(self.board, thread))
            title = "thread_{}".format(thread)
            try:
                subject = parsed["posts"][0]["sub"]
                subject = subject.replace("/", "")
                print(subject)
            except KeyError:
                subject = None
            for post in parsed["posts"]:
                try:
                    image = {
                            "url": post["tim"],
                            "width": post["w"],
                            "height": post["h"],
                            "name": post["filename"],
                            "ext": post["ext"]
                            }
                except KeyError:
                    pass
                self.image_downloader(image, title, subject)
            sleep(1) 

    def image_downloader(self, image, folder, real_title=None):
        """Downloads image if w >= 1920 and h >= 1080"""
        width, height = image["width"], image["height"]
        # Keeps backup if the subject name doesn't work with folder
        if real_title:
            prev = folder
            folder = real_title
        if width >= 1920 and height >= 1080 and width >= height:
            filename = "{}{}".format(image["url"], image["ext"])
            full_url = "http://i.4cdn.org/{}/{}".format(self.board, filename)
            try:
                full_filename = os.path.join(folder, filename) 
                if not os.path.exists(folder):
                    os.mkdir(folder)
            except:
                folder = prev
                full_filename = os.path.join(folder, filename) 
                if not os.path.exists(folder):
                    os.mkdir(folder)
            if not os.path.exists(full_filename):
                print("Downloading: {}".format(full_filename))
                urlretrieve(full_url, full_filename)
        
if __name__ == '__main__':
    f = Fetcher("wg")
    f.get_threads()
    f.thread_analyzer()
