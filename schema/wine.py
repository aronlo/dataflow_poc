import typing

class WineSchema(typing.NamedTuple):
    id: int
    winery: str
    variety: str
    province: str
    country: str
    points: int
    price: float
