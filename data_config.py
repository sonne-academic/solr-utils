from pathlib import Path

DATA_HOME = Path.home() / 'tcode' / 'data'
DBLP_DATA = DATA_HOME / 'dblp'
MAG_DATA = DATA_HOME / 'mag'
S2_DATA = DATA_HOME / 's2'
TRANCE_HOME = Path.home() / 'trance_data'

# then e.x. 2019-12 / 2019-12-01__crawledCompactTweets.json.gz
TWITTER_HOME = TRANCE_HOME / 'Twitter' / 'simple-json'

