import string

class Business:
    """This class devines a Business Object"""
    def __init__(
        self, 
        id: string,
        name: string,
        rating: int,
        cuisine: string
    ):
        self._id = id
        self._name = name
        self._rating = rating
        self._cuisine = cuisine

    @property
    def id(self) -> string:
        return self._id

    @property
    def name(self) -> string:
        return self._name

    @property
    def cuisine(self) -> string:
        return self._cuisine

    @property
    def rating(self) -> int:
        return self._rating

    def toString(self) -> string:
        return "_id: " + str(self._id) + ", name: " + self._name + ", cuisine: " + self._cuisine + ", rating: " + str(self._rating)
