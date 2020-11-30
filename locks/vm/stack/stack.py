from typing import Any

class Stack:
    def __init__(self):
        self._list = []

    def push(self, e: Any) -> None:
        self._list.append(e)

    def pop(self) -> Any:
        return self._list.pop()

    def peek(self) -> Any:
        if len(self._list) == 0:
            return None
        return self._list[-1]