class WrongLogin(Exception):
    pass


class WrongPassword(Exception):
    pass


class UserExists(Exception):
    pass


class ShortLogin(Exception):
    pass


class WrongTag(Exception):
    pass


class TagExists(Exception):
    pass


class DontLogin(Exception):
    pass


class BookExists(Exception):
    pass


class NoTags(Exception):
    pass


class EmptyLibrary(Exception):
    pass