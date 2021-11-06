import FB2


class BookHandler:
    def __init__(self, book):
        self.support_format = ['fb2', 'epub', 'pdf']
        self.book_path = book
        self.book_format = self.book_format_check()

    def book_format_check(self):
        book_format = self.book_path.split('.')[-1]
        if book_format not in self.support_format:
            raise TypeError
        return book_format
