from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta


class CouchbaseClient(object):

    def __init__(self) -> None:
        self.cluster = None
        self.bucket = None
        self.scope = None

    def init_app(self, conn_str: str, username: str, password: str):
        self.conn_str = conn_str
        self.bucket_name = "travel-sample"
        self.scope_name = "inventory"
        self.username = username
        self.password = password
        self.connect()

    def connect(self) -> None:
        if not self.cluster:
            try:
                auth = PasswordAuthenticator(self.username, self.password)
                cluster_opts = ClusterOptions(auth)
                cluster_opts.kv_timeout = timedelta(milliseconds=10000)
                cluster_opts.query_timeout = timedelta(milliseconds=10000)
                cluster_opts.apply_profile("wan_development")
                self.cluster = Cluster(self.conn_str, cluster_opts)
                self.cluster.wait_until_ready(timedelta(seconds=5))
                self.bucket = self.cluster.bucket(self.bucket_name)
            except CouchbaseException as error:
                print(f"Could not connect to cluster. \nError: {error}")
                exit()

            if not self.check_scope_exists():
                print("Inventory scope does not exist in the bucket.")
                exit()

            self.scope = self.bucket.scope(self.scope_name)

    def check_scope_exists(self) -> bool:
        try:
            scopes_in_bucket = [
                scope.name for scope in self.bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print("Error fetching scopes in cluster.")
            exit()

    def get_document(self, collection_name: str, key: str):
        return self.scope.collection(collection_name).get(key)

    def insert_document(self, collection_name: str, key: str, doc: dict):
        self.bucket.default_collection().insert(key, doc)
        self.scope.collection(collection_name).insert(key, doc)

    def delete_document(self, collection_name: str, key: str):
        return self.scope.collection(collection_name).remove(key)

    def upsert_document(self, collection_name: str, key: str, doc: dict):
        return self.scope.collection(collection_name).upsert(key, doc)

    def query(self, sql_query, *options, **kwargs):
        return self.scope.query(sql_query, *options, **kwargs)
