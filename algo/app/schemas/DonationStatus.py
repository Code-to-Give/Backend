from enum import Enum


class DonationStatus(str, Enum):
    READY = 'Ready'
    ALLOCATED = 'Allocated'
    ACCEPTED = 'Accepted'
    COLLECTED = 'Collected'
    REJECTED = 'Rejected'
