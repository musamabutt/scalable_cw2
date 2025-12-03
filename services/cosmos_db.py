# services/cosmos_db.py
from azure.cosmos import CosmosClient, PartitionKey
from config import COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_USERS_CONTAINER, COSMOS_VIDEOS_CONTAINER, COSMOS_COMMENTS_CONTAINER
import uuid

class CosmosDB:
    def __init__(self):
        self.client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        self.database = self.client.create_database_if_not_exists(COSMOS_DATABASE)
        self.users = self.database.create_container_if_not_exists(
            id=COSMOS_USERS_CONTAINER, partition_key=PartitionKey(path="/id")
        )
        self.videos = self.database.create_container_if_not_exists(
            id=COSMOS_VIDEOS_CONTAINER, partition_key=PartitionKey(path="/id")
        )
        self.comments = self.database.create_container_if_not_exists(
            id=COSMOS_COMMENTS_CONTAINER, partition_key=PartitionKey(path="/id")
        )

    # ---------- Users ----------
    def create_user(self, username: str, password: str):
        existing = list(self.users.query_items(
            query="SELECT * FROM c WHERE c.username=@username",
            parameters=[{"name":"@username","value":username}],
            enable_cross_partition_query=True
        ))
        if existing:
            return None
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "username": username,
            "password": password,
            "createdAt": __import__("datetime").datetime.utcnow().isoformat()
        }
        self.users.create_item(body=user)
        return user

    def get_user(self, username: str, password: str):
        result = list(self.users.query_items(
            query="SELECT * FROM c WHERE c.username=@username AND c.password=@password",
            parameters=[{"name":"@username","value":username}, {"name":"@password","value":password}],
            enable_cross_partition_query=True
        ))
        return result[0] if result else None

    def get_user_by_id(self, user_id: str):
        try:
            item = self.users.read_item(item=user_id, partition_key=user_id)
            return item
        except Exception:
            # fallback to query if read_item fails
            res = list(self.users.query_items(
                query="SELECT * FROM c WHERE c.id=@id",
                parameters=[{"name":"@id", "value": user_id}],
                enable_cross_partition_query=True
            ))
            return res[0] if res else None

    # ---------- Videos ----------
    def create_video(self, title: str, filename: str, user_id: str, username: str):
        video_id = str(uuid.uuid4())
        video = {
            "id": video_id,
            "title": title,
            "filename": filename,
            "user_id": user_id,
            "username": username, 
            "likes": 0,
            "createdAt": __import__("datetime").datetime.utcnow().isoformat()
        }
        self.videos.create_item(body=video)
        return video

    def get_videos(self):
        items = list(self.videos.read_all_items())
        # sort by createdAt desc if exists
        try:
            items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        except Exception:
            pass
        return items

    def update_video_likes(self, video_id: str):
        # read, increment, replace
        video = self.videos.read_item(item=video_id, partition_key=video_id)
        if 'likes' not in video:
            video['likes'] = 0
        video['likes'] += 1
        self.videos.replace_item(item=video_id, body=video)
        return video

    # ---------- Comments ----------
    def create_comment(self, video_id: str, user_id: str, username: str, content: str):
        comment_id = str(uuid.uuid4())
        comment = {
            "id": comment_id,
            "video_id": video_id,
            "user_id": user_id,
            "username": username,
            "content": content,
            "createdAt": __import__("datetime").datetime.utcnow().isoformat()
        }
        self.comments.create_item(body=comment)
        return comment

    def get_comments_for_video(self, video_id: str):
        return list(self.comments.query_items(
            query="SELECT * FROM c WHERE c.video_id=@video_id ORDER BY c.createdAt ASC",
            parameters=[{"name":"@video_id", "value": video_id}],
            enable_cross_partition_query=True
        ))
