class InvalidContentException(Exception):

    content = None
    url = None

    def __init__(self, url:str, content):
        if content is not None and len(content) > 500:
            self.content = content[0:500]
        else:
            self.content = content
        self.url = url

    def __str__(self):
        return f"Invalid content at {self.url}: {self.content}"





