create index if not exists idx_PaperReferences on PaperReferences(PaperId);
create index if not exists idx_ReferencesPaper on PaperReferences(PaperReferenceId);
create index if not exists idx_Journals on Journals(JournalId);
create index if not exists idx_FieldsOfStudy on FieldsOfStudy(FieldOfStudyId);
create index if not exists idx_PaperResources on PaperResources(PaperId);
create index if not exists idx_PaperUrls on PaperUrls(PaperId);
create index if not exists idx_Papers on Papers(PaperId);
create index if not exists idx_PaperJournals on Papers(JournalId);
create index if not exists idx_Affiliations on Affiliations(AffiliationId);
create index if not exists idx_Authors on Authors(AuthorId);
create index if not exists idx_ConferenceInstances on ConferenceInstances(ConferenceInstanceId);
create index if not exists idx_ConferenceSeries on ConferenceSeries(ConferenceSeriesId);
create index if not exists idx_PaperAuthorAffiliations on PaperAuthorAffiliations(PaperId,AuthorId);

