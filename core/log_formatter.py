import logging


class EmojiFormatter(logging.Formatter):
    LEVEL_EMOJIS = {
        'DEBUG':    '🔍',
        'INFO':     '📋',
        'WARNING':  '⚠️ ',
        'ERROR':    '❌',
        'CRITICAL': '🔥',
    }

    def format(self, record):
        record.emoji = self.LEVEL_EMOJIS.get(record.levelname, '📋')
        return super().format(record)
