from salty.rating.dao import save_rating_vote_in_db, get_active_contest_from_db, get_my_latest_vote_for_contest_from_db, \
    connect
from salty.rating.utils import unique_id
from salty_tickets.config import MONGO


def add_rating_vote(inputs_dict: dict, voter_uid: str, is_judge: bool = False) -> None:
    """
     Example:
         inputs_dict = {
            'name': 'Alex',
            'contest_uid': '2123-23123-3443d-21d',
            'ratings': {
                '42': 5,
                '33': 4,
                '23': 4,
            }
         }
    """
    connect(MONGO)
    save_rating_vote_in_db(
        name=inputs_dict.get('name', ''),
        voter_uid=voter_uid,
        contest_uid=inputs_dict['contest_uid'],
        ratings=inputs_dict['ratings'],
        is_judge=is_judge
    )


def get_current_contest_config(active_only) -> dict:
    connect(MONGO)
    return get_active_contest_from_db(active_only) or {}


def get_my_last_vote(contest_uid: str, voter_uid: str) -> dict:
    if not contest_uid:
        return {}
    connect(MONGO)
    return get_my_latest_vote_for_contest_from_db(voter_uid, contest_uid) or {}


def generate_voter_uid() -> str:
    return unique_id()

