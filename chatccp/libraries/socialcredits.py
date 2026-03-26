from ..database import db

SCORE_RATING = [
    (1000, "Exemplary Citizen"),
    (999, "Model Citizen"),
    (749, "Active Contributor"),
    (499, "Average"),
    (249, "Needs Improvement"),
    (99, "At Risk"),
    (0, "Restricted Access"),
]

class SocialCreditsLib:
    def __init__(self):
        pass

    def get_leaderboard(self, limit: int = 10) -> list[tuple[int, int, str, bool]]:
        top_users = db.get_top_users_by_field("social_score", limit=limit)

        return [
            (user.user_id, user.social_score, self.get_rating_for_score(user.social_score), user.is_supreme_leader)
            for user in top_users
        ]

    def get_rating_for_score(self, score: int) -> str:
        return next(label for min_score, label in SCORE_RATING if score >= min_score)

    def get_user_rating(self, user_id: int) -> tuple[int, str, bool]:
        is_supreme_leader = db.get_user_field(user_id, "is_supreme_leader") or False
        score = db.get_user_field(user_id, "social_score") or 0

        if is_supreme_leader:
            return 9999, "Supreme Leader", is_supreme_leader

        return min(score, 9998), self.get_rating_for_score(score), is_supreme_leader

    def set_supreme_leader(self, user_id: int, is_leader: bool) -> None:
        db.set_user_field(user_id, "is_supreme_leader", is_leader)

sclib = SocialCreditsLib()
