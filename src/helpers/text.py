from typing import Generator, Iterable
import tiktoken
from enum import Enum
from pydantic import validate_call
from pydantic import BaseModel
from operator import attrgetter
from itertools import islice


class EncodingNames(str, Enum):
    cl100k_base = "cl100k_base"


class ChunkedTokensProps(BaseModel):
    encoding_name: EncodingNames = EncodingNames.cl100k_base
    chunk_length: int = 8191


def __batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


@validate_call
def chunked_tokens(text: str, props=ChunkedTokensProps()) -> Iterable[tuple]:
    encoding_name, chunk_length = attrgetter("encoding_name", "chunk_length")(props)

    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = __batched(tokens, chunk_length)
    yield from chunks_iterator
