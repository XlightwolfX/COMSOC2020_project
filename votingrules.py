class VotingRules:

    @classmethod
    def _find_winner(cls, scoreboard):
        winners = set()
        m_val = max(scoreboard.values())
        for k, val in scoreboard.items():
            if val == m_val:
                winners.add(k)
        return winners

    @classmethod
    def _prepare_scoreboard_and_candidates(cls, preferences):
        candidates = set(preferences[0])
        scoreboard = {i: 0 for i in candidates}

        return scoreboard, candidates

    @classmethod
    def elect_borda(cls, preferences, counts):
        scoreboard, candidates = cls._prepare_scoreboard_and_candidates(preferences)

        for candidate in candidates:
            for ballot, count in zip(preferences, counts):
                scoreboard[candidate] += (len(candidates) - 1 - ballot.index(candidate)) * count
        return cls._find_winner(scoreboard)

    @classmethod
    def elect_plurality(cls, preferences, counts):
        scoreboard, candidates = cls._prepare_scoreboard_and_candidates(preferences)

        for candidate in candidates:
            for ballot, count in zip(preferences, counts):
                if ballot[0] == candidate:
                    scoreboard[candidate] += count
        return cls._find_winner(scoreboard)

    @classmethod
    def elect_copeland(cls, preferences, counts):
        scoreboard, candidates = cls._prepare_scoreboard_and_candidates(preferences)

        for candidate in candidates:
            contenders = candidates - {candidate}
            for enemy in contenders:
                pairwise_c = 0
                pairwise_e = 0
                for ballot, count in zip(preferences, counts):
                    if ballot.index(candidate) < ballot.index(enemy):
                        pairwise_c += count
                    elif ballot.index(candidate) > ballot.index(enemy):
                        pairwise_e += count
                if pairwise_c > pairwise_e:
                    scoreboard[candidate] += 1
                elif pairwise_c < pairwise_e:
                    scoreboard[candidate] -= 1
        return cls._find_winner(scoreboard)