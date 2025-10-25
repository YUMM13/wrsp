from collections import deque
import neo4j
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("URI")
CREDENTIALS = (os.getenv("DB_USERNAME"), os.getenv("DB_PASSWORD"))

class WikipediaDB:
    def __init__(self):
        self.driver = neo4j.GraphDatabase.driver(URI, auth=CREDENTIALS)

    def close(self):
        self.driver.close()

    def test(self):
        query = """MATCH (p:Page{title:"Minecraft"})-[:LINKS_TO]->(out:Page) RETURN [n IN nodes(out) | n.title] as neighbors"""
        with self.driver.session() as session:
            res = session.run(query)
            return res.data()
    
    # def findShortestBuiltIn(self, start_page, end_page, depth):
    #     query = """
    #         MATCH p=(a:Page {title:$start})-[*..$depth]->(b:Page {title:$end})
    #         RETURN [n IN nodes(p) | n.title] AS titles"""
    #     with self.driver.session() as session:
    #         res = session.run(query, start=start_page, end=end_page, depth=depth)
    #         return res.single()
        

# halo_(franchise), gordon_freeman, Exponential_decay, Bateman_equation
    def findShortestRoute(self, start, end):
        # get start and end page name
        start_title = start.split('/')[-1]
        end_title = end.split('/')[-1]

        # check that both articles exist
        check_start = """MATCH (p:Page) WHERE p.title = $start RETURN p"""
        with self.driver.session() as session:
                res = session.run(check_start, start=start_title)
                page = res.single()
                if not page:
                    return f"Error finding path: {start_title} was not found in the database."
                
        check_end = """MATCH (p:Page) WHERE p.title = $end RETURN p"""
        with self.driver.session() as session:
                res = session.run(check_end, end=end_title)
                page = res.single()
                if not page:
                    return f"Error finding path: {end_title} was not found in the database."
                
        # set up bfs
        visited = set()
        queue = deque([start_title])
        # key = child, value = parent
        parent = {}
        
        # go through queue
        while queue:
            curr = queue.popleft()
            print(f'processing {curr}')
            # if we find the end, then break out and reconstruct the path
            if curr == end_title:
                break
            visited.add(curr)
            # get neighbors
            query = """MATCH (p:Page{title:$curr})-[:LINKS_TO]->(out:Page) 
                WHERE NOT out.title =~ '^(Articles_|Wikipedia_|NPOV_disputes_|Use_mdy_dates_|Use_dmy_dates_|Use_American_English).*'
                RETURN collect(out.title) AS neighbors"""
            with self.driver.session() as session:
                res = session.run(query, curr=curr)
                neighbors = res.single().values()[0]
                for page in neighbors:
                    if page not in visited:
                        parent[page] = curr
                        queue.append(page)
            
        # remake path
        path = [end_title]
        curr_page = end_title
        while curr_page != start_title:
            p = parent[curr_page]
            path.append(p)
            curr_page = p
        # reverse path
        return path[::-1]
