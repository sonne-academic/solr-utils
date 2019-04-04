import xapian
import gzip

from data.mag.headers import Authors

def generate_json_dict(headers, generator):
    for line in generator:
        values = line.split('\t')
        values = [v.strip() for v in values]
        thing = dict(zip(headers, values))
        yield thing


def read_gzip_lines(file, encoding):
    with gzip.open(file, 'rt', encoding=encoding) as f:
        yield from f

### Start of example code.
def index():
    PATH = '/home/bone/data/thesis/data/mag'
    dbpath = PATH + '/authors.xpn'
    datapath = PATH + '/Authors.txt.gz'
    # Create or open the database we're going to be writing to.
    db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)

    # Set up a TermGenerator that we'll use in indexing.
    termgenerator = xapian.TermGenerator()
    termgenerator.set_stemmer(xapian.Stem("en"))
    for fields in generate_json_dict(Authors,read_gzip_lines(datapath, 'utf-8')):

        # 'fields' is a dictionary mapping from field name to value.
        # Pick out the fields we're going to index.
        title = fields.get('DisplayName', u'')
        identifier = fields.get('AuthorId', u'')

        # We make a document and tell the term generator to use this.
        doc = xapian.Document()

        # Store all the fields for display purposes.
        doc.set_data(title)

        # We use the identifier to ensure each object ends up in the
        # database only once no matter how many times we run the
        # indexer.
        idterm = identifier
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)
### End of example code.

if __name__ == '__main__':
    index()