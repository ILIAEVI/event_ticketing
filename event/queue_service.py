import redis


class QueueService:
    def __init__(self, event):
        """
        Initialize the QueueService with an event instance.
        :param event: The event object for which the queue is managed.
        """
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.event = event
        self.queue_key = f"event{self.event.id}:queue"
        self.unique_set_key = f"event{self.event.id}:users"
        self.allowed_users_set = f"event{self.event.id}:allowed_users"

    def add_to_queue(self, user_id: str) -> bool:
        """
        Add a user to the queue if not already present.
        :param user_id: The unique ID of the user.
        :return: True if the user was added to the queue, False otherwise.
        """
        if self.redis.sadd(self.unique_set_key, user_id):
            self.redis.rpush(self.queue_key, user_id)
            return True
        return False

    def get_user_position(self, user_id: str):
        """
        Encode User's id, check if it is in the queue and returns position.
        :param user_id: Unique ID of the user.
        :return: position of user in queue
        """
        queue = self.redis.lrange(self.queue_key, 0, -1)
        encoded_user_id = user_id.encode()
        if encoded_user_id in queue:
            position = queue.index(encoded_user_id) + 1
            return position
        return "Not in queue"

    def process_queue(self, count=10):
        self.clear_allowed_users()
        users = self.redis.lpop(self.queue_key, count=count)
        if users:
            self.redis.srem(self.unique_set_key, *users)
            user_ids = [user.decode() for user in users]

            self.redis.sadd(self.allowed_users_set, *user_ids)
            return user_ids
        return None

    def get_allowed_users(self):
        allowed_users = self.redis.smembers(self.allowed_users_set)
        decoded_users = [user_id.decode() for user_id in allowed_users]
        return decoded_users

    def clear_allowed_users(self):
        self.redis.delete(self.allowed_users_set)

    def get_queue_length(self):
        """
        Get the length of the queue.
        :return:  The number of users in the queue.
        """
        return self.redis.llen(self.queue_key)

    def clear_queue(self):
        """
        Clear the entire queue and unique set for the event.
        """
        self.redis.delete(self.queue_key)
        self.redis.delete(self.unique_set_key)
