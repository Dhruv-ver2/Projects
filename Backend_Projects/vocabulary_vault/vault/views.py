from django.shortcuts import render, redirect, get_object_or_404
from .models import VocabularyWord

# 1. READ & CREATE (Using Raw HTML Inputs)
def dashboard_view(request):
    if request.method == "POST":
        # Extract strings manually from the HTML input 'name' attributes
        input_word = request.POST.get('form_word')
        input_type = request.POST.get('form_type')
        input_meaning = request.POST.get('form_meaning')
        input_example = request.POST.get('form_example')
        
        # Save directly to db.sqlite3 using the ORM creation command
        VocabularyWord.objects.create(
            word=input_word,
            word_type=input_type,
            meaning=input_meaning,
            example_sentence=input_example
        )
        return redirect('/')
        
    # GET State: Pull all records from the database, newest first
    all_words = VocabularyWord.objects.all().order_by('-date_added')
    return render(request, 'index.html', {'words': all_words})


# 2. DELETE (Using Dynamic URL ID)
def delete_word_view(request, word_id):
    word_record = get_object_or_404(VocabularyWord, id=word_id)
    word_record.delete()
    return redirect('/')


# 3. UPDATE (Using Raw HTML Inputs + Instance Saving)
def update_word_view(request, word_id):
    word_record = get_object_or_404(VocabularyWord, id=word_id)
    
    if request.method == "POST":
        # Overwrite the existing object parameters with the updated inputs
        word_record.word_type = request.POST.get('form_type')
        word_record.meaning = request.POST.get('form_meaning')
        word_record.example_sentence = request.POST.get('form_example')
        
        word_record.save() # Commit the changes to the database file
        return redirect('/')
        
    return render(request, 'update.html', {'word_record': word_record})