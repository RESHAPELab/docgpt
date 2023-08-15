from enum import Enum
from itertools import islice
from operator import attrgetter
from typing import Iterable

import tiktoken
from pydantic import validate_call

from ..dto.text import ChunkedTokensProps


def _batched(iterable, n):
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
    chunks_iterator = _batched(tokens, chunk_length)
    yield from chunks_iterator
