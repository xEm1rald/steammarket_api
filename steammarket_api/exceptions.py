class ParseError(Exception):
    """Raises when something went wrong in parsing"""
    pass

class IncorrectHashName(Exception):
    """Raises on wrong hash name"""
    pass