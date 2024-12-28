"""Ayanamsa calculation input validation and error handling."""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging

class AyanamsaValidationError(Exception):
    """Custom exception for ayanamsa validation errors."""
    pass

class AyanamsaValidator:
    """Validator for ayanamsa calculations with optimized error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._valid_systems = {
            'LAHIRI', 'RAMAN', 'KRISHNAMURTI', 'DJWHAL_KHUL',
            'YUKTESHWAR', 'JN_BHASIN'
        }
        self._date_bounds = {
            'min': datetime(1, 1, 1),
            'max': datetime(9999, 12, 31, 23, 59, 59)
        }
    
    def validate_calculation_input(
        self, 
        date: datetime, 
        system: str,
        apply_nutation: bool
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate calculation inputs with optimized error handling.
        
        Args:
            date: Calculation date
            system: Ayanamsa system name
            apply_nutation: Whether to apply nutation correction
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self._validate_date(date)
            self._validate_system(system)
            return True, None
        except AyanamsaValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {str(e)}")
            return False, "Internal validation error occurred"
    
    def _validate_date(self, date: datetime) -> None:
        """Validate date is within acceptable bounds."""
        if not isinstance(date, datetime):
            raise AyanamsaValidationError("Date must be a datetime object")
        
        if date < self._date_bounds['min'] or date > self._date_bounds['max']:
            raise AyanamsaValidationError(
                f"Date must be between {self._date_bounds['min']} and {self._date_bounds['max']}"
            )
    
    def _validate_system(self, system: str) -> None:
        """Validate ayanamsa system name."""
        if not isinstance(system, str):
            raise AyanamsaValidationError("System must be a string")
        
        if system not in self._valid_systems:
            raise AyanamsaValidationError(
                f"Invalid ayanamsa system. Must be one of: {', '.join(sorted(self._valid_systems))}"
            )
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics for monitoring."""
        return {
            'valid_systems_count': len(self._valid_systems),
            'date_range_years': self._date_bounds['max'].year - self._date_bounds['min'].year,
            'min_date': self._date_bounds['min'].isoformat(),
            'max_date': self._date_bounds['max'].isoformat()
        }
