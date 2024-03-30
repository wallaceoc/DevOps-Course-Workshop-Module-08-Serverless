import logging
import json

from azure.functions import QueueMessage


def main(msg: QueueMessage, translationTable) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    message = json.loads(translationTable)
