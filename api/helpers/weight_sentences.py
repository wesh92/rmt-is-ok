def weighting_sentences(percentage: float):
    if percentage <= -1 and percentage >= -10:
        return "Slight Recommendation"
    elif percentage <= -11 and percentage >= -20:
        return "Moderate Recommendation"
    elif percentage <= -21 and percentage >= -30:
        return "Heavy Recommendation"
    elif percentage <= -31:
        return "Very Heavy Recommendation"
    elif percentage >= 0 and percentage <= 10:
        return "Slight Recommendation"
    elif percentage >= 11 and percentage <= 20:
        return "Moderate Recommendation"
    elif percentage >= 21 and percentage <= 30:
        return "Heavy Recommendation"
    elif percentage >= 31:
        return "Very Heavy Recommendation"
