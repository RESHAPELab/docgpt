from pydantic import BaseModel

from ..enums.encoding import EncodingName


class ChunkedTokensProps(BaseModel):
    encoding_name: EncodingName = EncodingName.cl100k_base
    chunk_length: int = 8191
