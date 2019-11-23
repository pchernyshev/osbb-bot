import queue
import re
from typing import List, Type


def descendants(cls_):
    candidates: queue.Queue = queue.Queue()
    candidates.put(cls_)
    descendants_: List[cls_] = []
    while not candidates.empty():
        parent = candidates.get(timeout=1)
        descendants_.append(parent)
        subclasses = parent.__subclasses__()
        if subclasses:
            for subclass in subclasses:
                candidates.put(subclass)
        if cls_ in descendants_:
            descendants_.remove(cls_)
    return descendants_


class Discoverable:
    @classmethod
    def responds_to(cls, query: str) -> bool:
        """
        Queries object with query in order to get boolean response.
        Only objects with `TYPE_QUALIFIER` class attribute  are supported.
        Class attribute can either be a list of valid values, or regex.

        Args:
            query (str): query

        Returns:
            bool: verdict if object responded.
        """
        supported_quailifier_usage = (' can either be'
                                      ' plain string, regex string'
                                      ' or list of acceptable values')

        qualifier_reference = "TYPE_QUALIFIER"
        qualifier = getattr(cls, qualifier_reference, None)
        if qualifier:
            if isinstance(qualifier, str):
                valid = re.compile(qualifier)
                return bool(valid.match(query))
            elif isinstance(qualifier, list):
                return query in qualifier
            else:
                raise NotImplementedError(qualifier_reference
                                          + supported_quailifier_usage)
        else:
            raise AttributeError('An implementation has to define '
                                 + qualifier_reference + ' which'
                                 + supported_quailifier_usage)

    @classmethod
    def __descendants__(cls) -> List[Type]:
        """ __descendants__() -> list of immediate descendants (recursive)"""
        return descendants(cls)
