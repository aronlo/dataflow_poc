import psycopg2

class Database():
    def __init__(self, dbname='postgres', user='postgres', password='secret', host='localhost'):
        self._dbname= dbname
        self._user = user
        self._password = password
        self._host = host

    def get_conn(self):
        return psycopg2.connect(
        dbname=self._dbname, 
        user=self._user, 
        password=self._password,
        host=self._host)
