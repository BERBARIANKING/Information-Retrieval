from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from imdb import IMDb

app = Flask(__name__, template_folder='templates', static_folder='static')

RESULTS_PER_PAGE = 10

# Create an instance of IMDb class
ia = IMDb()

# Define a basic boolean indexer function
def boolean_indexer(query, movies):
    # Tokenize the query
    query_tokens = query.lower().split()

    # List to store matching movies
    matching_movies = []

    # Iterate through movies
    for movie in movies:
        # Get movie title and plot
        title = movie['title'].lower()
        plot = movie.get('plot', [''])[0].lower() if 'plot' in movie else ''

        # Check if all query tokens are present in either title or plot
        if all(token in title or token in plot for token in query_tokens):
            movie['matches_query'] = True
            matching_movies.append(movie)
        else:
            movie['matches_query'] = False

    return matching_movies

# Main route for displaying search results
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        filter_option = request.form.get('filter', 'movies')
        page = int(request.form.get('page', 1))
        
        # Search for movies or documentaries based on the filter option
        if filter_option == 'movies':
            movies = ia.search_movie(query)
        elif filter_option == 'documentaries':
            movies = scrape_national_geographic_documentaries()
        else:
            movies = []

        # Apply boolean indexer
        matching_movies = boolean_indexer(query, movies)
        
        # Slice the search results to paginate
        start_index = (page - 1) * RESULTS_PER_PAGE
        end_index = start_index + RESULTS_PER_PAGE
        paginated_movies = matching_movies[start_index:end_index]
        
        # Check if there are more results available
        more_results_available = len(matching_movies) > end_index
        
        # Pass the search results, query, filter option, and other data to the template
        return render_template('test.html', search_results=paginated_movies,
                               page=page, more_results_available=more_results_available,
                               query=query, filter_option=filter_option)
    
    # If it's a GET request or no movies found
    return render_template('test.html', search_results=[], page=1, more_results_available=False)

# Route for displaying movie details and summary
@app.route('/movie/<string:movie_id>')
def movie_details(movie_id):
    # Fetch subtitles for the selected movie
    subtitles = search_subtitles_subs4free(movie_id)
    # Fetch movie details from IMDb
    movie = ia.get_movie(movie_id)
    # Extract plot summary
    plot_summary = movie['plot'][0] if 'plot' in movie and movie['plot'] else 'Plot summary not available'
    # Redirect to the summary page with the plot summary
    return redirect(url_for('summary', plot_summary=plot_summary))

# Route for displaying the summary page
@app.route('/summary')
def summary():
    plot_summary = request.args.get('plot_summary')
    return render_template('summary.html', plot_summary=plot_summary)

if __name__ == '__main__':
    app.run(debug=True)
