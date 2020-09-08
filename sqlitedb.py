import sqlite3


class DB(object):
    def __init__(self, config):
        self.conn = sqlite3.connect(config['host'])
        self.cur = self.conn.cursor()

        for stament in config['tables']:
            print(stament)
            self.cur.execute(stament)
    
    def close(self):
        self.cur.close()

    def commit(self):
        self.conn.commit()
    
    def execute(self, stament):
        self.cur.execute(stament)

    def executes(self, staments):
        for stament in staments:
            self.cur.execute(stament)

    def select(self, stament, rtntype):
        self.cur.execute(stament)
        if rtntype == "one":
            return self.cur.fetchone()
        elif rtntype == "all":
            return self.cur.fetchall()

