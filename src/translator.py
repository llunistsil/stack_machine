class StackOverflowError(Exception):
    """Переполнение стека данных"""

    def __init__(self, message="Data stack overflow"):
        super().__init__(message)


class StackUnderflowError(Exception):
    """Исчерпание стека данных"""

    def __init__(self, message="Data stack underflow"):
        super().__init__(message)
