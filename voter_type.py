from itertools import permutations
import numpy as np


class VoterTypes:
    def __init__(self, num_types=2, gen_type='half_normal'):
        """Create type generator object; interface - self.generate()"""
        self._gen_types = {
                            'half_normal': self._half_normal_generator,
                            'tshirt': self._tshirt_generator
                          }
        self._num_types = num_types
        if gen_type not in self._gen_types:
            raise NotImplementedError('This generation type has not been implemented.')

        self.generate = self._gen_types[gen_type]
        if gen_type == 'half_normal':
            self._types = []
            self._pick_types()
            self._hn_values = np.array([self._half_normal_pdf(x) for x in range(4)])

        if gen_type == 'tshirt':
            self._tshirt_init()

    def _tshirt_init(self, path='dataset/tshirt.soc'):
        with open(path, 'r') as f:
            raw = f.readlines()
            num_alternatives = int(raw[0].strip('\n'))
            preference_profiles = [list(eval(x[2:].strip('\n'))) for x in raw[13:]]

        four_alternatives = list(np.random.choice(range(1, num_alternatives + 1), 4, replace=False))
        a_map = {a: i + 1 for i, a in enumerate(four_alternatives)}
        self._preference_profiles = [[a_map[a] for a in pref if a in a_map] for pref in preference_profiles]

    def _tshirt_generator(self):
        p = np.random.randint(len(self._preference_profiles))
        return self._preference_profiles[p]

    # half_normal
    def _pick_types(self):
        all_types = [list(x) for x in permutations([1, 2, 3, 4])]
        total = len(all_types)
        while len(self._types) < self._num_types:
            t = all_types[np.random.randint(total)]

            if t not in self._types:
                self._types.append(t)

    def _half_normal_generator(self, t=None):
        strict_order = []
        # pick one of the types randomly

        if type is None:
            t = self._types[np.random.randint(self._num_types)][:]

        for i in range(4):
            distribution = self._hn_values[:4 - i] / sum(self._hn_values[:4 - i])
            alternative = np.random.choice(t, p=distribution)
            t.remove(alternative)
            strict_order.append(alternative)
        return strict_order

    def _half_normal_pdf(self, x, sigma=1):
        return (2**0.5 / (sigma * np.pi)) * np.exp(- (x**2 / (2 * sigma**2)))



if __name__ == "__main__":
    # Test
    Types = VoterTypes(num_types=2, gen_type='half_normal')

    x = Types.generate()

    print(x)
