import logging
import time
import uuid
import json
import typing
import azure.functions as func


def main(request: func.HttpRequest, translation: func.Out[str], translationQ: func.Out[typing.List[str]]) -> func.HttpResponse:
    logging.info('HTTP trigger function received a request.')
    start = time.time()

    req_body = request.get_json()
    subtitle = req_body.get("subtitle")
    languages = req_body.get("languages")

    rowKey = str(uuid.uuid4())
    tableData = {
        "Name": subtitle,
        "PartitionKey": "translation",
        "RowKey": rowKey,
        "languages": languages
    }

    languageList = []

    for language in languages:                
        queueData = {
            "rowKey": rowKey,
            "languageCode": language
        }
        languageList.append(json.dumps(queueData))

    translationQ.set(languageList)
    translation.set(json.dumps(tableData))

    end = time.time()
    processingTime = end - start

    return func.HttpResponse(
        f"Processing took {str(processingTime)} seconds. Translation is: {subtitle}. With RowKey: {rowKey}",
        status_code=200
    )
