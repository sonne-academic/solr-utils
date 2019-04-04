Affiliations = ['AffiliationId', 'Rank', 'NormalizedName', 'DisplayName', 'GridId', 'OfficialPage', 'WikiPage',
                'PaperCount', 'CitationCount', 'CreatedDate']
Authors = ['AuthorId', 'Rank', 'NormalizedName', 'DisplayName', 'LastKnownAffiliationId', 'PaperCount', 'CitationCount',
           'CreatedDate']
ConferenceInstances = ['ConferenceInstanceId', 'NormalizedName', 'DisplayName', 'ConferenceSeriesId', 'Location',
                       'OfficialUrl', 'StartDate', 'EndDate', 'AbstractRegistrationDate', 'SubmissionDeadlineDate',
                       'NotificationDueDate', 'FinalVersionDueDate', 'PaperCount', 'CitationCount', 'CreatedDate']
ConferenceSeries = ['ConferenceSeriesId', 'Rank', 'NormalizedName', 'DisplayName', 'PaperCount', 'CitationCount',
                    'CreatedDate']
FieldOfStudyChildren = ['FieldOfStudyId', 'ChildFieldOfStudyId']
FieldsOfStudy = ['FieldOfStudyId', 'Rank', 'NormalizedName', 'DisplayName', 'MainType', 'Level', 'PaperCount',
                 'CitationCount', 'CreatedDate']
Journals = [
    'JournalId',
    'Rank',
    'NormalizedName',
    'DisplayName',
    'Issn',
    'Publisher',
    'Webpage',
    'PaperCount',
    'CitationCount',
    'CreatedDate'
]
PaperAbstractsInvertedIndex = ['PaperId', 'IndexedAbstract']
PaperAuthorAffiliations = [
    'PaperId',
    'AuthorId',
    'AffiliationId',
    'AuthorSequenceNumber',
    'OriginalAffiliation'
]
PaperCitationContexts = ['PaperId', 'PaperReferenceId', 'CitationContext']
PaperFieldsOfStudy = ['PaperId', 'FieldOfStudyId', 'Score']
PaperLanguages = ['PaperId', 'LanguageCode']
PaperRecommendations = ['PaperId', 'RecommendedPaperId', 'Score']
PaperReferences = ['PaperId', 'PaperReferenceId']
PaperResources = ['PaperId', 'ResourceType', 'ResourceUrl', 'SourceUrl', 'RelationshipType']
PaperUrls = ['PaperId', 'SourceType', 'SourceUrl']
Papers = ['PaperId', 'Rank', 'Doi', 'DocType', 'PaperTitle', 'OriginalTitle', 'BookTitle', 'Year', 'Date', 'Publisher',
          'JournalId', 'ConferenceSeriesId', 'ConferenceInstanceId', 'Volume', 'Issue', 'FirstPage', 'LastPage',
          'ReferenceCount', 'CitationCount', 'EstimatedCitation', 'OriginalVenue', 'CreatedDate']
RelatedFieldOfStudy = ['FieldOfStudyId1', 'Type1', 'FieldOfStudyId2', 'Type2', 'Rank']
