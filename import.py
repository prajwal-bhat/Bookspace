import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, email VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT null)")
    db.execute("CREATE TABLE reviews(isbn VARCHAR NOT NULL, review VARCHAR NOT NULL, rating INTEGER not null, username VARCHAR NOT NULL)")
    print("Table created")
    csvfile = open("books.csv")
    reader = csv.reader(csvfile)
    count=0
    for isbn, title, author, year in reader:
        if isbn=="isbn":
            continue
        count+=1
        print(f"{count} data added")
        db.execute("INSERT INTO books(isbn,title,author,year) VALUES(:isbn, :title, :author, :year)",{"isbn":isbn, "title":title, "author":author, "year":year})

    print("Completed")    
    db.commit()

main()  