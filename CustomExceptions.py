class WrongLoginError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class UserExistsError(Exception):
    pass


class ShortLoginError(Exception):
    pass


class WrongTagError(Exception):
    pass


class TagExistsError(Exception):
    pass


class DontLoginError(Exception):
    pass


class BookExistsError(Exception):
    pass


class NoTagsError(Exception):
    pass


class EmptyLibraryError(Exception):
    pass
