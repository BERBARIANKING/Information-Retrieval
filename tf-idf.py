from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pyspark.ml.feature import RegexTokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.sql.functions import explode
import math
from math import sqrt

app = Flask(__name__, template_folder='templates', static_folder='static')

# Spark initialization
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TF-IDF Search Engine") \
    .getOrCreate()

# Step 1: Tokenize the plot summary words
moviePlots = spark.read.option("header", "false").option("delimiter","\t").csv("/FileStore/tables/plot_summaries.txt").toDF("id","summary")
tokenizer = RegexTokenizer().setInputCol("summary").setOutputCol("words").setPattern("\\W+")
wordsData = tokenizer.transform(moviePlots)

# Step 2: Remove stop words
remover = StopWordsRemover().setInputCol("words").setOutputCol("Word Collection")
plotWords = remover.transform(wordsData).select("id","Word Collection").toDF("movie_id","plot_summary")

# Step 3: Converting to RDD after exploding the rows
plotWords_Split = plotWords.select(plotWords.movie_id,explode(plotWords.plot_summary)).rdd

# Step 4: Performing map-reduce to get the word count per movie per word
movWord_Init = plotWords_Split.map(lambda x:((x[0],x[1]),1))
movWord_Count = movWord_Init.reduceByKey(lambda x,y:x+y)

# Step 5: Performing map-reduce to find the movie frequency for the particular word
total_Docs = plotWords_Split.count()
docs_Count = movWord_Count.map(lambda x:(x[0][1],1))
tf = docs_Count.reduceByKey(lambda x,y: x + y)

# Step 6: Computing TF-IDF
idf = tf.map(lambda x:(x[0],math.log((total_Docs/x[1]))))
word_Movie = movWord_Count.map(lambda x:(x[0][1],(x[0][0],x[1])))
tfidf = word_Movie.join(idf)
final_tfidf = tfidf.map(lambda x: (x[0],((x[1][0][0],x[1][0][1]),x[1][1],x[1][1]*x[1][0][1])))

# Step 7: Reading movie metadata for getting the movie name from movieId
movie_metadata = spark.read.csv('/FileStore/tables/movie_metadata.tsv', header=None, sep = '\t')
movie_details = movie_metadata.select("_c0","_c2").toDF("movie_id","movie_name").rdd

def search_tfidf(query):
    query = query.lower().split()
    freq_terms = spark.sparkContext.parallelize(query).map(lambda x : (x, 1)).reduceByKey(lambda x,y : x+y)
    final_tfidf_mod = final_tfidf.map(lambda x :(x[0], x[1][2]))
    terms_present = freq_terms.join(final_tfidf_mod)
    merge_terms = terms_present.map(lambda x : (x[0], x[1][1]))
    tf_movies = final_tfidf.map(lambda x : (x[0], (x[1][0][0], x[1][2]))).join(merge_terms).map(lambda x : (x[1][0], x[1][1], x[1][0][1]))
    cos_val_init = tf_movies.map(lambda x : (x[0], (x[1] * x[2], x[2] * x[2], x[1] * x[1])))
    cos_val = cos_val_init.reduceByKey(lambda x,y : ((x[0] + y[0], x[1] + y[1], x[2] + y[2])))
    cos_score = cos_val.map(lambda x : (x[0], x[1][0]/(sqrt(x[1][1]) * sqrt(x[1][2]))))
    RDD_res =  cos_score.map(lambda x : (x[0][0], 1)).reduceByKey(lambda x,y : x+y)
    movie_list = RDD_res.join(movie_details).map(lambda x : (x[0], x[1][1]))
    movie_cos_score = cos_score.map(lambda x : (x[0][0], x[1]))
    movie_cos_score = movie_cos_score.join(movie_list).distinct().sortBy(lambda x : -x[1][0])
    sorted_movie_cos_score = movie_cos_score.map(lambda x : [x[0],x[1][1],x[1][0]]).toDF(["Movie Id", "Movie Name", "Cosine Similarity"])
    return sorted_movie_cos_score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_tfidf(query)
        return render_template('results.html', results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
