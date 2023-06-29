from pythorhead import Lemmy
from pythorhead import community
from pythorhead import post
from pythorhead import comment
from pythorhead.types import SortType
from hugchat import hugchat
from hugchat.login import Login
import time

def get_posts(c_id):
    posts = lemmy.post.list(community_id=c_id,community_name=None,limit=1,page=None,saved_only=None, sort=SortType.New,type_=None)
    return posts

def post_data(post):
    try:
        return post["post"]["id"],post["post"]["url"]
    except KeyError:
        return post["post"]["id"],""

def get_comments(c_id,p_id):
    return lemmy.comment.list(community_id=c_id,community_name=None,limit=None,max_depth=None,page=None,parent_id=None,post_id=p_id,saved_only=None,sort=None,type_=None)

def check_comments(comments_data):
    for element in comments_data:
        comment = element["comment"]["content"]
        if "tldr" in comment:
            return False
    return True

def make_comment(p_id,comment_body):
    return lemmy.comment.create(p_id,comment_body)

def prepare_tldr(prompt,post_id):
    try:
        ai_response = chatbot.chat(prompt)
        tldr_comment = "tldr  \n" + ai_response
        write_comment = make_comment(post_id,tldr_comment)
        # Create a new conversation
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        print(tldr_comment)
    except ModelOverloadedError:
        print("Model is Overloaded")
        pass

if __name__ == "__main__":
    #hugchat hugging face account
    email = "<your-mail>"
    passwd = "<your-password>"
    # Log in to huggingface and grant authorization to huggingchat
    sign = Login(email, passwd)
    cookies = sign.login()
    # Save cookies to usercookies/<email>.json
    sign.saveCookies()
    # Create a ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

    #lemmy
    lemmy = Lemmy("<lemmy-instance>") # like "https://enterprise.lemmy.ml"

    try:
        lemmy.log_in("<your-lemmy-account>", "<your-password>")
        community_id = int(lemmy.discover_community("<your_community_name>")) # like "crypto"
        community = lemmy.community.get(community_id)
        print(community_id)

        while True:
            last_post = get_posts(community_id)[0]
            post_id, post_url = post_data(last_post)
            comments = get_comments(community_id,post_id)
            if check_comments(comments) == True and len(post_url)!=0:
                print(post_id,"\n",post_url)
                ai_request = 'tldr' + post_url + 'in less than 250 characters prepare up to 5 bullet points. Do not include narration.'
                prepare_tldr(ai_request,post_id)
                print("success")
            time.sleep(60)

    except Exception as e:
        print(f"An error occurred: {e}")
