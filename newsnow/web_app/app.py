import json
import os
import sys
from flask import Flask, render_template, redirect, url_for

# Add the parent directory (newsnow) to sys.path to find the news_fetchers module
# This allows us to import modules from the 'news_fetchers' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from news_fetchers.general_news_fetcher import fetch_general_news
except ImportError:
    # Fallback for environments where the above path adjustment might not be enough
    # or for local testing where newsnow might already be in PYTHONPATH.
    # This is a simple fallback, a more robust solution might involve packaging.
    if 'news_fetchers.general_news_fetcher' not in sys.modules:
        print("Attempting fallback import for news_fetchers.general_news_fetcher")
        # This assumes 'newsnow' is the project root and is in PYTHONPATH
        from newsnow.news_fetchers.general_news_fetcher import fetch_general_news


# Initialize a Flask application
# template_folder and static_folder are relative to the 'web_app' directory where app.py is located.
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Define the path to the JSON data file, relative to this app.py file
# This path is used by both index() and refresh_news()
JSON_DATA_FILEPATH = os.path.join(os.path.dirname(__file__), '../data/general_news.json')


@app.route('/')
def index():
    """
    Serves the main page with news articles.
    Reads news articles from a JSON file and passes them to the template.
    """
    news_articles = []
    try:
        with open(JSON_DATA_FILEPATH, 'r', encoding='utf-8') as f:
            news_articles = json.load(f)
    except FileNotFoundError:
        print(f"Error: The data file '{JSON_DATA_FILEPATH}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{JSON_DATA_FILEPATH}'.")
    except Exception as e:
        print(f"An unexpected error occurred while reading '{JSON_DATA_FILEPATH}': {e}")

    return render_template('index.html', articles=news_articles)

@app.route('/refresh_news')
def refresh_news():
    """
    Fetches fresh news using fetch_general_news, saves it to the JSON file,
    and then redirects back to the index page.
    """
    print("Attempting to refresh news...")
    try:
        news_items = fetch_general_news()  # Fetches data
        if news_items:
            # Ensure the directory for the JSON file exists
            os.makedirs(os.path.dirname(JSON_DATA_FILEPATH), exist_ok=True)
            
            # Save the fetched news items to the JSON file
            with open(JSON_DATA_FILEPATH, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, indent=4, ensure_ascii=False)
            print(f"News refreshed and saved, {len(news_items)} items to {JSON_DATA_FILEPATH}.")
        else:
            print("News fetcher ran, but no items were returned to save.")
            # Optionally, clear the existing file if no news is returned
            # or leave it as is, depending on desired behavior.
            # For now, we'll leave it as is.
    except Exception as e:
        print(f"Error during news refresh or saving: {e}")
        # Log the full traceback for more detailed debugging if needed
        import traceback
        traceback.print_exc()

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Runs the Flask development server
    # Debug mode is on for development for auto-reloading and error messages.
    # Host '0.0.0.0' makes it accessible on the network if needed.
    app.run(debug=True, host='0.0.0.0', port=5000)
