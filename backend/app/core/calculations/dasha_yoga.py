"""
Dasha Yoga calculations and interpretations
"""
from typing import Dict, List, Tuple
from decimal import Decimal

class DashaYoga:
    """
    Calculate and interpret Dasha Yogas (planetary combinations during Dasha periods)
    """
    
    # Yoga definitions and their effects
    yoga_definitions = {
        'Raja Yoga': {
            'combinations': [
                ('Sun', 'Jupiter'),
                ('Moon', 'Jupiter'),
                ('Venus', 'Jupiter')
            ],
            'effects': [
                'Rise in position and authority',
                'Success in career and public life',
                'Recognition and honors'
            ]
        },
        'Dhana Yoga': {
            'combinations': [
                ('Jupiter', 'Venus'),
                ('Mercury', 'Venus'),
                ('Moon', 'Venus')
            ],
            'effects': [
                'Financial prosperity',
                'Material gains',
                'Business success'
            ]
        },
        'Vidya Yoga': {
            'combinations': [
                ('Jupiter', 'Mercury'),
                ('Moon', 'Mercury'),
                ('Venus', 'Mercury')
            ],
            'effects': [
                'Academic success',
                'Intellectual achievements',
                'Success in education'
            ]
        },
        'Karma Yoga': {
            'combinations': [
                ('Saturn', 'Mars'),
                ('Saturn', 'Sun'),
                ('Mars', 'Sun')
            ],
            'effects': [
                'Professional success through hard work',
                'Recognition in career',
                'Leadership positions'
            ]
        }
    }
    
    @classmethod
    def find_active_yogas(cls, 
                         main_planet: str, 
                         sub_planet: str, 
                         prat_planet: str = None) -> List[Dict[str, List[str]]]:
        """
        Find active Yogas based on the current Dasha period planets
        
        Args:
            main_planet: Mahadasha lord
            sub_planet: Antardasha lord
            prat_planet: Pratyantardasha lord (optional)
            
        Returns:
            List of active yogas with their effects
        """
        active_yogas = []
        planet_pairs = [
            (main_planet, sub_planet),
            (main_planet, prat_planet) if prat_planet else None,
            (sub_planet, prat_planet) if prat_planet else None
        ]
        
        for yoga_name, yoga_info in cls.yoga_definitions.items():
            for pair in planet_pairs:
                if not pair:
                    continue
                    
                # Check if this pair forms the yoga (in either order)
                if pair in yoga_info['combinations'] or tuple(reversed(pair)) in yoga_info['combinations']:
                    active_yogas.append({
                        'name': yoga_name,
                        'effects': yoga_info['effects'],
                        'planets': list(pair)
                    })
                    
        return active_yogas
    
    @classmethod
    def calculate_yoga_strength(cls, 
                              yoga_name: str, 
                              planet_positions: Dict[str, float]) -> Decimal:
        """
        Calculate the strength of a yoga based on planetary positions
        
        Args:
            yoga_name: Name of the yoga
            planet_positions: Dictionary of planet longitudes
            
        Returns:
            Strength of the yoga (0.0 to 1.0)
        """
        base_strength = Decimal('0.5')  # Default medium strength
        
        # Factors that strengthen a yoga
        strengthening_factors = {
            'mutual_aspect': Decimal('0.2'),  # Planets aspecting each other
            'exaltation': Decimal('0.3'),     # Planet in exaltation
            'own_sign': Decimal('0.2'),       # Planet in own sign
            'friendly_sign': Decimal('0.1'),  # Planet in friendly sign
        }
        
        # Factors that weaken a yoga
        weakening_factors = {
            'debilitation': Decimal('-0.3'),  # Planet in debilitation
            'combust': Decimal('-0.2'),       # Planet combust
            'enemy_sign': Decimal('-0.1'),    # Planet in enemy sign
        }
        
        # Apply strengthening and weakening factors based on planetary positions
        # This is a simplified calculation - in practice, you would check actual
        # planetary positions against their exaltation, debilitation points, etc.
        
        return max(min(base_strength, Decimal('1.0')), Decimal('0.0'))
    
    @classmethod
    def get_yoga_predictions(cls, 
                           active_yogas: List[Dict[str, List[str]]], 
                           planet_positions: Dict[str, float]) -> List[Dict[str, any]]:
        """
        Generate detailed predictions for active yogas
        
        Args:
            active_yogas: List of active yogas
            planet_positions: Dictionary of planet longitudes
            
        Returns:
            List of predictions with timing and strength
        """
        predictions = []
        
        for yoga in active_yogas:
            strength = cls.calculate_yoga_strength(yoga['name'], planet_positions)
            
            prediction = {
                'yoga_name': yoga['name'],
                'strength': float(strength),
                'effects': yoga['effects'],
                'timing': {
                    'best_period': 'First half of dasha',  # Simplified - would need more complex calculation
                    'peak_effects': 'Middle of dasha'      # Simplified - would need more complex calculation
                },
                'recommendations': [
                    f"Best time to initiate {yoga['name'].lower()} related activities",
                    f"Focus on {', '.join(yoga['effects'][:2]).lower()}"
                ]
            }
            
            predictions.append(prediction)
            
        return predictions
