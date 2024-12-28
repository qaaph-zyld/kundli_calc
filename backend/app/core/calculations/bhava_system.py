"""
Bhava (House) Analysis System for Vedic Astrology
"""
from typing import Dict, List, Tuple, Optional
from decimal import Decimal

class BhavaSystem:
    """
    Implements comprehensive Bhava (House) analysis including aspects,
    strengths, and relationships between houses and planets
    """
    
    # House significations and natural characteristics
    house_significations = {
        1: ['self', 'personality', 'health', 'appearance', 'beginnings'],
        2: ['wealth', 'family', 'speech', 'resources', 'investments'],
        3: ['siblings', 'courage', 'communication', 'short travels', 'skills'],
        4: ['mother', 'happiness', 'home', 'education', 'property'],
        5: ['children', 'intelligence', 'creativity', 'romance', 'speculation'],
        6: ['enemies', 'diseases', 'debts', 'service', 'obstacles'],
        7: ['spouse', 'partnership', 'business', 'foreign travels', 'public'],
        8: ['longevity', 'occult', 'transformation', 'research', 'inheritance'],
        9: ['fortune', 'dharma', 'higher learning', 'father', 'spirituality'],
        10: ['career', 'status', 'authority', 'reputation', 'government'],
        11: ['gains', 'aspirations', 'friends', 'elder siblings', 'success'],
        12: ['losses', 'expenses', 'liberation', 'foreign lands', 'isolation']
    }
    
    # Aspect relationships between houses
    house_aspects = {
        1: [7],      # 7th aspect
        2: [8],      # 7th aspect
        3: [9],      # 7th aspect
        4: [10],     # 7th aspect
        5: [11],     # 7th aspect
        6: [12],     # 7th aspect
        7: [1],      # 7th aspect
        8: [2],      # 7th aspect
        9: [3],      # 7th aspect
        10: [4],     # 7th aspect
        11: [5],     # 7th aspect
        12: [6]      # 7th aspect
    }
    
    # House relationships (friendly, neutral, enemy)
    house_relationships = {
        'trine': [5, 9],     # 120 degrees
        'square': [4, 10],   # 90 degrees
        'sextile': [3, 11],  # 60 degrees
        'opposition': [7],    # 180 degrees
    }
    
    @classmethod
    def calculate_house_strength(cls, 
                               house: int, 
                               planet_positions: Dict[str, float],
                               aspects: Dict[str, List[int]]) -> Dict[str, any]:
        """
        Calculate strength and influences for a specific house
        
        Args:
            house: House number (1-12)
            planet_positions: Dictionary of planet positions
            aspects: Dictionary of aspects to the house
            
        Returns:
            Dictionary containing house strength analysis
        """
        if not 1 <= house <= 12:
            raise ValueError(f"Invalid house number: {house}")
            
        strength = Decimal('0.5')  # Base strength
        influences = []
        
        # Natural significations
        significations = cls.house_significations.get(house, [])
        
        # Aspect influences
        aspect_influences = []
        for planet, aspected_houses in aspects.items():
            if house in aspected_houses:
                aspect_influences.append({
                    'planet': planet,
                    'type': 'aspect',
                    'effect': 'strengthening' if planet in ['Jupiter', 'Venus'] else 'mixed'
                })
                strength += Decimal('0.1')
        
        # Occupying planets
        occupants = []
        for planet, position in planet_positions.items():
            house_position = ((position // 30) + 1)
            if house_position == house:
                occupants.append(planet)
                strength += Decimal('0.2')
        
        # House lord strength
        house_lord = cls.get_house_lord(house)
        if house_lord in planet_positions:
            lord_house = ((planet_positions[house_lord] // 30) + 1)
            lord_strength = cls.analyze_lord_placement(house, lord_house)
            strength += lord_strength
        
        return {
            'strength': min(strength, Decimal('1.0')),
            'significations': significations,
            'occupants': occupants,
            'aspects': aspect_influences,
            'lord': house_lord,
            'relationships': cls.get_house_relationships(house)
        }
    
    @classmethod
    def get_house_lord(cls, house: int) -> str:
        """Get natural lord of the house"""
        # Simplified natural lordship
        lords = {
            1: 'Mars',
            2: 'Venus',
            3: 'Mercury',
            4: 'Moon',
            5: 'Sun',
            6: 'Mercury',
            7: 'Venus',
            8: 'Mars',
            9: 'Jupiter',
            10: 'Saturn',
            11: 'Saturn',
            12: 'Jupiter'
        }
        return lords.get(house, '')
    
    @classmethod
    def analyze_lord_placement(cls, 
                             house: int, 
                             lord_house: int) -> Decimal:
        """Analyze strength of house lord placement"""
        if house == lord_house:
            return Decimal('0.3')  # Lord in own house
            
        # Check relationship between houses
        relationship = cls.get_house_relationship(house, lord_house)
        
        strengths = {
            'trine': Decimal('0.2'),
            'sextile': Decimal('0.15'),
            'square': Decimal('-0.1'),
            'opposition': Decimal('-0.2')
        }
        
        return strengths.get(relationship, Decimal('0'))
    
    @classmethod
    def get_house_relationship(cls, 
                             house1: int, 
                             house2: int) -> str:
        """Get relationship between two houses"""
        difference = abs(house1 - house2)
        if difference in [4, 8]:
            return 'square'
        elif difference in [5, 9]:
            return 'trine'
        elif difference in [3, 11]:
            return 'sextile'
        elif difference == 7:
            return 'opposition'
        else:
            return 'neutral'
    
    @classmethod
    def get_house_relationships(cls, house: int) -> Dict[str, List[int]]:
        """Get all relationships for a house"""
        relationships = {}
        for rel_type, offsets in cls.house_relationships.items():
            related_houses = []
            for offset in offsets:
                related_house = ((house + offset - 1) % 12) + 1
                related_houses.append(related_house)
            relationships[rel_type] = related_houses
        return relationships
    
    @classmethod
    def analyze_bhava_chart(cls, 
                           planet_positions: Dict[str, float],
                           aspects: Dict[str, List[int]]) -> Dict[str, any]:
        """
        Perform comprehensive analysis of all houses
        
        Args:
            planet_positions: Dictionary of planet positions
            aspects: Dictionary of aspects
            
        Returns:
            Dictionary containing analysis of all houses
        """
        analysis = {}
        
        # Analyze each house
        for house in range(1, 13):
            analysis[house] = cls.calculate_house_strength(
                house,
                planet_positions,
                aspects
            )
        
        # Find strongest and weakest houses
        strengths = {h: data['strength'] for h, data in analysis.items()}
        strongest = max(strengths.items(), key=lambda x: x[1])[0]
        weakest = min(strengths.items(), key=lambda x: x[1])[0]
        
        return {
            'house_analysis': analysis,
            'strongest_house': strongest,
            'weakest_house': weakest,
            'chart_balance': sum(strengths.values()) / 12
        }
