from abc import ABCMeta, abstractmethod


class MatchData(metaclass=ABCMeta):
    @abstractmethod
    def match_data(self):
        pass
