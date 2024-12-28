"""
Unified Vedic Chart Analysis System
PGF Protocol: VCI_001
Gate: GATE_3 -> GATE_4 Transition
Version: 1.0.0

This module provides a unified interface for comprehensive Vedic chart analysis,
integrating all core calculation components:
- Ayanamsa calculations
- Divisional charts
- Planetary strengths
- House analysis
- Aspect analysis
- Yoga calculations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

from .calculations.ayanamsa import EnhancedAyanamsaManager
from .calculations.divisional_charts import DivisionalChartEngine
from .calculations.planetary_strength import PlanetaryStrengthCalculator, PlanetaryStrength
from .calculations.house_analysis import EnhancedHouseAnalysisEngine, HouseStrength
from .calculations.aspect_analysis import AspectAnalyzer, AspectInfluence
from .calculations.yoga_calculator import YogaCalculator, YogaResult

@dataclass
class ChartAnalysis:
    """Complete chart analysis results"""
    # Basic chart information
    ayanamsa_value: float
    divisional_charts: Dict[int, Dict[str, float]]
    
    # Strength calculations
    planetary_strengths: Dict[str, PlanetaryStrength]
    house_strengths: Dict[int, HouseStrength]
    
    # Relationship analysis
    aspects: Dict[tuple, AspectInfluence]
    
    # Special combinations
    yogas: List[YogaResult]
    
    # Overall chart assessment
    chart_strength: float
    primary_influences: List[str]
    recommendations: List[str]

class UnifiedAnalyzer:
    """Unified interface for comprehensive chart analysis"""
    
    def __init__(self):
        # Initialize all component calculators
        self.ayanamsa_calc = EnhancedAyanamsaManager()
        self.divisional_calc = DivisionalChartEngine()
        self.strength_calc = PlanetaryStrengthCalculator()
        self.house_analyzer = EnhancedHouseAnalysisEngine()
        self.aspect_analyzer = AspectAnalyzer()
        self.yoga_calc = YogaCalculator()
        
        # Define analysis weights
        self.analysis_weights = {
            'planetary_strength': 0.25,
            'house_strength': 0.25,
            'aspect_strength': 0.25,
            'yoga_strength': 0.25
        }
    
    def analyze_chart(
        self,
        birth_time: datetime,
        latitude: float,
        longitude: float,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> ChartAnalysis:
        """
        Perform comprehensive chart analysis
        
        Args:
            birth_time: Date and time of birth
            latitude: Birth place latitude
            longitude: Birth place longitude
            planet_positions: Dictionary of planet positions with longitudes
            
        Returns:
            ChartAnalysis object containing complete analysis
        """
        # 1. Calculate Ayanamsa
        ayanamsa = self.ayanamsa_calc.calculate_precise_ayanamsa(birth_time)
        
        # 2. Generate divisional charts
        divisions = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
        location = {'lat': latitude, 'lon': longitude}
        divisional_charts = {
            d: self.divisional_calc.calculate_chart(birth_time, d, location)
            for d in divisions
        }
        
        # 3. Calculate planetary strengths
        planetary_strengths = {}
        for planet, data in planet_positions.items():
            strength = self.strength_calc.calculate_strength(
                planet=planet,
                longitude=data['longitude'],
                chart_time=birth_time,
                house_position=int(data['longitude'] / 30) + 1
            )
            planetary_strengths[planet] = strength
        
        # 4. Analyze house strengths
        house_positions = self._get_house_positions(planet_positions)
        house_strengths = {}
        
        for house in range(1, 13):
            occupants = [
                {'name': p, **d}
                for p, d in planet_positions.items()
                if int(d['longitude'] / 30) + 1 == house
            ]
            
            # Get aspects to this house
            aspects = self._get_aspects_to_house(house, planet_positions)
            
            # Get house lord
            lord = self._get_house_lord(house, planet_positions)
            
            analysis = self.house_analyzer.analyze_house(
                house=house,
                occupants=occupants,
                aspects=aspects,
                lord=lord
            )
            house_strengths[house] = analysis
        
        # 5. Calculate aspects
        aspects = self.aspect_analyzer.calculate_all_aspects(planet_positions)
        
        # 6. Calculate yogas
        yogas = []
        yogas.extend(self.yoga_calc.calculate_raj_yoga(planet_positions, house_positions))
        yogas.extend(self.yoga_calc.calculate_dhana_yoga(planet_positions, house_positions))
        yogas.extend(self.yoga_calc.calculate_mahapurusha_yoga(planet_positions))
        
        # 7. Calculate overall chart strength
        chart_strength = self._calculate_chart_strength(
            planetary_strengths,
            house_strengths,
            aspects,
            yogas
        )
        
        # 8. Generate primary influences and recommendations
        influences = self._determine_primary_influences(
            planetary_strengths,
            house_strengths,
            yogas
        )
        recommendations = self._generate_recommendations(
            planetary_strengths,
            house_strengths,
            yogas
        )
        
        return ChartAnalysis(
            ayanamsa_value=ayanamsa,
            divisional_charts=divisional_charts,
            planetary_strengths=planetary_strengths,
            house_strengths=house_strengths,
            aspects=aspects,
            yogas=yogas,
            chart_strength=chart_strength,
            primary_influences=influences,
            recommendations=recommendations
        )
    
    def _get_house_positions(
        self,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> Dict[int, List[str]]:
        """Convert planet positions to house positions"""
        houses = {i: [] for i in range(1, 13)}
        for planet, data in planet_positions.items():
            house = int(data['longitude'] / 30) + 1
            houses[house].append(planet)
        return houses
    
    def _get_aspects_to_house(
        self,
        house: int,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Get list of aspects to a specific house"""
        aspects = []
        house_longitude = (house - 1) * 30
        
        for planet, data in planet_positions.items():
            planet_house = int(data['longitude'] / 30) + 1
            if planet_house != house:  # Don't consider self-aspect
                aspect = {
                    'planet': planet,
                    'strength': data.get('strength', 50),
                    'type': self._determine_aspect_type(
                        data['longitude'],
                        house_longitude
                    ),
                    'is_applying': self._is_aspect_applying(
                        data['longitude'],
                        house_longitude
                    )
                }
                aspects.append(aspect)
        
        return aspects
    
    def _get_house_lord(
        self,
        house: int,
        planet_positions: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Get details of house lord"""
        # Simplified lordship (using natural zodiac)
        lords = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
        }
        
        lord = lords[house]
        return {
            'planet': lord,
            'strength': planet_positions[lord].get('strength', 50),
            'house': int(planet_positions[lord]['longitude'] / 30) + 1,
            'dignity': planet_positions[lord].get('dignity', 'neutral')
        }
    
    def _determine_aspect_type(
        self,
        longitude1: float,
        longitude2: float
    ) -> str:
        """Determine type of aspect between two points"""
        diff = abs(longitude1 - longitude2) % 360
        if diff < 10 or diff > 350:
            return 'conjunction'
        elif 115 < diff < 125:  # 120° ±5°
            return 'trine'
        elif 175 < diff < 185:  # 180° ±5°
            return 'opposition'
        elif 85 < diff < 95:    # 90° ±5°
            return 'square'
        elif 55 < diff < 65:    # 60° ±5°
            return 'sextile'
        else:
            return 'none'
    
    def _is_aspect_applying(
        self,
        longitude1: float,
        longitude2: float
    ) -> bool:
        """Determine if aspect is applying or separating"""
        # This is a simplified version. In reality, we need planet speeds
        return True
    
    def _calculate_chart_strength(
        self,
        planetary_strengths: Dict[str, PlanetaryStrength],
        house_strengths: Dict[int, HouseStrength],
        aspects: Dict[tuple, AspectInfluence],
        yogas: List[YogaResult]
    ) -> float:
        """Calculate overall chart strength"""
        # Calculate component strengths
        avg_planetary_strength = sum(p.total_strength for p in planetary_strengths.values()) / len(planetary_strengths)
        avg_house_strength = sum(h.total_strength for h in house_strengths.values()) / len(house_strengths)
        avg_aspect_strength = sum(a.strength for a in aspects.values()) / len(aspects) if aspects else 50
        avg_yoga_strength = sum(y.strength for y in yogas) / len(yogas) if yogas else 50
        
        # Weight the components
        weights = {
            'planetary': 0.35,
            'house': 0.25,
            'aspect': 0.20,
            'yoga': 0.20
        }
        
        # Calculate weighted average
        total_strength = (
            avg_planetary_strength * weights['planetary'] +
            avg_house_strength * weights['house'] +
            avg_aspect_strength * weights['aspect'] +
            avg_yoga_strength * weights['yoga']
        )
        
        return total_strength

    def _determine_primary_influences(
        self,
        planetary_strengths: Dict[str, PlanetaryStrength],
        house_strengths: Dict[int, HouseStrength],
        yogas: List[YogaResult]
    ) -> List[str]:
        """Determine primary influences in the chart"""
        influences = []
        
        # Add strongest planets
        strong_planets = sorted(
            planetary_strengths.items(),
            key=lambda x: x[1].total_strength,
            reverse=True
        )[:3]
        influences.extend(f"Strong {p[0]}" for p in strong_planets)
        
        # Add strongest houses
        strong_houses = sorted(
            house_strengths.items(),
            key=lambda x: x[1].total_strength,
            reverse=True
        )[:3]
        influences.extend(f"Prominent {h[0]}th house" for h in strong_houses)
        
        # Add significant yogas
        significant_yogas = sorted(
            yogas,
            key=lambda x: x.strength,
            reverse=True
        )[:3]
        influences.extend(y.description for y in significant_yogas)
        
        return influences
    
    def _generate_recommendations(
        self,
        planetary_strengths: Dict[str, PlanetaryStrength],
        house_strengths: Dict[int, HouseStrength],
        yogas: List[YogaResult]
    ) -> List[str]:
        """Generate recommendations based on chart analysis"""
        recommendations = []
        
        # Check for weak planets
        weak_planets = [
            p for p, s in planetary_strengths.items()
            if s.total_strength < 50
        ]
        if weak_planets:
            recommendations.append(
                f"Strengthen {', '.join(weak_planets)} through appropriate remedies"
            )
        
        # Check for weak houses
        weak_houses = [
            h for h, s in house_strengths.items()
            if s.total_strength < 50
        ]
        if weak_houses:
            recommendations.append(
                f"Focus on areas related to houses {', '.join(map(str, weak_houses))}"
            )
        
        # Add yoga-based recommendations
        for yoga in yogas:
            if yoga.strength > 70:
                recommendations.append(f"Utilize {yoga.description} for maximum benefit")
        
        return recommendations
