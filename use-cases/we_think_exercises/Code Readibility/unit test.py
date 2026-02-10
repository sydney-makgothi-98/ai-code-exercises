import unittest

from exercise_2 import calculate

class TestCompoundInterestCalculator(unittest.TestCase):
    def test_basic_interest_no_additions(self):
        # Test simple compound interest with no additional contributions
        result = calculate(
            initial_principal=1000,
            annual_rate_percent=5,
            years=1,
            annual_contribution=0,
        )

        # With 1000 principal, 5% rate, monthly compounding for 1 year
        self.assertAlmostEqual(result["final_amount"], 1051.16, places=2)
        self.assertAlmostEqual(result["interest_earned"], 51.16, places=2)
        self.assertEqual(result["total_contributions"], 1000)

    def test_with_additional_contributions(self):
        # Test with annual additional contributions
        result = calculate(
            initial_principal=1000,
            annual_rate_percent=5,
            years=3,
            annual_contribution=500,
        )

        # With additional contributions of 500 at end of years 1 and 2
        self.assertAlmostEqual(result["final_amount"], 2239.52, places=2)
        self.assertAlmostEqual(result["interest_earned"], 239.52, places=2)
        self.assertEqual(result["total_contributions"], 2000)

    def test_different_compounding_frequency(self):
        # Test with quarterly compounding
        result_quarterly = calculate(
            initial_principal=10000,
            annual_rate_percent=4,
            years=2,
            compounding_per_year=4,
        )

        # Compare with monthly compounding
        result_monthly = calculate(
            initial_principal=10000,
            annual_rate_percent=4,
            years=2,
            compounding_per_year=12,
        )

        # Quarterly should be slightly less than monthly
        self.assertLess(result_quarterly["final_amount"], result_monthly["final_amount"])

    def test_zero_interest(self):
        # Test with zero interest rate
        result = calculate(
            initial_principal=5000,
            annual_rate_percent=0,
            years=5,
            annual_contribution=1000,
        )

        # Should just be principal plus additions
        self.assertEqual(result["final_amount"], 9000)
        self.assertEqual(result["interest_earned"], 0)
        self.assertEqual(result["total_contributions"], 9000)

# Run the tests
if __name__ == "__main__":
    unittest.main()