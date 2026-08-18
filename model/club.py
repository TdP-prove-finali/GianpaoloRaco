from dataclasses import dataclass


@dataclass
class Club:
    club_id:int
    name:str

    def __hash__(self):
        return hash(self.club_id)

    def __eq__(self, other):
        return self.club_id == other.club_id

    def __str__(self):
        return f"{self.club_id} --> {self.name}"
