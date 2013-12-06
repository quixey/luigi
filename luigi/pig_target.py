from luigi.s3 import S3Target


class PigTarget():
    def __init__(self, path, s3_client, addSuccess=True):
        self.path = path
        if addSuccess:
            self.path += '/_SUCCESS'
        self.s3_client = s3_client

    def exists(self):
        return self.s3_client.exists(self.path)

    def create(self):
        S3Target(self.path, self.s3_client).open('w').close()
