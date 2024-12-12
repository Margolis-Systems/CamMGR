import main
from src import logger

log = logger.Log('audio_handler')


def init_ac():
    audio = []
    audio_conf = main.mongo.read_all('settings', {'audio': {'$exists': True}})
    for a in audio_conf:
        log.write('init: {}'.format(a['audio']['source']))
        # audio.append()
    return audio


def audio_record():
    return
