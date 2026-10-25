import pandas as pd


def leaderboard_shakeup(teams, public, private):
    """Ranks on both leaderboards (lower score = better) and the rank change."""
    df = pd.DataFrame({"team": list(teams), "public": list(public), "private": list(private)})
    df["public_rank"] = df["public"].rank(method="min").astype(int)      # ties share the best rank
    df["private_rank"] = df["private"].rank(method="min").astype(int)
    df["rank_change"] = df["public_rank"] - df["private_rank"]            # positive = moved up
    out = df[["team", "public_rank", "private_rank", "rank_change"]]
    return out.sort_values(["private_rank", "team"]).reset_index(drop=True)
