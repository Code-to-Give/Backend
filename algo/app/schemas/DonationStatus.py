from enum import Enum

class DonationStatus(Enum):
    READY = 'Ready'
    ALLOCATED = 'Allocated'
    ACCEPTED = 'Accepted'
    COLLECTED = 'Collected'