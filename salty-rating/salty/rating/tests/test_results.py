import pytest
import mongoengine as me
import numpy as np
from salty.rating.admin import start_contest, stop_contest, get_contest_results
from salty.rating.utils import unique_id
from salty.rating.voting import add_rating_vote, get_current_contest_config


def test_e2e():
    me.connect(host='mongomock://mock')

    contest_config = start_contest({
        'name': 'Test',
        'contestants': ['22', '44', '12']
    })

    voters = [unique_id() for x in range(3)]
    judges = [unique_id() for x in range(3)]

    def _input(scores, name=''):
        return {
            'name': name,
            'contest_uid': contest_config['contest_uid'],
            'ratings': {k: v for k, v in zip(contest_config['contestants'], scores) if v}
        }

    data = [
        # all skate
        ('v', 0, [4, 0, 0]),
        ('v', 0, [4, 4, 0]),
        ('v', 1, [0, 5, 0]),
        ('v', 2, [0, 5, 0]),
        ('j', 0, [0, 0, 5]),
        ('j', 1, [5, 0, 0]),
        ('j', 1, [5, 4, 0]),
        ('j', 1, [5, 4, 3]),
        ('j', 2, [0, 4, 0]),

        # 1st spotlight
        ('v', 0, [5, 4, 0]),
        ('v', 1, [3, 5, 0]),
        ('j', 0, [4, 0, 5]),
        ('j', 1, [4, 4, 3]),
        ('j', 2, [4, 4, 0]),

        # 2nd spotlight
        ('v', 1, [3, 4, 0]),
        ('v', 2, [4, 5, 0]),
        ('j', 0, [4, 5, 5]),
        ('j', 1, [4, 5, 3]),

        # 3rd spotlight
        ('v', 0, [5, 4, 3]),
        ('v', 1, [3, 4, 4]),
        ('j', 0, [4, 5, 4]),
        ('j', 1, [4, 5, 4]),
        ('j', 2, [4, 4, 5]),

        # all skate
        ('v', 0, [4, 4, 3]),
        ('j', 1, [4, 5, 3]),
    ]

    ratings_temp = {}
    for d in data:
        is_judge = d[0] == 'j'
        if is_judge:
            _uid = judges[d[1]]
        else:
            _uid = voters[d[1]]
        add_rating_vote(_input(d[2], f'{d[0]}_{d[1]}'), _uid, is_judge)
        ratings_temp[(d[0], d[1])] = [x if x > 0 else np.nan for x in d[2]]

    stop_contest(contest_config)

    ratings_v = np.nanmean([r for k, r in ratings_temp.items() if k[0] == 'v'], axis=0)
    ratings_j = np.nanmean([r for k, r in ratings_temp.items() if k[0] == 'j'], axis=0)
    total_ratings = np.nanmean([ratings_v, ratings_j], axis=0)

    results = get_contest_results(contest_config)

    assert dict(zip(contest_config['contestants'], total_ratings)) == results['Total']
    assert dict(zip(contest_config['contestants'], ratings_v)) == results['Audience']
    assert dict(zip(contest_config['contestants'], ratings_j)) == results['Judges']
