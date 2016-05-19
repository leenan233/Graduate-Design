import MySQLdb



database = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent', unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889)
PatentDB = database
class DBConnection:
    def connect(self):  
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='Patent',
                                   unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', port=8889 )
      
    def execute(self, sql):  
        try:  
            cursor = self.conn.cursor()  
            cursor.execute(sql)  
        except (AttributeError, MySQLdb.OperationalError):  
            self.connect()  
            cursor = self.conn.cursor()  
            cursor.execute(sql)  
        return cursor  
    
    def close(self):  
        if(self.cursor):  
            self.cursor.close()  
            self.conn.commit()  
            self.conn.close()  