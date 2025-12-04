# feedback/utils/sentiment_analyzer.py
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize analyzer once (it's expensive to create)
analyzer = SentimentIntensityAnalyzer()

def analyze_comment_sentiment(comment_text):
    """
    Analyze sentiment of professor feedback comment
    
    Args:
        comment_text (str): The student's comment
    
    Returns:
        tuple: (sentiment_score, sentiment_label)
            - sentiment_score: float between -1.0 to +1.0
            - sentiment_label: 'positive', 'negative', or 'neutral'
    """
    # Get sentiment scores
    scores = analyzer.polarity_scores(comment_text)
    compound_score = scores['compound']
    
    # Classify sentiment
    if compound_score >= 0.05:
        label = 'positive'
    elif compound_score <= -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    
    return compound_score, label  # Make sure this return statement exists!