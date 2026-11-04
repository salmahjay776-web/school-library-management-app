
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, Field, Session, create_engine, select



sqlite_url = "sqlite:///library.db"

engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False}
)



class BookBase(SQLModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category: Optional[str] = None
    publisher: Optional[str] = None
    quantity: int = 0


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)



class BookCreate(BookBase):
    pass



class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    publisher: Optional[str] = None
    quantity: Optional[int] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)



app = FastAPI(
    title="School Library Management App API",
    description="API for managing school library books",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()



def get_session():
    with Session(engine) as session:
        yield session



@app.get("/")
def home():
    return {
        "message": "Welcome to the School Library Management API"
    }



@app.get("/books", response_model=list[Book])
def get_books():
    with Session(engine) as session:
        statement = select(Book).order_by(Book.created_at.desc())
        books = session.exec(statement).all()
        return books



@app.post(
    "/books",
    response_model=Book,
    status_code=status.HTTP_201_CREATED
)
def create_book(book: BookCreate):
    with Session(engine) as session:
        new_book = Book.model_validate(book)

        session.add(new_book)
        session.commit()
        session.refresh(new_book)

        return new_book



@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if not book:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )

        return book



@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_data: BookUpdate):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if not book:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )

        update_data = book_data.model_dump(exclude_unset=True)
        book.sqlmodel_update(update_data)

        session.add(book)
        session.commit()
        session.refresh(book)

        return book


# 13. DELETE A BOOK

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)

        if not book:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )

        session.delete(book)
        session.commit()

        return None


