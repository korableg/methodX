
import sqlite3
import os

class Settings:
    
    class DBConnector:
        
        def __init__(self, path: str):
        
            if not os.path.exists(path):
                os.makedirs(path, 0o644)
            
            self.Connection = sqlite3.connect(path + "settings.db")
            self.Cursor = self.Connection.cursor()

            self.Cursor.execute("CREATE TABLE IF NOT EXISTS parameters ( name TEXT NOT NULL UNIQUE, value TEXT NOT NULL, PRIMARY KEY(name) )")
            self.Cursor.execute("CREATE TABLE IF NOT EXISTS vms ( ipAddress TEXT NOT NULL UNIQUE, PRIMARY KEY(ipAddress) )")
            self.Cursor.execute("CREATE TABLE IF NOT EXISTS phoneNumbers ( number TEXT NOT NULL UNIQUE, PRIMARY KEY(number) )")

            self.Cursor.execute("INSERT OR IGNORE INTO parameters (name, value) VALUES ('port', '1812')")
            self.Cursor.execute("INSERT OR IGNORE INTO parameters (name, value) VALUES ('secret', 'Tp0G*B@geqLPuda~0BLAmxaba4IuSFkYqTX*1mWTEv*{LDuF8l')")
            self.Cursor.execute("INSERT OR IGNORE INTO parameters (name, value) VALUES ('testSecret', 'Qwerty123')")

            self.Connection.commit()
    
    def __init__(self, path: str):

        self.Path         = path + "/etc/methodX/"
        self.__db         = self.DBConnector(self.Path)
        self.__port       = int(self.__getParameterFromDB("port"))
        

    def __getParameterFromDB(self, name):
        self.__db.Cursor.execute("SELECT value FROM parameters WHERE name= ? LIMIT 1", (name,))
        dbRow = self.__db.Cursor.fetchone()

        if dbRow != None:
            return dbRow[0]

        return None

    def __getVMSFromDB(self):
        vms = []
        self.__db.Cursor.execute("SELECT ipAddress FROM vms")
        dbRows = self.__db.Cursor.fetchall()
        for dbRow in dbRows:
            vms.append(dbRow[0])
        
        return tuple(vms)

    def __getPhonesFromDB(self):
        phoneNumbers = []
        self.__db.Cursor.execute("SELECT number FROM phoneNumbers")
        dbRows = self.__db.Cursor.fetchall()
        for dbRow in dbRows:
            phoneNumbers.append(dbRow[0])
        
        return tuple(phoneNumbers)

    def _getPort(self):
        return self.__port

    def _getSecret(self):
        return self.__getParameterFromDB("secret")

    def _getTestSecret(self):
        return self.__getParameterFromDB("testSecret")

    def _getVMS(self):
        return self.__getVMSFromDB()
    
    def _getPhones(self):
        return self.__getPhonesFromDB()

    def Check(self):
        if self.Port == 0:
            raise Exception("Port = 0")
        if len(self.Secret) == 0:
            raise Exception("Secret is not defined")
        if len(self.TestSecret) == 0:
            raise Exception("Test Secret is not defined")
        #if len(self.VMS) == 0:
        #    raise Exception("VMS is not defined")
        #if len(self.Phones) == 0:
        #    raise Exception("Phones is not defined")

    Port = property(_getPort)
    Secret = property(_getSecret)
    TestSecret = property(_getTestSecret)
    VMS = property(_getVMS)
    Phones = property(_getPhones)
