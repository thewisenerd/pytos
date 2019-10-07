class Builder:
    def __init__(self, base: str, ver: str):
        self.__base = base
        self.__ver = ver

    def build(self, path: str) -> str:
        return 'https://{}/{}{}'.format(self.__base, self.__ver, path)
