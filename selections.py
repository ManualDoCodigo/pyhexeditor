class Selections:
    def __init__(self) -> None:
        self.selections = []

    def add(self, start, end):
        selection = Selection(start, end)
        self.selections.append(selection)

    def isSelected(self, address):
        for selection in self.selections:
            if selection.contains(address):
                return True
        return False


class Selection:
    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end

    def contains(self, address):
        return address >= self.start and address <= self.end
