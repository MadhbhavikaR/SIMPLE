from enum import Enum, auto
class PromptType(Enum):
    SECRET = auto()
    PATH = auto()
    EMAIL = auto()
    DOMAIN = auto()
    NUMBER = auto()
    STRING = auto()
    PASSWORD = auto()
