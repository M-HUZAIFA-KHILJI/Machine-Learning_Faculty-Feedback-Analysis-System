from django.db import models

class Professor(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def get_sentiment_stats(self):
        """Calculate sentiment statistics for this professor"""
        comments = self.comments.all()
        if not comments:
            return {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
        
        positive = comments.filter(sentiment_label='positive').count()
        negative = comments.filter(sentiment_label='negative').count()
        neutral = comments.filter(sentiment_label='neutral').count()
        
        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "total": comments.count()
        }


class Comment(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='comments')
    student_name = models.CharField(max_length=100, blank=True, null=True)
    comment_text = models.TextField()
    sentiment_score = models.FloatField()
    sentiment_label = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment for {self.professor.name} by {self.student_name or 'Anonymous'}"