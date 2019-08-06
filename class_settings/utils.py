class Missing:
    def __bool__(self):
        return False


missing = Missing()
