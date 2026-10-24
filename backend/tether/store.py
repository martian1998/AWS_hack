"""Serializable optimistic transactions shared by SQLite and DynamoDB adapters.

SQLite is a durable local development adapter, never represented as AWS evidence.
Each read in a decision is condition-checked at commit, including absent rows.
"""
import json
import sqlite3
import time
import random
from dataclasses import dataclass
from pathlib import Path

from botocore.exceptions import ClientError, BotoCoreError
from .errors import Conflict, StorageUnavailable

TABLES = ("Records", "Escalations", "Audit", "Work", "Control")


@dataclass
class Row:
    table: str
    pk: str
    sk: str
    data: dict
    version: int
    gpk: str | None = None
    gsk: str | None = None


class Transaction:
    def __init__(self, store):
        self.store = store
        self.reads = {}
        self.writes = {}

    def get(self, table, pk, sk="META"):
        key = (table, pk, sk)
        if key not in self.reads:
            self.reads[key] = self.store.get(*key)
        if key in self.writes:
            return self.writes[key]
        return self.reads[key]

    def put(self, table, pk, sk, data, gpk=None, gsk=None):
        key = (table, pk, sk)
        self.get(*key)
        original = self.reads[key]
        if table == "Audit" and original:
            raise ValueError("AUDIT_IMMUTABLE")
        self.writes[key] = Row(table, pk, sk, json.loads(json.dumps(data)),
                               (original.version if original else 0) + 1, gpk, gsk)


class Store:
    def run(self, operation, retries=8):
        for attempt in range(retries):
            tx = Transaction(self)
            result = operation(tx)
            try:
                self.commit(tx)
                return result
            except Conflict:
                if attempt + 1 == retries:
                    raise StorageUnavailable() from None
                time.sleep(random.uniform(0, min(0.005 * 2**attempt, .08)))


class SQLiteStore(Store):
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("CREATE TABLE IF NOT EXISTS items (collection TEXT, pk TEXT, sk TEXT, version INTEGER, data TEXT, gpk TEXT, gsk TEXT, PRIMARY KEY(collection,pk,sk))")
            con.execute("CREATE INDEX IF NOT EXISTS gsi1 ON items(collection,gpk,gsk)")
        self.fail_next_commit = False  # injected local/test failure; never an HTTP input

    def connect(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    @staticmethod
    def decode(row):
        return None if row is None else Row(row["collection"], row["pk"], row["sk"], json.loads(row["data"]), row["version"], row["gpk"], row["gsk"])

    def get(self, table, pk, sk="META"):
        with self.connect() as con:
            return self.decode(con.execute("SELECT * FROM items WHERE collection=? AND pk=? AND sk=?", (table, pk, sk)).fetchone())

    def query(self, table, partition, *, index=False, after="", until=None, limit=50):
        limit = min(max(limit, 1), 100)
        p, s = ("gpk", "gsk") if index else ("pk", "sk")
        sql = f"SELECT * FROM items WHERE collection=? AND {p}=? AND {s}>?"
        values = [table, partition, after]
        if until is not None:
            sql += f" AND {s}<=?"
            values.append(until)
        sql += f" ORDER BY {s} ASC LIMIT ?"
        values.append(limit)
        with self.connect() as con:
            return [self.decode(row) for row in con.execute(sql, values).fetchall()]

    def commit(self, tx):
        if len(tx.reads) > 100:
            raise ValueError("TRANSACTION_TOO_LARGE")
        with self.connect() as con:
            try:
                con.execute("BEGIN IMMEDIATE")
                for key, old in tx.reads.items():
                    current = con.execute("SELECT version FROM items WHERE collection=? AND pk=? AND sk=?", key).fetchone()
                    if (current[0] if current else None) != (old.version if old else None):
                        raise Conflict()
                if self.fail_next_commit:
                    self.fail_next_commit = False
                    raise StorageUnavailable()
                for row in tx.writes.values():
                    con.execute("INSERT INTO items VALUES (?,?,?,?,?,?,?) ON CONFLICT(collection,pk,sk) DO UPDATE SET version=excluded.version,data=excluded.data,gpk=excluded.gpk,gsk=excluded.gsk",
                                (row.table, row.pk, row.sk, row.version, json.dumps(row.data, ensure_ascii=False), row.gpk, row.gsk))
                con.commit()
            except (Conflict, StorageUnavailable):
                con.rollback()
                raise
            except sqlite3.Error:
                con.rollback()
                raise StorageUnavailable() from None


class DynamoStore(Store):
    def __init__(self, client, prefix):
        self.client, self.prefix = client, prefix

    def table(self, name):
        if name not in TABLES:
            raise ValueError("UNKNOWN_TABLE")
        return f"{self.prefix}-{name.lower()}"

    @staticmethod
    def decode(table, item):
        if not item:
            return None
        return Row(table, item["PK"]["S"], item["SK"]["S"], json.loads(item["data"]["S"]),
                   int(item["version"]["N"]), item.get("GSI1PK", {}).get("S"), item.get("GSI1SK", {}).get("S"))

    @staticmethod
    def encode(row):
        item = {"PK": {"S": row.pk}, "SK": {"S": row.sk}, "data": {"S": json.dumps(row.data, ensure_ascii=False)}, "version": {"N": str(row.version)}}
        if row.gpk is not None and row.gsk is not None:
            item.update(GSI1PK={"S": row.gpk}, GSI1SK={"S": row.gsk})
        return item

    def get(self, table, pk, sk="META"):
        try:
            result = self.client.get_item(TableName=self.table(table), Key={"PK": {"S": pk}, "SK": {"S": sk}}, ConsistentRead=True)
            return self.decode(table, result.get("Item"))
        except (ClientError, BotoCoreError):
            raise StorageUnavailable() from None

    def query(self, table, partition, *, index=False, after="", until=None, limit=50):
        names = {"#p": "GSI1PK" if index else "PK", "#s": "GSI1SK" if index else "SK"}
        values = {":p": {"S": partition}, ":after": {"S": after}}
        expression = "#p = :p AND #s > :after"
        # DynamoDB allows only one sort-key predicate. A bounded range is expressed with BETWEEN.
        if until is not None:
            values[":after"] = {"S": after + "\x01"}
            values[":until"] = {"S": until}
            expression = "#p = :p AND #s BETWEEN :after AND :until"
        args = dict(TableName=self.table(table), KeyConditionExpression=expression,
                    ExpressionAttributeNames=names, ExpressionAttributeValues=values, Limit=min(max(limit, 1), 100))
        if index:
            args["IndexName"] = "GSI1"
        else:
            args["ConsistentRead"] = True
        try:
            return [self.decode(table, item) for item in self.client.query(**args).get("Items", [])]
        except (ClientError, BotoCoreError):
            raise StorageUnavailable() from None

    def commit(self, tx):
        operations = []
        for key, old in tx.reads.items():
            table, pk, sk = key
            condition = {"ConditionExpression": "#v = :v", "ExpressionAttributeNames": {"#v": "version"}, "ExpressionAttributeValues": {":v": {"N": str(old.version)}}} if old else {"ConditionExpression": "attribute_not_exists(PK)"}
            common = {"TableName": self.table(table), **condition}
            if key in tx.writes:
                operations.append({"Put": {**common, "Item": self.encode(tx.writes[key])}})
            else:
                operations.append({"ConditionCheck": {**common, "Key": {"PK": {"S": pk}, "SK": {"S": sk}}}})
        if not operations:
            return
        if len(operations) > 100:
            raise ValueError("TRANSACTION_TOO_LARGE")
        try:
            self.client.transact_write_items(TransactItems=operations)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            reasons = {r.get("Code") for r in exc.response.get("CancellationReasons", [])}
            if code == "TransactionConflictException" or (code == "TransactionCanceledException" and reasons <= {"None", "ConditionalCheckFailed", "TransactionConflict"}):
                raise Conflict() from None
            raise StorageUnavailable() from None
        except BotoCoreError:
            raise StorageUnavailable() from None
