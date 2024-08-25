from enum import Enum

class FoodType(str, Enum):
    HALAL = 'halal'
    NONE = 'none'
    VEGETARIAN = 'vegetarian'
    NON_BEEF = 'no-beef'