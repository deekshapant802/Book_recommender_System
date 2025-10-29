from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=["GET", "POST"])
def recommend():
    if request.method == "POST":
        user_input = request.form.get('user_input')
    else:  # GET request (when you type URL directly)
        user_input = request.args.get('user_input')

    if not user_input:
        return render_template('recommend.html', data=[], message="Please enter a book title.")

    user_input = user_input.strip().lower()

    # Create a mapping of lowercase titles to original titles
    title_mapping = {title.lower(): title for title in pt.index}

    if user_input not in title_mapping:
        return render_template('recommend.html',
                               data=[],
                               message=f"❌ '{user_input}' not found. Please try another book.")

    # Get the original title from the mapping
    original_title = title_mapping[user_input]

    # Find the index of the book in the pivot table
    index = np.where(pt.index == original_title)[0][0]

    # Get similarity scores for this book
    similar_items = sorted(list(enumerate(similarity_scores[index])),
                           key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)