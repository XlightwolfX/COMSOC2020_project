from partialorders import PartialOrder

class Voter:
    """Class representing a voter in the social network"""

    def __init__(self, partial, strict):
        """A voter is defined by a known partial order + a strict "true" order.
        NOTE: we might decide to recide the strict order and only have the partial one.

        Parameters:
        partial (PartialOrder): a partial order representing the knowledge of the player
        strict (list(int): a strict order representing his true order"""

        assert partial.check_consistency(strict), "A voter's knowledge of his order must be consistent with his true order."

        self.partial = partial
        self.strict = strict

        self.indecisivness = partial.compute_indecisivness()

    def cast_random_vote(self):
        """Return a random vote.

        Returns:
        list(int): a true order consistent with the voter's self-knowledge"""

        return self.partial.random_strict_order()

    def delegate(self, neighbours_ids, neighbours, criteria = 'min_indecision'):
        """ Choose whom to delegate to. Criteria: among those who are consistent, pick 
        the less indecisive. If none is consistent, return none."

        Parameters:
        neighbours_ids (list(int)): list of the ids of the neighbours
        neighbours (list(Voter)): list of the actual neighbours
        criteria (str): specify which criteria to use.

        Returns:
        ([list(int)]): indexes of the choosen delegators. Might be empty!"""


        if criteria == 'min_indecision': # pick alternative that minimizes indecision
            min_score = float('inf')
            candidadate_list = []

            for i, p in zip(neighbours_ids, neighbours):
                if self.partial.check_consistency(p.partial):
                    score = p.indecisivness
                    if score < min_score:
                        min_score = score
                        candidadate_list = [i]
                    elif score == min_score:
                        candidadate_list.append(i)

                # if he's less or equally decided then us, we don't delegate
                candidadate_list = [] if min_score >= self.indecisivness else candidadate_list

        elif criteria == 'random': # randomly pick a consistent parital order
            # TODO first, decide based on indecisivness whether i votes or not
            consistent_orders = [i for i, p in zip(neighbours_ids, neighbours) if self.partial.check_consistency(p.partial)]
            candidadate_list = [random.choice(consistent_orders)] if consistent_orders else []
        else:
            raise NotImplementedError('This delegation strategy has not been implemented.')

        # three cases: none, one or more than one
        return candidadate_list