class ParsingFailureException(Exception):
    content = None

    def __init__(self, content: str, id: str):
        self.content = content
        self.id = id

    def __str__(self):
        return f"Failure at {self.id} while parsing the content: {self.content}"