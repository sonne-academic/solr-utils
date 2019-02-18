import requests
import json

lookup_options = {
    'AnalyzingLookupFactory': {
        'suggestAnalyzerFieldType': 'text_prefix',  # no default, most examples use string. must be defined in Schema
        'exactMatchFirst': 'false',  # true
        'preserveSep': 'true',  # true
        'maxGraphExpansions': -1,  # -1
        'maxSurfaceFormsPerAnalyzedForm': 256,  # 256
        'preservePositionIncrements': 'true',  # false
    },
    'FuzzyLookupFactory': {
        'exactMatchFirst': 'true',
        'preserveSep': 'true',
        #  'maxSurfaceFormsPerAnalyzedForm': '',
        'maxGraphExpansions': -1,
        'preservePositionIncrements': 'false',
        'maxEdits': 1,  # max 2
        'transpositions': 'true',
        'nonFuzzyPrefix': 1,
        'minFuzzyLength': 3,
        'unicodeAware': 'false',
    },
    'AnalyzingInfixLookupFactory': {
        'indexPath': 'analyzingInfixSuggesterIndexDir',
        'minPrefixChars': 4,
        'allTermsRequired': 'true',
        'highlight': 'true',
        'suggestAnalyzerFieldType': 'text_prefix',
    },
    'BlendedInfixLookupFactory': {
        # 'blenderType': 'position_linear',
        # 'blenderType': 'position_reciprocal',
        # 'exponent': '2.0',
        'suggestAnalyzerFieldType': 'text_prefix',
        'allTermsRequired': 'true',
        'minPrefixChars': 4,
        # 'numFactor': 10,
        # 'indexPath': 'blendedInfixSuggesterIndexDir',
        # 'minPrefixChars': 4,
    },
    'FreeTextLookupFactory': {
        'suggestFreeTextAnalyzerFieldType': 'text_prefix',
        'ngrams': 2,
    },
    'FSTLookupFactory': {
        'exactMatchFirst': 'true',
        # 'weightBuckets': '',   # The number of separate buckets for weights
    },
    'TSTLookupFactory': {},
    'WFSTLookupFactory': {},
    'JaspellLookupFactory': {},  # deprecated in lucene
}
dictionary_options = {
    'DocumentDictionaryFactory': {
        # 'weightField': '',  # A field that is stored or a numeric DocValue field. optional
        # 'payloadField': '',  # should be a field that is stored. optional
        # 'contextField': '',
        # Field to be used for context filtering. Note that only some lookup implementations support filtering.
    },
    'DocumentExpressionDictionaryFactory': {
        'payloadField': '',
        'weightExpression': '',
        'contextField': '',
    },
    'HighFrequencyDictionaryFactory': {
        #  A value between zero and one representing the minimum fraction of the total documents
        #  where a term should appear in order to be added to the lookup dictionary.
        'threshold': 0.5,
    },
    'FileDictionaryFactory': {
        'fieldDelimiter': '\t',
    }
}

if __name__ == '__main__':
    collection = 'dblp'
    config = 'dblp'
    name = 'default'
    field = 'author'
    sourceLocation = ''
    storeDir = ''
    buildOnCommit = 'false'
    buildOnOptimize = 'false'
    buildOnStartup = 'false'
    lookupImpl = 'FreeTextLookupFactory'
    dictionaryImpl = 'DocumentDictionaryFactory'
    suggester = {
        'name': name,
        'lookupImpl': lookupImpl,
        'dictionaryImpl': dictionaryImpl,
        'field': field,
    }
    suggester.update(lookup_options[lookupImpl])
    suggester.update(dictionary_options[dictionaryImpl])

    replace_field = {
        "replace-field-type": {
            "name": "text_prefix",
            "class": "solr.TextField",
            "positionIncrementGap": "100",
            "indexAnalyzer": {
                "tokenizer": {
                    "class": "solr.WhitespaceTokenizerFactory",
                },
                "filters": [
                    # {
                    #     "class": "solr.EdgeNGramFilterFactory",
                    #     "minGramSize": "3",
                    #     "maxGramSize": "15"
                    # },
                    {
                        "class": "solr.LowerCaseFilterFactory",
                    }
                ]
            },
            "queryAnalyzer": {
                "tokenizer": {
                    "class": "solr.WhitespaceTokenizerFactory",
                },
                "filters": [
                    {
                        "class": "solr.LowerCaseFilterFactory",
                    }
                ]
            },
        }
    }

    searchcomponent = {
        "update-searchcomponent": {
            "name": "authorsuggest",
            "class": "solr.SuggestComponent",
            "suggester": suggester
        }
    }

    # print('replacing field type')
    # r = requests.post(f'http://localhost:8983/api/c/{collection}/schema', json=replace_field)
    # print(r.text)

    # headers = {'Content-Type': 'text/xml'}

    print('sending new suggester config')
    # print(json.dumps(cmd, indent=2))
    r = requests.post(f'http://localhost:8983/api/c/{collection}/config', json=searchcomponent)
    print(r.text)
    print('building suggest index')
    r = requests.get(f'http://localhost:8983/solr/{collection}/authors', params={'suggest.build': 'true'})
    print(r.text)
