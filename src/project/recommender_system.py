import numpy as np
import pandas as pd
import re
import ast
from matplotlib import pyplot as plt

def col(df, colname = "artists"):
    return np.array([int(x == colname) for x in df.columns]).argmax()

def query_artists(df, lists = [], full = False, strict = True):
    return pd.concat([query_artist(df, string = name, strict = strict) for name in lists], axis = 0)

def query_artist(df, string = "--", full = False, strict = True):
    lists = []
    for i, artist in enumerate(df["artists"]):
        if(len(re.findall(string, "".join(artist))) != 0):
            if(strict):
                if(string == artist):
                    if(full):
                        lists.append(df.iloc[i])
                    else:
                        lists.append(df.iloc[i, [col(df, "artists"), col(df, "genres")]])
            else:
                if(full):
                    lists.append(df.iloc[i])
                else:
                    lists.append(df.iloc[i, [col(df, "artists"), col(df, "genres")]])
    if(full):
        return pd.DataFrame(lists, columns = df.columns)
    else:
        return pd.DataFrame(lists, columns = ["artists", "genres"])

def perfect_eval(string):
    try:
        return ast.literal_eval(string)
    except:
        return []

def create_random_dict(df_by_artists, length, score):
    list_of_names = list(set(df_by_artists["artists"]))
    random_indices = [round(x) for x in np.random.random(length)*len(list_of_names)]
    random_names = pd.Series(list_of_names).iloc[random_indices].values.tolist()
    random_rates = [int(round(x)) for x in (score[0] + np.random.random(length)*(score[1]-score[0]))]
    name_rate_dict = {}
    for index in range(length):
        name_rate_dict.update({random_names[index]: random_rates[index]})
    return name_rate_dict

def rate_artist(df_by_artists, name_rate_dict):
    #convert the name_rate_series to a pandas dataframe
    name_rate_series = pd.DataFrame({"rate": name_rate_dict.values, "artists": name_rate_dict.index})
    #create a new dataframe, only selecting the artists and genres columns of artists selected by user
    artists_genres = df_by_artists[df_by_artists["artists"].isin(list(name_rate_dict.keys()))][["artists", "genres"]]
    #merge both of these
    df_name_rate = pd.merge(name_rate_series, artists_genres, on = "artists", how = "inner")
    df_x = df_name_rate.copy()
    #create the artist-genre-matrix for artists selected by users
    for index, genres in enumerate(df_name_rate["genres"]):
        for genre in genres:
            #artist includes the genre: 1
            df_x.at[index, genre] = 1
    #artist does not include the genre: 0
    df_x = df_x.fillna(0)
    #ratings of artists
    df_user = df_x["rate"]
    #drop all columns except the genre columns
    df_genre_matrix = df_x.drop(["artists", "genres", "rate"], axis = 1).reset_index(drop = True)
    #find out the genres' ratings
    df_profile = df_genre_matrix.transpose().dot(df_user)
    return df_profile

def select_artist(df_by_artists, df_rate):
    # save the indices of artists, which include any of the genres in the genre profile
    list_of_id = []
    for index, row in df_by_artists.iterrows():
        for genre in row["genres"]:
            if(genre in df_rate.index):
                list_of_id.append(index)
    #find the unique indices
    list_of_id = list(set(list_of_id))
    #select the artists and genres columns of the artists including any of the genres in the genre profile
    df_select_columns = df_by_artists.iloc[list_of_id, [col(df_by_artists, "artists"), col(df_by_artists, "genres")]]
    df_select = df_select_columns.copy()
    #create the artist-genre-matrix of new artists
    for index, row in df_select_columns.iterrows():
        for genre in row['genres']:
            #artist includes genre: 1
            df_select.at[index, genre] = 1
    #artist does not include genre: 0
    df_select = df_select.fillna(0)[df_rate.index]
    return df_select

def recommend_artist_by_genre(df_by_artists, name_rate_dict, how_many):
    df_by_artists = df_by_artists.copy()
    #make sure that genres are list, not string
    df_by_artists["genres"] = [perfect_eval(genre) for genre in df_by_artists["genres"]]
    #create a name_rate pandas series
    name_rate_series = pd.Series(name_rate_dict)
    #find out the genre profile of user
    df_rate = rate_artist(df_by_artists, name_rate_series)
    #create new artists' matrix
    df_select = select_artist(df_by_artists, df_rate)
    #calculate similarity scores of those artists
    affinity_scores = df_select.dot(df_rate)/df_rate.sum()
    #sort it in descending order
    affinity_scores_sorted = pd.Series(affinity_scores, name = "genre_affinity").sort_values(ascending = False)
    #retrieve the names of artists by their indices
    artists_in_df = df_by_artists.iloc[affinity_scores_sorted.index, [col(df_by_artists, "artists")]]
    #store the artists' names and their similarity scores in a dataframe
    resulted_df = pd.concat([affinity_scores_sorted, artists_in_df], axis = 1)
    #drop the artists already selected by user and limit the count of artists to a specified amount
    output = resulted_df[~resulted_df["artists"].isin(name_rate_series.index)].iloc[:how_many, :]
    #create new indices
    return output.reset_index()

def pretty_recommend_artist(df_by_artists, name_rate_dict, how_many):
    df_scores = recommend_artist_by_genre(df_by_artists, name_rate_dict, how_many)
    print("\n\n--- GENRE AFFINITY ---\n\n")
    for index, row in df_scores.iterrows():
        print("Number ",str(index),": ",row["artists"]," matching ",str(round(row["genre_affinity"] * 100, 2)),"%")
    print("\n\n")
    plt.figure(figsize = (10, 10))
    plt.bar(list(df_scores["artists"]), list(df_scores["genre_affinity"]), color = ["green" for x in range(how_many)])
    plt.xticks(rotation = 90)
    plt.xlabel("Artists")
    plt.ylabel("Score")
    plt.title("Top "+str(how_many)+" Favourite Artists")

def songs_dict(name_rate_dict, how_many):
    df_by_artists = pd.read_csv("data_w_genres.csv")
    df_scores = recommend_artist_by_genre(df_by_artists, name_rate_dict, how_many)
    return df_scores.to_dict()

df_by_artists = pd.read_csv("data_w_genres.csv")
# name_rate_dict = create_random_dict(df_by_artists, 10, [0, 10])
# name_rate_dict_1 = {"Linkin Park": 10, "Red Hot Chili Peppers": 9, "Three Days Grace": 7, "Arctic Monkeys": 4, "Papa Roach": 6,
#                     "Green Day": 8, "Foo Fighters": 1, "Billy Talent": 2, "Nirvana": 5, "The Offspring": 3}
# name_rate_dict_2 = {"Rihanna": 10, "Beyonce": 9, "Britney Spears": 7, "Adele": 4, "Camila Cabello": 6, "Ciara": 8,
#                  "Nicki Minaj": 8, "Iggy Azalea": 8, "Ariana Grande": 5, "Clean Bandit": 3}
name_rate_dict_3 = {"MGMT": 10, "Temples": 10, "Glass Animals": 7, "The Beatles": 8, "The Clash": 7, "Alphaville": 5,
                    "One Direction": 6, "David Bowie": 7}
how_many = 10

# query_artists(df_by_artists, list(name_rate_dict_3.keys()))
# print(type(recommend_artist_by_genre(df_by_artists, name_rate_dict_3, how_many)))
