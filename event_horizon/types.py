from typing import Annotated

from sqlalchemy import Text
from sqlalchemy.orm import mapped_column


str_16 = Annotated[str, 16]
str_36 = Annotated[str, 36]
str_80 = Annotated[str, 80]
str_120 = Annotated[str, 120]
str_255 = Annotated[str, 255]
text = Annotated[str, mapped_column(Text())]
