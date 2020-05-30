import argparse
import os
import itertools as it
from random import randint
from votingrules import VotingRules
from voter_type import VoterTypes


class Dataset:
    """Container for Preflib dataset. Possible to generate random synth data

    Arguments: source (str): Source for voter preferences ('random'|'type_random'|<path>)
               rand_params(List(int,int)): parameters for random generation [alternativeNum, voterNum, typeNum(for type_random)]
               type_generation (str): Parameter for type generator if type_random is selected ('tshirt'|'half_normal')"""
    def __init__(self, source='random', rand_params=[3, 10, 2], type_generation='half_normal'):

        self.preferences, self.counts, candidates = self._process_data(source, rand_params, type_generation)
        self.candidates = set(range(1, candidates + 1))

    @staticmethod
    def _is_int(s):
        """check if string is an int"""
        try:
            int(s)
            return True
        except:
            return False

    def _process_data(self, source, param, type_generation):
        """process preflib dataset or make synth data"""
        preferences = []
        counts = []

        # generate preferences uniformly
        if source == 'random':
            # make synthetic data; reproduce preflib format
            assert len(param) >= 2, 'Specify all parameters for random generation [voterNr, prefNr]'
            candidates = list(range(1, param[0] + 1))
            voters = param[1]
            pref_permutations = list(it.permutations(candidates))

            profile = dict()
            for v in range(voters):
                perm = randint(0, len(pref_permutations) - 1)
                ballot = list(pref_permutations[perm])
                ballot_id = "".join([str(i) for i in ballot])
                try:
                    cnt = profile[ballot_id][0]
                    cnt += 1
                    profile[ballot_id] = [cnt] + ballot
                except:
                    profile[ballot_id] = [1] + ballot

            headless_tokens = list(profile.values())
            header = [[param[0]]]
            for c in candidates:
                header.append(f'{str(c)}:')
            header.append('x,x,x') # in preflib this line is for extra info (nr of voters/ballots/...)
            tokens = header + headless_tokens

        # generate preferences according to types
        elif source == 'type_random':
            # make synthetic data; reproduce preflib format
            candidates = list(range(1, param[0] + 1))
            assert len(param) >= 3, 'Specify all parameters for type_random generation [voterNr, prefNr, typeNr]'
            assert len(candidates) == 4, 'type_random generation supported only for 4 alternatives'
            voters = param[1]
            types = param[2]
            generator = VoterTypes(num_types=types, gen_type=type_generation)

            profile = dict()
            for v in range(voters):
                ballot = generator.generate()
                ballot_id = "".join([str(i) for i in ballot])
                try:
                    cnt = profile[ballot_id][0]
                    cnt += 1
                    profile[ballot_id] = [cnt] + ballot
                except:
                    profile[ballot_id] = [1] + ballot

            headless_tokens = list(profile.values())
            header = [[param[0]]]
            for c in candidates:
                header.append(f'{str(c)}:')
            header.append('x,x,x')  # in preflib this line is for extra info (nr of voters/ballots/...)
            tokens = header + headless_tokens

        else:
            if not os.path.exists(source):
                raise ValueError('Dataset: specified path (or source) does not exist')

            with open(source, 'r') as f:
                raw = f.readlines()
                tokens = [[int(j) if self._is_int(j) else j for j in i.strip('\n').split(',')] for i in raw]

        for line_num, line in enumerate(tokens):
            if line_num == 0:
                # get nr of candidates
                candidates_nr = line[0]
            elif line_num > candidates_nr + 1:
                preferences.append(line[1:])
                counts.append(line[0])
            else:
                # candidate mapping; skip
                pass

        return preferences, counts, candidates_nr

    def count_voters(self):
        """return total voters"""
        return sum(self.counts)

    def count_unique_ballots(self):
        """return number of unique ballots"""
        return len(self.preferences)


# runnable for testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='random',
                        help='choose source of the dataset (random or filepath)')
    parser.add_argument('--random_params', type=int, nargs='+', default=[3, 10, 2],
                        help='[alternatives, voters]')
    parser.add_argument('--type_gen', type=str, default='half_normal',
                        help='half_normal | tshirt')

    args = parser.parse_args()

    data = Dataset(source=args.dataset, rand_params=args.random_params, type_generation=args.type_gen)
    print(data.preferences)
    print(data.counts)
    print(data.count_voters())
    print(data.count_unique_ballots())
    print(f"Borda winner: {VotingRules.elect('borda', data.preferences, data.counts)}")
    print(f"Plurality winner: {VotingRules.elect('plurality', data.preferences, data.counts)}")
    print(f"Copeland winner:{VotingRules.elect('copeland', data.preferences, data.counts)}")
