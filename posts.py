import facebook as fb

fb_profile_id = "adithyabhatk"


def preprocess_data(data):
    return data


def get_posts(access_token):
    facebook_graph = fb.GraphAPI(access_token)
    feeds = facebook_graph.get_connections("me", "feed")
    data = feeds['data']
    return preprocess_data(data)
