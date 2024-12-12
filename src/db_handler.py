from pymongo import MongoClient


class MongoDB:
    def __init__(self, db_name, db_adr=''):
        if db_adr:
            self.db = MongoClient(db_adr)[db_name]
        else:
            self.db = MongoClient()[db_name]

    def read_one(self, col_name, query, sort_by=''):
        if sort_by:
            ret = self.db[col_name].find_one(query, {'_id': False}).sort([(sort_by, -1)])
        else:
            ret = self.db[col_name].find_one(query, {'_id': False})
        if not ret:
            ret = {}
        return ret

    def read_all(self, col_name, query, sort_by=''):
        if sort_by:
            ret = self.db[col_name].find(query, {'_id': False}).sort([(sort_by, -1)])
        else:
            ret = self.db[col_name].find(query, {'_id': False})
        if not ret:
            ret = []
        return ret

    def write(self,col_name, doc):
        self.db[col_name].insert_one(doc)

    def update_one(self,col_name, key, doc, opr='$set', upsert=False):
        self.db[col_name].update_one(key, {opr : doc}, upsert=upsert)
