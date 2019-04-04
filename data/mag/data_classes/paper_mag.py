from dataclasses import dataclass
from typing import Optional, Any


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


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


@dataclass
class Doc:
    paper_id: str
    rank: int
    paper_title: str
    original_title: str
    year: int
    date: str
    publisher: Optional[str]
    volume: Optional[str]
    issue: Optional[str]
    first_page: Optional[str]
    reference_count: int
    citation_count: int
    estimated_citation: int
    original_venue: Optional[str]
    conference_series_id: Optional[int]
    conference_instance_id: Optional[int]
    created_date: str
    version: float
    last_page: Optional[str]
    doc_type: Optional[str]
    journal_id: Optional[int]
    doi: Optional[str]
    book_title: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Doc':
        assert isinstance(obj, dict)
        paper_id = from_str(obj.get("PaperId"))
        rank = from_int(obj.get("Rank"))
        paper_title = from_str(obj.get("PaperTitle"))
        original_title = from_str(obj.get("OriginalTitle"))
        year = from_int(obj.get("Year"))
        date = from_str(obj.get("Date"))
        publisher = from_union([from_str, from_none], obj.get("Publisher"))
        volume = from_union([from_str, from_none], obj.get("Volume"))
        issue = from_union([from_str, from_none], obj.get("Issue"))
        first_page = from_union([from_str, from_none], obj.get("FirstPage"))
        reference_count = from_int(obj.get("ReferenceCount"))
        citation_count = from_int(obj.get("CitationCount"))
        estimated_citation = from_int(obj.get("EstimatedCitation"))
        original_venue = from_union([from_str, from_none], obj.get("OriginalVenue"))
        conference_series_id = from_union([from_int, from_none], obj.get("ConferenceSeriesId"))
        conference_instance_id = from_union([from_int, from_none], obj.get("ConferenceInstanceId"))
        created_date = from_str(obj.get("CreatedDate"))
        version = from_float(obj.get("_version_"))
        last_page = from_union([from_str, from_none], obj.get("LastPage"))
        doc_type = from_union([from_str, from_none], obj.get("DocType"))
        journal_id = from_union([from_int, from_none], obj.get("JournalId"))
        doi = from_union([from_str, from_none], obj.get("Doi"))
        book_title = from_union([from_str, from_none], obj.get("BookTitle"))
        return Doc(paper_id, rank, paper_title, original_title, year, date, publisher, volume, issue, first_page, reference_count, citation_count, estimated_citation, original_venue, conference_series_id, conference_instance_id, created_date, version, last_page, doc_type, journal_id, doi, book_title)

    def to_dict(self) -> dict:
        result: dict = {}
        result["PaperId"] = from_str(self.paper_id)
        result["Rank"] = from_int(self.rank)
        result["PaperTitle"] = from_str(self.paper_title)
        result["OriginalTitle"] = from_str(self.original_title)
        result["Year"] = from_int(self.year)
        result["Date"] = from_str(self.date)
        result["Publisher"] = from_union([from_str, from_none], self.publisher)
        result["Volume"] = from_union([from_str, from_none], self.volume)
        result["Issue"] = from_union([from_str, from_none], self.issue)
        result["FirstPage"] = from_union([from_str, from_none], self.first_page)
        result["ReferenceCount"] = from_int(self.reference_count)
        result["CitationCount"] = from_int(self.citation_count)
        result["EstimatedCitation"] = from_int(self.estimated_citation)
        result["OriginalVenue"] = from_union([from_str, from_none], self.original_venue)
        result["ConferenceSeriesId"] = from_union([from_int, from_none], self.conference_series_id)
        result["ConferenceInstanceId"] = from_union([from_int, from_none], self.conference_instance_id)
        result["CreatedDate"] = from_str(self.created_date)
        result["_version_"] = to_float(self.version)
        result["LastPage"] = from_union([from_str, from_none], self.last_page)
        result["DocType"] = from_union([from_str, from_none], self.doc_type)
        result["JournalId"] = from_union([from_int, from_none], self.journal_id)
        result["Doi"] = from_union([from_str, from_none], self.doi)
        result["BookTitle"] = from_union([from_str, from_none], self.book_title)
        return result
