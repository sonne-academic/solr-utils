from dataclasses import dataclass
from typing import Optional

@dataclass
class PaperAuthorAffiliation:
    PaperId: str
    AuthorId: str
    AffiliationId: Optional[str]
    AuthorSequenceNumber: str
    OriginalAffiliation: Optional[str]
