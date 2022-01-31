"""rating_system.py: Contains Rating class."""

from pymongo.mongo_client import MongoClient
import db_secret

client = MongoClient("mongodb+srv://" + db_secret.secret_id + ":"
                     + db_secret.secret_key +
                     "@cluster0.6se1s.mongodb.net/myFirstDatabase?" +
                     "retryWrites=true&w=majority"
                     )
db = client['kirjasto-backend']
book_collection = db['backendAPI']
user_collection = db['users']
rating_collection = db['ratings']
retrieved_book_collection = list(book_collection.find({}, {'_id': False}))
retrieved_user_collection = list(user_collection.find({}, {'_id': False}))
retrieved_rating_collection = list(rating_collection.find({}, {'_id': False}))


class RatingSystem:
    """
    Class that contain functions
    that are necessary to make rating system work as intended.
    """

    def __init__(self):
        self.books = retrieved_book_collection
        self.users = retrieved_user_collection
        self.user_ratings = retrieved_rating_collection

    def get_retrieved_book_collection(self):
        """
        Function that returns a dictionary called self.books
        that contains retrieved book collection.
        """
        return self.books

    def get_retrieved_user_collection(self):
        """
        Function that returns a dictionary called self.users
        that contains retrieved user collection.
        """
        return self.users

    def get_retrieved_rating_collection(self):
        """
        Function that returns a dictionary called self.user_ratings
        that contains retrieved rating collection.
        """
        return self.user_ratings

    def has_the_user_already_rated_this_book(self, user_id, book_id):
        """Function that checks whether a user has already rated the book."""

        for rating in self.user_ratings:
            if rating["User_ID"] == user_id and rating["Book_ID"] == book_id:
                return True
        return False

    def replace_user_rating(self, new_rating):
        """Function that replaces old rating with a new one."""

        for rating in self.user_ratings:
            if rating["User_ID"] == new_rating["User_ID"] and \
                    rating["Book_ID"] == new_rating["Book_ID"]:
                self.user_ratings.remove(rating)
        self.user_ratings.append(new_rating)

    def give_rating(self, user_id: int, book_id: int, rating: int):
        """
        Function that saves user's rating,
        oid, user id, rated book's id and rating
        to a list called self.user_ratings.
        """

        new_rating = {
            "User_ID": user_id,
            "Book_ID": book_id,
            "Rating": rating
            }

        if self.has_the_user_already_rated_this_book(user_id, book_id):
            rating_collection.replace_one(
                self.get_reimbursable_user_rating(new_rating),
                new_rating
                )
            self.replace_user_rating(new_rating)
        else:
            self.user_ratings.append(new_rating)
            rating_collection.insert_one(new_rating)

    def delete_rating(self, user_id: int, book_id: int):
        """Function that deletes a rating and updates data after."""

        for rating in self.user_ratings:
            if rating["User_ID"] == user_id and rating["Book_ID"] == book_id:
                rating_collection.remove(rating)
                self.user_ratings.remove(rating)

        #Needs to be updated some other way since now Object_id will be added aswell
        #self.update_books_dictionary_ratings()
        #self.update_users_dictionary_rating()

    def get_books_rating_data(self, book_id):
        """
        Function that returns single books rating
        and the amount that the book has been rated.
        """

        count = 0
        rating_sum = 0
        for rating in self.user_ratings:
            if rating["Book_ID"] == book_id:
                if rating["Book_ID"]:
                    count += 1
                    rating_sum += int(rating["Rating"])
        if rating_sum == 0:
            return (0, 0)
        else:
            return (rating_sum / count, count)

    def get_users_mean_score(self, user_id):
        """
        Function that returns single user's mean score
        and the amount that the user has rated books.
        """

        count = 0
        rating_sum = 0
        for rating in self.user_ratings:
            if rating["User_ID"] == user_id:
                if rating["User_ID"]:
                    count += 1
                    rating_sum += int(rating["Rating"])
        if rating_sum == 0:
            return (0, 0)
        else:
            return (rating_sum / count, count)

    def update_books_dictionary_ratings(self):
        """Function that updates ratings in the dictionary called books."""

        for rating in self.books:
            book_id = rating["Book_ID"]
            rating["Rating"] = (
                f"{self.get_books_rating_data(book_id)[0]} "
                f"out of 5 ({self.get_books_rating_data(book_id)[1]} "
                f"ratings)"
                )

    def update_users_dictionary_rating(self):
        """Function that updates mean score in the dictionary called users."""

        for score in self.books:
            user_id = score["Book_ID"]
            score["Mean_score"] = (
                f"{self.get_users_mean_score(user_id)[0]} "
                f"out of 5 ({self.get_users_mean_score(user_id)[1]} "
                f"ratings)"
                )

    def get_reimbursable_book(self, book):
        """
        Function that returns book
        that was originally from the books collection
        if the parameter is the new version of the old book.
        """

        for retrieved_book in retrieved_book_collection:
            if retrieved_book["Book_ID"] == book["Book_ID"]:
                return retrieved_book

    def get_reimbursable_user(self, user):
        """
        Function that returns user
        that was originally from the users collection
        if the parameter is the new version of the old user.
        """

        for retrieved_user in retrieved_user_collection:
            if retrieved_user["user_name"] == user["user_name"]:
                return retrieved_user

    def get_reimbursable_user_rating(self, rating):
        """
        Function that returns user_rating
        that was originally from the user_ratings collection
        if the parameter is the new version of the old user_rating.
        """

        for retrieved_rating in retrieved_rating_collection:
            if retrieved_rating["User_ID"] == rating["User_ID"]:
                return retrieved_rating

    def post_updated_book_collection(self):
        """
        Function that replaces book_collection
        with dictionary called self.books.
        """

        self.update_books_dictionary_ratings()

        for book in self.books:
            book_collection.replace_one(self.get_reimbursable_book(book), book)

    def post_updated_user_collection(self):
        """
        Function that replaces user_collection
        with dictionary called self.users.
        """

        self.update_users_dictionary_rating()

        for user in self.users:
            book_collection.replace_one(self.get_reimbursable_user(user), user)


if __name__ == "__main__":

    rating_system = RatingSystem()

    rating_system.give_rating(
        1,
        1,
        1
        )

    rating_system.give_rating(
        2,
        2,
        2
        )

    rating_system.give_rating(
        3,
        3,
        3
        )

    rating_system.give_rating(
        4,
        4,
        4
        )

    rating_system.post_updated_book_collection()
    rating_system.post_updated_user_collection()

    #ObjectID is added after the new addition
    #rating_system.delete_rating(1, 1)

    print(rating_system.get_retrieved_rating_collection())
