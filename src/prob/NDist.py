import scipy.stats as stats
from .config import GAME_SLIDERS

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
        return stats.norm.ppf(percentile, loc=self.mu, scale=self.sigma)