#!/usr/bin/env python3
"""
Test Runner for Vedic Astrology System
Executes test suites and generates performance reports
"""

import pytest
import psutil
import time
import json
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Test execution and performance monitoring framework"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'test_results': {},
            'performance_metrics': {}
        }
    
    def _get_system_info(self):
        """Gather system information"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def run_tests(self):
        """Execute test suite with performance monitoring"""
        test_start = time.time()
        initial_memory = psutil.Process().memory_info().rss
        
        # Run pytest with detailed output
        pytest_args = [
            '-v',
            '--durations=10',
            '--maxfail=5',
            'test_ayanamsa.py'
        ]
        
        test_result = pytest.main(pytest_args)
        
        # Calculate metrics
        test_duration = time.time() - test_start
        final_memory = psutil.Process().memory_info().rss
        memory_used = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        self.results['performance_metrics'] = {
            'test_duration_seconds': round(test_duration, 2),
            'memory_usage_mb': round(memory_used, 2),
            'peak_memory_mb': round(psutil.Process().memory_info().peak_wset / (1024 * 1024), 2)
        }
        
        self.results['test_results'] = {
            'exit_code': test_result,
            'status': 'Success' if test_result == 0 else 'Failed'
        }
        
        return self.results
    
    def generate_report(self):
        """Generate detailed test report"""
        report_path = Path('test_reports')
        report_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_path / f'test_report_{timestamp}.json'
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=4)
        
        return report_file

if __name__ == '__main__':
    runner = TestRunner()
    results = runner.run_tests()
    report_file = runner.generate_report()
    
    print("\nTest Execution Summary:")
    print(f"Status: {results['test_results']['status']}")
    print(f"Duration: {results['performance_metrics']['test_duration_seconds']}s")
    print(f"Memory Usage: {results['performance_metrics']['memory_usage_mb']}MB")
    print(f"Report saved to: {report_file}")
