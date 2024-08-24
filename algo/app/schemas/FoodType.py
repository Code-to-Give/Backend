from enum import Enum

class FoodType(str, Enum):
    HALAL = 'Halal'
    NON_HALAL = 'Non-Halal'
    VEGETARIAN = 'Vegetarian'
    VEGAN = 'Vegan'
    NON_BEEF = 'Non-Beef'