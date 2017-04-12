import facebook as fb

fb_profile_id = "adithyabhatk"

class Post():
	def __init__(self):
		self.title 	= ""
		self.id 	= ""
		self.msg 	= ""

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

def get_posts(access_token):
  facebook_graph = fb.GraphAPI(oauth_access_token)
  feeds = facebook_graph.get_connections("me","feed")
  data = feeds['data']
  return preprocess_data(data)
