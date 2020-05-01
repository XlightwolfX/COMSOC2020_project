import argparse
import os


class Dataset:
    def __init__(self, source='random'):

        self.preferences, self.counts = self._process_data(source)

    def _process_data(self, source):
        preferences = []
        counts = []
        if source == 'random':
            raise NotImplementedError('Dataset: random generation not implemented')
        else:
            if not os.path.exists(source):
                raise ValueError('Dataset: specified path does not exist')

            with open(source, 'r') as f:
                raw = f.readlines()
            for line_num, line in enumerate(raw):
                if line_num == 0:
                    # get nr of candidates
                    candidates_nr = int(line)
                elif line_num > candidates_nr + 1:
                    # extract preferences and counts
                    tokens = line.strip('\n').split(',')
                    preferences.append(tokens[1:])
                    counts.append(tokens[0])
                else:
                    # candidate mapping; skip
                    pass

        return preferences, counts


# runnable for testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='random',
                        help='choose source of the dataset (randomly generated or from file)')

    args = parser.parse_args()

    data = Dataset(source=args.dataset)
