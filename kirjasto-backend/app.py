#Testing authentication
from distutils.log import debug
from flask import Flask, Response, render_template, session, redirect
from functools import wraps
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient

#Testing authentication
from pymongo.mongo_client import MongoClient

from bson.objectid import ObjectId
from tests import (
    is_book_already_added, is_book_id_inside_book_collection,
    is_comment_data_inside_comment_collection,
    is_rating_acceptable,
    is_user_name_inside_user_collection,
    is_object_int
    )
from books import (
    get_books,
    get_book_by_id,
    add_new_book,
    delete_book_by_id,
    update_book,
    loan_book_by_username_and_id
    )
from comments import (
    delete_comments_by_id,
    get_comments,
    get_comments_by_book_id,
    post_comment
    )
from rating_system import RatingSystem
import db_secret

parser = reqparse.RequestParser()

app = Flask(__name__)
#Testing authentication
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
api = Api(app)
rating_system = RatingSystem()

client = MongoClient(
    "mongodb+srv://" + db_secret.secret_id + ":" + db_secret.secret_key +
    "@cluster0.6se1s.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    )
db = client['kirjasto-backend']
collection = db['books']
testcollection = db["testerdata"]

#Testing authentication
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap

# Routes
from user import routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')


class TesterData(Resource):
    """Class for testing sending and returning data."""
    # def get(self):
    #     return list(testcollection.find())

    def get(self, _id):
        """Function that returns data with object id."""

        return testcollection.find_one({"_id": ObjectId(_id)})

    def post(self):
        """
        Function that posts data depending on
        what is writed on the frontend form.
        """

        parser.add_argument("name", type=str)
        parser.add_argument("writer", type=str)
        parser.add_argument("year", type=int)
        args = parser.parse_args()

        item = {
            "name": args["name"],
            "writer": args["writer"],
            "year": args["year"]
            }
        testcollection.insert_one(item)
        return "Nice!"


class Books(Resource):
    """Class for returning book data from the database."""

    def get(self, book_id=None):
        """Function that returns book data depending on the url."""

        if book_id is not None:
            if is_book_id_inside_book_collection(book_id):
                return get_book_by_id(book_id)
            return "Book is not inside the database!"
        return get_books()


class BooksAddNewBook(Resource):
    """Class for posting book data to the database."""

    def post(
            self, name, writer, year, isbn, about, tags,
            description):
        """Function that posts book data to the database."""

        if is_book_already_added(name, isbn):
            return "Book has already been added!"

        add_new_book(
            name, writer, year, isbn, about, tags,
            description
            )
        return "Book was added succesfully!"


class BooksUpdateBook(Resource):
    """Class for updating book data to the database."""

    def put(
            self, book_id, name, writer, year, isbn, rating, about, tags,
            description, loaner, loan_status):
        """Function that updates book data to the database."""

        if is_book_id_inside_book_collection(book_id) and is_book_already_added(name, isbn) and is_object_int(year):
            update_book(
                book_id, name, writer, year, isbn, rating, about, tags, description,
                loaner, loan_status)
            return "Book was updated succesfully!"
        return "error: Not a valid book_id, name or isbn! " \
            "book_id, name and isbn must be inside the database!"


class BooksDeleteByID(Resource):
    """Class for deleting book data from the database."""

    def delete(self, book_id):
        """Function that deletes book data from the database."""
        if is_book_id_inside_book_collection(book_id):

            delete_book_by_id(book_id)
            return "Book was deleted succesfully!"
        return "error: Not a valid book_id! Book_id must be inside the database!"


class BooksLoanByUsernameAndID(Resource):
    """Class for changing book datas loan state."""

    def post(self, user_name, book_id):
        """Function that changes book's loan state."""

        loan_book_by_username_and_id(user_name, book_id)
        return "Book was loaned succesfully!"


class Comments(Resource):
    """Class for returning comment data from the database."""

    def get(self, book_id=None):
        """Function that returns comment data depending on the url."""
        if book_id is not None:
            
            if is_book_id_inside_book_collection(book_id):
                get_comments_by_book_id(book_id)
                return "Comments retrieved successfully!"
            return "error: Not a valid book_id!"
        
        return get_comments()


class CommentsAddNewComment(Resource):
    """Class for posting comment data to the database."""

    def post(self, user_name, comment, book_id):
        """Function that posts comment data to the database."""

        if is_book_id_inside_book_collection(book_id) and is_user_name_inside_user_collection(user_name):
            post_comment(user_name, comment, book_id)
            return "Comment was posted succesfully!"
        return "error: Not a valid username or book_id! " \
            "book_id and username must exist!"


class CommentsDelete(Resource):
    """Class for deleting comment data from the database."""

    def delete(self, user_name, book_id, comment_id):
        """Function that deletes comment data from the database."""
        if is_user_name_inside_user_collection(user_name) and is_book_id_inside_book_collection(book_id) and is_comment_data_inside_comment_collection(user_name, book_id):
            delete_comments_by_id(user_name, book_id, comment_id)
            return "Comment was deleted succesfully!"
        return "error: Not a valid username, book_id or comment_id!"


#Not needed in rating system?
#-----------------------------------------------------------------------------
#Needed in user file
class RatingsGetUsers(Resource):
    """Class for returning user data from the database."""

    def get(self, user_name=None):
        """Function that returns user data depending on the url."""

        if user_name is not None:
            if is_user_name_inside_user_collection(user_name):

                rating_system.get_retrieved_user_by_username(user_name)
                return "return was successful"
            return 'error: Not a valid username! username must exist!'

        return rating_system.get_retrieved_user_collection()


#Needed?
class RatingsPostUsers(Resource):
    """Class for updating user data from the database."""

    def post(self):
        """
        Function that replaces user_collection
        with dictionary called self.users.
        """

        rating_system.post_updated_user_collection()
        return "User data was updated succesfully!"
#-----------------------------------------------------------------------------


#Editing this
class Ratings(Resource):
    """Class for returning rating data from the database."""

    def get(self, user_name=None, book_id=None):
        """Function that returns rating data depending on the url."""

        if book_id is not None:
            if is_book_id_inside_book_collection(book_id) and is_user_name_inside_user_collection(user_name):
                return rating_system.get_retrieved_rating_by_username_and_id(
                    user_name,
                    book_id
                    )
            return "Incorrect username or book id!"
        elif user_name is not None:
            if is_user_name_inside_user_collection(user_name):
                return rating_system.get_retrieved_ratings_by_username(
                    user_name)
            return "Incorrect username"
        
        return rating_system.get_retrieved_rating_collection()
        


class RatingsAddNewRating(Resource):
    """Class for posting rating data to the database."""

    def post(self, user_name: int, book_id: int, rating: int):
        """Function that posts comment data to the database."""

        rating_system.give_rating(user_name, book_id, rating)
        return "Rating was posted succesfully!"


class RatingsDeleteByUsernameAndBookID(Resource):
    """Class for deleting rating data from the database."""

    def delete(self, user_name, book_id):
        """Function that deletes rating data from the database."""

        rating_system.delete_rating(user_name, book_id)
        return "Rating was deleted succesfully!"


class HomePage(Resource):
    def get(self):
        return Response(response=render_template("index.html"))


api.add_resource(TesterData, "/api/testerdata/<_id>")
# works
api.add_resource(HomePage, '/')
# works
api.add_resource(
    Books,
    '/api/books',
    '/api/books/<book_id>'
    )
# works needs to be edited
api.add_resource(
    BooksAddNewBook,
    '/api/books/add/<name>/<writer>/<year>/<isbn>/' +
    '<about>/<tags>/<description>'
    )
# works but is this needed?
api.add_resource(
    BooksUpdateBook, '/api/books/update/<book_id>/<name>/<writer>/' +
    '<year>/<isbn>/<rating>/<about>/<tags>/<description>/<loaner>/<loan_status>'
    )
# works
api.add_resource(BooksDeleteByID, '/api/books/d/<book_id>/')
# not complete
api.add_resource(
    BooksLoanByUsernameAndID,
    '/api/books/loan/<user_name>/<book_id>'
    )
# works
api.add_resource(
    Comments,
    '/api/comments',
    '/api/comments/<book_id>'
    )
# works
api.add_resource(
    CommentsAddNewComment,
    '/api/comments/add/<user_name>/<comment>/<book_id>'
    )
# Works
api.add_resource(
    CommentsDelete,
    '/api/comments/d/<user_name>/<book_id>/<comment_id>'
    )
# Works
api.add_resource(
    RatingsGetUsers,
    '/api/ratings/users',
    '/api/ratings/users/<user_name>'
    )

# Not sure
#api.add_resource(RatingsPostUsers, '/api/ratings/post/users/')

# Works but when book is added doesn't work after reboot?
api.add_resource(
    Ratings,
    '/api/ratings',
    '/api/ratings/<user_name>',
    '/api/ratings/<user_name>/<book_id>'
    )
# Works
api.add_resource(
    RatingsAddNewRating,
    '/api/ratings/add/<user_name>/<book_id>/<rating>'
    )
# not complete
api.add_resource(
    RatingsDeleteByUsernameAndBookID,
    '/api/ratings/d/<book_id>/user_name'
    )


# Runs on port 8000!!
if __name__ == "__main__":
    #api urls work with this
    #app.run(debug=True)
    #api urls work with this without authentication
    app.run(debug=True, host='127.0.0.1', port=8000)
    #for testing
    #app.run(debug=True, use_debugger=False, use_reloader=False, host='127.0.0.1', port=8000)
