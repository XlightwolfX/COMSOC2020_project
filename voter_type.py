from itertools import permutations
import numpy as np


class VoterTypes:
    def __init__(self, num_types, gen_type='half_normal'):
        self._gen_types = {'half_normal': self._half_normal_generator}
        self._num_types = num_types
        if gen_type not in self._gen_types:
            raise NotImplementedError('This generation type has not been implemented.')

        self.generate = self._gen_types[gen_type]
        if gen_type == 'half_normal':
            self._types = []
            self._pick_types()
            self._hn_values = np.array([self._half_normal_pdf(x) for x in range(4)])

    def _pick_types(self):
        all_types = [list(x) for x in permutations([1, 2, 3, 4])]
        total = len(all_types)
        while len(self._types) < self._num_types:
            t = all_types[np.random.randint(total)]

            if t not in self._types:
                self._types.append(t)

    def _half_normal_generator(self):
        strict_order = []
        # pick one of the types randomly
        t = self._types[np.random.randint(self._num_types)][:]

        for i in range(4):
            distribution = self._hn_values[:4 - i] / sum(self._hn_values[:4 - i])
            alternative = np.random.choice(t, p=distribution)
            t.remove(alternative)
            strict_order.append(alternative)
        return strict_order

    def _half_normal_pdf(self, x, sigma=1):
        return (2**0.5 / (sigma * np.pi)) * np.exp(- (x**2 / (2 * sigma**2)))
