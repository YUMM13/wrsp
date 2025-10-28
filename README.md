# wrsp (Wikipedia Race Shortest Path)
A CLI tool that finds the shortest possible route between 2 wikipedia pages.
## What is it?
A Wikipedia Race is a game where players start on one Wikipedia article and navigate to a second article by only clicking the outlinks on the page. The player who gets to the end page the quickest wins. 
The project automates the process by using a graph search algorithm to find the optimal path between the two nodes.
## How does it work?
### The Database
I utilized a graph database (Neo4j) to model Wikipedia:
- Nodes are pages
- Edges represent outlinks to other pages

Instead of building my own database, I used a premade Neo4j database from [EPFL](https://lts2.epfl.ch/Datasets/Wikipedia/) since it had pages and outlinks. 
However, this dump had 2 main issues. 
1. **Outdated Format**
It was built for an older version of Neo4j (3.5) and the data is from 2018. This was not a large issue, since the algorithm still works perfectly. 
2. **Maintenance Pages**
The dump included Wikipedia’s internal maintenance articles (e.g. “Articles needing citation updates from June 2016”). These aren’t used in actual races and caused the algorithm to waste time exploring irrelevant paths.
To fix this, I labeled such pages as "Metadata" so the algorithm ignores them during traversal.
### The Algorithm
The algorithm is based on BFS with a couple of additional features.
1. **Depth Limiter** 
This feature limits the scope of our search to articles that are within 7 clicks away from the original page. In practice, most unrelated articles connected within 5 clicks, so 7 is a reasonable max. 
2. **Path Rebuilder**
To reconstruct the shortest path efficiently, I used was a parent dictionary that keeps track of how each page was reached. 
When the algorithm found the end page, the algorithm walks back through the parent chain until it reaches the start. This process runs in O(d) time (where d ≤ 7) and uses O(n) memory for visited nodes.
3. **Batch Processing**
Originally, the algorithm processed nodes one at a time, which caused slow performance due to frequent database requests.
To optimize this, I added batch processing, allowing up to 50 pages to process at a time. This significantly reduced the number of Neo4j requests and improved throughput. 
## How To Install
To install wrsp, you can install it directly through GitHub
`pip install https://github.com/YUMM13/wrsp.git`
### Database Setup
wrsp requires a running Neo4j instance.
A copy of the database is included with the project.
To launch your own instance using Docker:
```
// launch the container
docker run --name wikipedia -it ^
-p 7474:7474 -p 7687:7687 ^
-v "path/for/database/content/to/persist/data:/data"
-v "path/to/dump_file/dump:/dump"
-e NEO4J_AUTH=neo4j/password ^
neo4j:4.4.31

// after the container loads, stop it and run this
bin/neo4j-admin load ^
--from=/dump/graph.db.dump ^
--database=graph.db ^
--force
```
Once your database is running, you can run the app in your terminal using this command
`wrsp 'https://en.wikipedia.org/wiki/page_1' 'https://en.wikipedia.org/wiki/page_2'`
