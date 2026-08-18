from dataclasses import dataclass


@dataclass
class Competizione:
    competition_id:int
    name:str

    def __hash__(self):
        return hash(self.competition_id)
    def __eq__(self, other):
        return self.competition_id == other.competition_id

    def __str__(self):
        return f"{self.competition_id} --> {self.name}"