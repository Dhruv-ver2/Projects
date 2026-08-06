from django.db import models  # <-- Fix the import here!

class VocabularyWord(models.Model):  # <-- Change db.Model to models.Model
    WORD_TYPES = [
        ('Noun', 'Noun'),
        ('Verb', 'Verb'),
        ('Adjective', 'Adjective'),
        ('Adverb', 'Adverb'),
        ('Technical', 'Technical/Coding'),
    ]

    word = models.CharField(max_length=100, unique=True)  # <-- Change db to models
    word_type = models.CharField(max_length=20, choices=WORD_TYPES, default='Noun')
    meaning = models.TextField()
    example_sentence = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} ({self.word_type})"