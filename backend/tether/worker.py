"""Inert Stage A handler: unfinished records are never acknowledged as complete."""


def handler(event, context):
    return {"batchItemFailures": [{"itemIdentifier": record["messageId"]}
                                  for record in event.get("Records", [])]}
