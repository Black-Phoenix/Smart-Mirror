import facebook as fb

fb_profile_id = "adithyabhatk"


class Post():
    def __init__(self):
        self.title = "No Title"
        self.id = ""
        self.msg = "No Body"


def preprocess_data(data):
    posts = []
    for item in data:
        temp = Post()
        if 'message' in item.keys():
            temp.msg = item['message']
        if 'story' in item.keys():
            temp.title = item['story']
        temp.id = item['id']
        posts.append(temp)
    return posts

updating = False
post_data = []
id = 0
curr_fb_item = 0
curr_alpha = 255 * 2.0
expanded_post = False

def get_posts():
    global updating, post_data, id
    updating = True
    f = open("Conf/facebook/" + str(id)+ ".conf")
    access_token = f.readline()
    facebook_graph = fb.GraphAPI(access_token)
    feeds = facebook_graph.get_connections("me", "feed")
    data = feeds['data']
    updating = False
    post_data = preprocess_data(data)
