import mongoengine as me


ALIAS_RATING = 'rating'


def document_to_dict(doc):
    if doc is not None:
        doc_dict = doc.to_mongo().to_dict()
        doc_dict = {k: v for k, v in doc_dict.items() if k != '_id'}
        return doc_dict


def connect(host=None):
    if host is None:
        host = 'mongomock://localhost'
    me.connect(host=host, alias=ALIAS_RATING)


class RatingVoteDocument(me.Document):
    meta = {
        'collection': 'rating_votes',
        'db_alias': ALIAS_RATING,
    }
    name = me.StringField()
    voter_uid = me.StringField()
    ratings = me.DictField()
    contest_uid = me.StringField()
    is_judge = me.BooleanField()

    def to_dict(self) -> dict:
        doc_dict = document_to_dict(self)
        if hasattr(self, '_id'):
            doc_dict['timestamp'] = self._id.generation_time()
        return doc_dict


class ContestConfigDocument(me.Document):
    meta = {
        'collection': 'rating_contests',
        'db_alias': ALIAS_RATING,
    }
    active = me.BooleanField()
    name = me.StringField()
    contestants = me.ListField()
    contest_uid = me.StringField()

    def to_dict(self) -> dict:
        doc_dict = document_to_dict(self)
        if hasattr(self, '_id'):
            doc_dict['timestamp'] = self._id.generation_time()
        return doc_dict


def save_rating_vote_in_db(name: str, voter_uid: str, contest_uid: str,
                           ratings: dict, is_judge: bool) -> None:
    RatingVoteDocument(
        name=name,
        voter_uid=voter_uid,
        ratings=ratings,
        contest_uid=contest_uid,
        is_judge=is_judge
    ).save()


def save_new_contest_in_db(contest_config: dict) -> None:
    ContestConfigDocument(**contest_config).save()


def stop_contest_in_db(contest_uid: str) -> None:
    doc = ContestConfigDocument.objects(contest_uid=contest_uid).first()
    doc.active = False
    doc.save()


def get_ratings_from_db(contest_uid: str) -> list:
    results = RatingVoteDocument.objects.aggregate(
        {'$match': {'contest_uid': contest_uid}},
        # {'$last': "$_id"},
        {'$group': {
            "_id": "$voter_uid",
            "ratings": {'$last': "$ratings"},
            "is_judge": {'$last': "$is_judge"},
            "name": {'$last': "$name"},
        }}
    )
    return list(results)


def list_contests_from_db(limit=5) -> list:
    docs = ContestConfigDocument.objects.order_by('-_id')[:limit]
    return list([doc.to_dict() for doc in docs])


def get_active_contest_from_db(active_only=False) -> dict:
    if active_only:
        kwargs = {'active': True}
    else:
        kwargs = {}
    doc = ContestConfigDocument.objects(**kwargs).order_by('-_id').first()
    if doc is not None:
        return doc.to_dict()


def get_my_latest_vote_for_contest_from_db(voter_uid: str, contest_uid: str) -> dict:
    doc = RatingVoteDocument.objects(voter_uid=voter_uid, contest_uid=contest_uid).order_by('-_id').first()
    if doc is not None:
        return doc.to_dict()
