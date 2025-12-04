from django.shortcuts import render, redirect
from django.db.models import Count, Avg, Q, Sum
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import re
from .models import Professor, Comment
from .forms import FeedbackForm
from .utils.sentiment_analyzer import analyze_comment_sentiment

def home(request):
    # Annotate professors with average sentiment score and total comments to display badges on the home page
    # Only show professors who have at least one comment (avoid rendering unintended/placeholder records)
    professors = Professor.objects.annotate(
        total_comments=Count('comments'),
        avg_sentiment_score=Avg('comments__sentiment_score')
    ).filter(total_comments__gt=0)

    # Normalize None to 0 for template friendliness
    for p in professors:
        if getattr(p, 'avg_sentiment_score') is None:
            p.avg_sentiment_score = 0
        if getattr(p, 'total_comments') is None:
            p.total_comments = 0
        # compute a percentage (0-100) from avg sentiment (-1..1)
        try:
            pct = int(max(0, min(100, ((p.avg_sentiment_score + 1) / 2) * 100)))
        except Exception:
            pct = 0
        p.score_pct = pct

    return render(request, 'feedback/home.html', {'professors': professors})

def dashboard(request):
    # Overall statistics (fast counts)
    total_professors = Professor.objects.count()
    total_comments = Comment.objects.count()

    # Sentiment distribution across all comments (single query)
    sentiment_stats = Comment.objects.aggregate(
        positive=Count('id', filter=Q(sentiment_label='positive')),
        negative=Count('id', filter=Q(sentiment_label='negative')),
        neutral=Count('id', filter=Q(sentiment_label='neutral'))
    )

    # Annotate professors with aggregated sentiment counts and average score to avoid N+1 queries
    annotated_profs = Professor.objects.annotate(
        total=Count('comments'),
        positive=Count('comments', filter=Q(comments__sentiment_label='positive')),
        negative=Count('comments', filter=Q(comments__sentiment_label='negative')),
        neutral=Count('comments', filter=Q(comments__sentiment_label='neutral')),
        avg_sentiment_score=Avg('comments__sentiment_score')
    )

    professors_with_stats = []
    for p in annotated_profs:
        total = p.total or 0
        positive = p.positive or 0
        negative = p.negative or 0
        neutral = p.neutral or 0
        avg_score = p.avg_sentiment_score or 0

        positive_ratio = (positive / total) * 100 if total > 0 else 0

        professors_with_stats.append({
            'professor': p,
            'stats': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'total': total
            },
            'positive_ratio': positive_ratio,
            'avg_sentiment_score': avg_score,
            # precompute a CSS-safe width and background color to avoid templating logic inside inline styles
            'score_pct': int(max(0, min(100, ((avg_score + 1) / 2) * 100))),
            'score_style': None,
        })

    # compute score_style for each item (so templates can use a safe inline style)
    for item in professors_with_stats:
        avg_score = item['avg_sentiment_score']
        if avg_score > 0.3:
            color = '#28a745'
        elif avg_score > -0.3:
            color = '#ffc107'
        else:
            color = '#dc3545'
        item['score_style'] = f"width: {item['score_pct']}%; background: {color};"

    # Sort by average sentiment score (best first)
    professors_with_stats.sort(key=lambda x: x['avg_sentiment_score'], reverse=True)

    # Trend Over Time Data (Last 30 days) - keep as-is but use efficient filtering
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trend_data = []

    # Pre-fetch daily counts using a simple loop; this is small (30 iterations) and fast enough
    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_comments = Comment.objects.filter(created_at__date=day.date())

        day_stats = day_comments.aggregate(
            count=Count('id'),
            avg_score=Avg('sentiment_score'),
            positive=Count('id', filter=Q(sentiment_label='positive')),
            negative=Count('id', filter=Q(sentiment_label='negative')),
            neutral=Count('id', filter=Q(sentiment_label='neutral'))
        )

        trend_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'display_date': day.strftime('%b %d'),
            'count': day_stats['count'] or 0,
            'avg_score': day_stats['avg_score'] or 0,
            'positive': day_stats['positive'] or 0,
            'negative': day_stats['negative'] or 0,
            'neutral': day_stats['neutral'] or 0,
        })

    # Word Cloud Data (Most frequent words across all comments) - limit to a reasonable subset
    all_comments = Comment.objects.only('comment_text')
    word_frequency = get_word_frequency_from_comments(all_comments)

    # Recent comments (fast, single query with related professor)
    recent_comments = Comment.objects.select_related('professor').order_by('-created_at')[:5]

    context = {
        'total_professors': total_professors,
        'total_comments': total_comments,
        'sentiment_stats': sentiment_stats,
        'professors_with_stats': professors_with_stats,
        'recent_comments': recent_comments,
        'trend_data': trend_data,
        'word_frequency': word_frequency[:20],  # Top 20 words for word cloud
        # raw sentiment scores for histogram chart
        'sentiment_scores': list(Comment.objects.values_list('sentiment_score', flat=True)),
    }

    return render(request, 'feedback/dashboard.html', context)

def get_word_frequency_from_comments(comments, top_n=50):
    """Extract most frequent words from comments for word cloud"""
    all_text = " ".join([comment.comment_text for comment in comments])
    
    # Clean and tokenize text
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'but', 'for', 'with', 'that', 'this', 'from', 'have', 'has',
        'was', 'were', 'are', 'you', 'your', 'they', 'their', 'there', 'what',
        'which', 'who', 'when', 'where', 'why', 'how', 'just', 'like', 'then',
        'than', 'very', 'really', 'quite', 'some', 'more', 'most', 'about',
        'because', 'should', 'would', 'could', 'will', 'can', 'may', 'might'
    }
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count frequency
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

def submit_feedback(request):
    # Allow optional pre-selection via GET param: ?prof=<id>
    prof_id = request.GET.get('prof')
    preselected_professor = None

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Get form data
            professor = form.cleaned_data['professor']
            student_name = form.cleaned_data['student_name']
            comment_text = form.cleaned_data['comment_text']
            
            # AI Sentiment Analysis
            sentiment_score, sentiment_label = analyze_comment_sentiment(comment_text)
            
            # Save to database
            comment = Comment(
                professor=professor,
                student_name=student_name,
                comment_text=comment_text,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label
            )
            comment.save()
            
            # Success message with sentiment results
            messages.success(request, 
                f'✅ Feedback submitted successfully! '
                f'Sentiment: {sentiment_label.title()} '
                f'(Score: {sentiment_score:.2f})'
            )
            return redirect('submit_feedback')
    else:
        # If a professor id is provided via GET, try to pre-fill the form
        if prof_id:
            try:
                preselected_professor = Professor.objects.get(id=prof_id)
                form = FeedbackForm(initial={'professor': preselected_professor.id})
            except Professor.DoesNotExist:
                form = FeedbackForm()
        else:
            form = FeedbackForm()
    
    return render(request, 'feedback/submit_feedback.html', {
        'form': form,
        'preselected_professor': preselected_professor
    })

def professor_detail(request, professor_id):
    professor = Professor.objects.get(id=professor_id)
    comments = professor.comments.all().order_by('-created_at')
    stats = professor.get_sentiment_stats()
    
    # Professor-specific analytics
    avg_score = Comment.objects.filter(professor=professor).aggregate(
        Avg('sentiment_score')
    )['sentiment_score__avg'] or 0
    
    # Word frequency for this professor
    word_frequency = get_word_frequency_from_comments(comments)
    
    # Trend data for this professor
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trend_data = []
    
    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        day_comments = comments.filter(created_at__date=day.date())
        
        day_stats = day_comments.aggregate(
            count=Count('id'),
            avg_score=Avg('sentiment_score')
        )
        
        trend_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'display_date': day.strftime('%b %d'),
            'count': day_stats['count'] or 0,
            'avg_score': day_stats['avg_score'] or 0,
        })
    
    context = {
        'professor': professor,
        'comments': comments,
        'stats': stats,
        'avg_score': avg_score,
        'word_frequency': word_frequency[:20],
        'trend_data': trend_data,
    }
    return render(request, 'feedback/professor_detail.html', context)