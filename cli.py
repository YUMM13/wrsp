import typer
from db_client import WikipediaDB

app = typer.Typer()

@app.command()
def test():
    db = WikipediaDB()
    res = db.test()
    for r in res:
        print(r)
    db.close()

@app.command()
def wrsp(start: str, end: str):
    db = WikipediaDB()
    path = db.findShortestRoute(start, end)
    print(path)
    db.close()

if __name__ == "__main__":
    app()