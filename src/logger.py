from datetime import datetime


class Log:
    def __init__(self, file_name):
        self.dir = 'logs/{}.txt'.format(file_name)
        self.ts_format = '%Y-%m-%d %H:%M:%S'

    def write(self, log):
        ts = datetime.now().strftime(self.ts_format)
        with open(self.dir, 'w') as lf:
            lf.write('{} : {}'.format(ts, log))
