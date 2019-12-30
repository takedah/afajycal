from afajycal.models import ScheduleFactory


class Calendar:
    def __init__(self, source):
        """
        Args:
            source (:obj:`MatchData`): MatchDataクラスのサブクラスのオブジェクト。

        """
        schedule_factory = ScheduleFactory()
        for row in source.match_data:
            schedule_factory.create(row)
        self.__schedules = schedule_factory.schedules

    @property
    def schedules(self):
        return self.__schedules
