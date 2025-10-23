import typer
from db_client import WikipediaDB

app = typer.Typer()

@app.command()
def test():
    db = WikipediaDB()
    res = db.test2()
    for r in res:
        print(r)
    db.close()

if __name__ == "__main__":
    app()