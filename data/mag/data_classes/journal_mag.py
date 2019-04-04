from dataclasses import dataclass
from typing import Optional, Any, TypeVar


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


@dataclass
class Doc:
    journal_id: str
    rank: int
    normalized_name: str
    display_name: str
    webpage: Optional[str]
    paper_count: int
    citation_count: int
    created_date: str
    version: float
    issn: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Doc':
        assert isinstance(obj, dict)
        journal_id = from_str(obj.get("JournalId"))
        rank = from_int(obj.get("Rank"))
        normalized_name = from_str(obj.get("NormalizedName"))
        display_name = from_str(obj.get("DisplayName"))
        webpage = from_union([from_str, from_none], obj.get("Webpage"))
        paper_count = from_int(obj.get("PaperCount"))
        citation_count = from_int(obj.get("CitationCount"))
        created_date = from_str(obj.get("CreatedDate"))
        version = from_float(obj.get("_version_"))
        issn = from_union([from_str, from_none], obj.get("Issn"))
        return Doc(journal_id, rank, normalized_name, display_name, webpage, paper_count, citation_count, created_date, version, issn)

    def to_dict(self) -> dict:
        result: dict = {}
        result["JournalId"] = from_str(self.journal_id)
        result["Rank"] = from_int(self.rank)
        result["NormalizedName"] = from_str(self.normalized_name)
        result["DisplayName"] = from_str(self.display_name)
        result["Webpage"] = from_union([from_str, from_none], self.webpage)
        result["PaperCount"] = from_int(self.paper_count)
        result["CitationCount"] = from_int(self.citation_count)
        result["CreatedDate"] = from_str(self.created_date)
        result["_version_"] = to_float(self.version)
        result["Issn"] = from_union([from_str, from_none], self.issn)
        return result

