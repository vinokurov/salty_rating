from salty.rating.dao import save_new_contest_in_db, stop_contest_in_db, get_ratings_from_db, connect
from salty.rating.results import calculate_totals
from salty.rating.utils import unique_id
from salty_tickets.config import MONGO


def start_contest(inputs: dict) -> dict:
    """
    Example:
         inputs = {
            'name': 'Mix & Match - Finals',
            'contestants': ['22', '33', '44', '12'],
         }
    """
    connect(MONGO)
    contest_config = {
        'name': inputs.get('name', ''),
        'contest_uid': unique_id(),
        'contestants': inputs['contestants'],
        'active': True
    }
    save_new_contest_in_db(contest_config)
    return contest_config


def stop_contest(contest_config: dict) -> dict:
    connect(MONGO)
    stop_contest_in_db(contest_config['contest_uid'])
    contest_config['active'] = False
    return contest_config


def get_contest_results(contest_config: dict) -> dict:
    connect(MONGO)
    db_results = get_ratings_from_db(contest_config['contest_uid'])
    results = calculate_totals(db_results)
    return results.fillna('N/A').to_dict()


def list_contests() -> list:
    pass
