import logging

logger = logging.getLogger('msgcenter')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
