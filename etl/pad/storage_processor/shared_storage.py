import os
from abc import ABC, abstractmethod

from pad.common.utils import classproperty
from pad.db.sql_item import SimpleSqlItem


class ServerDependentSqlItem(SimpleSqlItem, ABC):
    @property
    @abstractmethod
    def BASE_TABLE(self):
        ...

    @classproperty
    def TABLE(cls) -> str:
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return cls.BASE_TABLE + '_na'
        # elif server.upper() == "JP":
        #    return cls.BASE_TABLE + '_jp'
        # elif server.upper() == "KR":
        #    return cls.BASE_TABLE + '_kr'
        else:
            return cls.BASE_TABLE
