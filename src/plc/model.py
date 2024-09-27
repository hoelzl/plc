from attrs import frozen


@frozen
class Model:
    id: str
    slug: str
