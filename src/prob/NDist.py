import scipy.stats as stats
import numpy as np
import random
from .config import GAME_SLIDERS, MAX_PCT, MIN_PCT

class NDist:
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

    def calculate_pdf(self, percentile):
        # Calculate the Z-score corresponding to the given percentile
        z_score = stats.norm.ppf(percentile)
        # Calculate the PDF for the given Z-score
        pdf_value = stats.norm.pdf(z_score, loc=self.mu, scale=self.sigma)
        return pdf_value
    
    def calculate_x(self, percentile):
        """
            Returns the x value given the percentile and the settings mean and standard deviation.
        """
        return NDist(stats.norm.ppf(percentile, loc=self.mu, scale=self.sigma), self.sigma)
    
    def calculate_random_percentile(self, mn=MIN_PCT, mx=MAX_PCT, rnd=2, mode="normal"):
        """
            Generates a random value from a normal distribution.  
        """
        if mode == "normal":
            val = np.random.normal(loc=self.mu, scale=self.sigma)
        elif mode == "skew": # Used for choosing random player numbers
            # Parameters for the Beta distribution
            alpha = 2.0  # Shape parameter
            beta = 5.0   # Shape parameter
            low = 0      # Lower bound (cutoff near zero)
            high = 99    # Upper bound

            # Generate random values from the Beta distribution
            random_values = low + (high - low) * np.random.beta(alpha, beta, 100)
            val = random.choice(random_values)

        val = max(val, mn)
        val = min(val, mx)
        return round(val, rnd)