class DownloadException(Exception):

    def __init__(self, file_name: str, error, url: str):
        self.file_name = file_name
        self.error = error
        self.url = url

    def __str__(self):
        return f"Failure when downloading {self.file_name}. Error: {self.error}. Source: {self.url}"