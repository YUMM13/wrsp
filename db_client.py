from collections import deque
import neo4j
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("URI")
CREDENTIALS = (os.getenv("DB_USERNAME"), os.getenv("DB_PASSWORD"))
MAX_DEPTH = 7
BATCH_SIZE = 50

class WikipediaDB:
    def __init__(self):
        self.driver = neo4j.GraphDatabase.driver(URI, auth=CREDENTIALS)

    def close(self):
        self.driver.close()

    # test function used for debugging
    def test(self):
        batch = ["Minecraft", "Calculus", "Xbox_360"]
        query = """MATCH (p:Page) WHERE p.title IN $batch
                MATCH (p)-[:LINKS_TO]->(out) 
                WHERE NOT (out:Metadata)
                RETURN p.title AS parent, collect(out.title) AS neighbors"""
        with self.driver.session() as session:
            res = session.run(query, batch=batch)
            return res.data()[0]["neighbors"]
        
    # finds shortest route between two wikipedia articles
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
        parent = {}                         # key = child, value = parent
        depth = {start_title: 0}            # key = page,  value = number of clicks away from start page
        batch_titles = []

        # go through queue
        while queue:
            # fill batch process
            while queue and len(batch_titles) < BATCH_SIZE:
                batch_titles.append(queue.popleft())
            print(f"Current Depth = {depth[batch_titles[0]]}")
            # if we find the end, then break out and reconstruct the path
            if end_title in parent:
                break
            # get neighbors
            query = """MATCH (p:Page) WHERE p.title IN $batch
                MATCH (p)-[:LINKS_TO]->(out) 
                WHERE NOT (out:Metadata)
                RETURN p.title AS parent, collect(out.title) AS neighbors"""
            # iterate through neighbors
            with self.driver.session() as session:
                res = session.run(query, batch=batch_titles)
                batch_result = res.data()
                for r in batch_result:
                    par, neighbors = r["parent"], r["neighbors"]
                    # track depth to limit scope
                    curr_depth = depth[par]
                    for page in neighbors:
                        if page not in visited and curr_depth <= MAX_DEPTH:
                            visited.add(page)
                            if page not in parent:
                                parent[page] = par
                            depth[page] = curr_depth + 1
                            queue.append(page)
            batch_titles.clear()
            
        # remake path
        path = [end_title]
        curr_page = end_title
        while curr_page != start_title:
            p = parent[curr_page]
            path.append(p)
            curr_page = p
        # reverse path
        return f"SHORTEST PATH: {path[::-1]}"
