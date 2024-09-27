from attrs import frozen


@frozen
class Message:
    role: str
    content: str
