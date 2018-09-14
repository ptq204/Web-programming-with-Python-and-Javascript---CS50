import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    count = 0
    f = open('books.csv')
    reader = csv.reader(f)
    for ISBN, Title, Author, Year in reader:
        db.execute("INSERT INTO books VALUES(:ISBN, :Title, :Author, :Year)",
        {"ISBN" : ISBN, "Title" : Title, "Author" : Author, "Year" : Year})
        count = count + 1
    db.commit()
    print('inserted {} books'.format(count))

if __name__ == '__main__':
    main()



