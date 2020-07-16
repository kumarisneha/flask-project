from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Book

import json
# Connect to Database and create database session
engine = create_engine('sqlite:///books-collection.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

"""
api functions
"""
from flask import jsonify


def get_books():
    books = session.query(Book).all()
    print([b.serialize for b in books])
    return jsonify(books=[b.serialize for b in books])

def get_book(book_id):
    book = session.query(Book).filter(Book.id==book_id).first()
    if not book:
        return jsonify({"message":"Book id not found"})
    return jsonify(books=book.serialize)


def makeANewBook(title, author, genre):
    addedbook = Book(title=title, author=author, genre=genre)
    session.add(addedbook)
    session.commit()
    return jsonify(Book=addedbook.serialize)


def updateBook(id, title, author, genre):
    updatedBook = session.query(Book).filter(Book.id==id).first()
    if not updatedBook:
        return jsonify({"message":"Book for this id not found"})
    if title:
        updatedBook.title = title
    if author:
        updatedBook.author = author
    if genre:
        updatedBook.genre = genre
    session.add(updatedBook)
    session.commit()
    return jsonify({"message":'Updated a Book with id %s' % id})


def deleteABook(id):
    bookToDelete = session.query(Book).filter_by(id=id).first()
    if not bookToDelete:
        return jsonify({"message":"Id not found"})    
    session.delete(bookToDelete)
    session.commit()
    return jsonify({"message":'Removed Book with id %s' % id})


class Books(Resource):
    def get(self):
        return get_books()

    def post(self):
        data = json.loads(request.data)
        print("data--------", data)
        title = data.get("title",None)
        author = data.get("author",None)
        genre = data.get("genre",None)
        if title is None or author is None or genre is None:
            return jsonify({"message":"Any one from title, author, genre is missing"})
        else:
            addedbook = Book(title=title, author=author, genre=genre)
            session.add(addedbook)
            session.commit()
            return jsonify(Book=addedbook.serialize)

class BookId(Resource):
    def get(self, id):
        return get_book(id)

    def put(self, id):
        title = request.args.get('title', '')
        author = request.args.get('author', '')
        genre = request.args.get('genre', '')
        print(id, title, author, genre)
        return updateBook(id, title, author, genre)

    def delete(self, id):
        return deleteABook(id)

api.add_resource(Books, '/booksApi', '/')
api.add_resource(BookId, '/booksApi/<int:id>')

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)