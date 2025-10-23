import neo4j
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("URI")
CREDENTIALS = (os.getenv("DB_USERNAME"), os.getenv("DB_PASSWORD"))

class WikipediaDB:
    def __init__(self):
        self.driver = neo4j.GraphDatabase.driver(URI, auth=CREDENTIALS)
        # self.database = database

    def close(self):
        self.driver.close()

    def test(self):
        query = """MATCH (p:Page{title:"Minecraft"}) RETURN p"""
        with self.driver.session() as session:
            res = session.run(query)
            return res.data()
    
    def findShortestRoute(self, start, end):
        print(1)