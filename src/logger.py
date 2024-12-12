from datetime import datetime
import csv


class Log:
    def __init__(self, file_name):
        self.dir = 'logs/{}.txt'.format(file_name)
        self.ts_format = '%Y-%m-%d %H:%M:%S'

    def write(self, log, user='PRG'):
        ts = datetime.now().strftime(self.ts_format)
        with open(self.dir, 'a', encoding='utf8', newline='') as lf:
            writer = csv.writer(lf)
            writer.writerow([ts, user, log])
