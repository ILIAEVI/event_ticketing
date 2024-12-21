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

    def add_to_queue(self, user_id: str):
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
        queue = self.redis.lrange(self.queue_key, 0, -1)
        try:
            position = queue.index(str(user_id))
            return position + 1
        except ValueError:
            return None

    def process_queue(self):
        user_id = self.redis.lpop(self.queue_key)
        if user_id:
            self.redis.srem(self.unique_set_key, user_id)
            return user_id.decode()
        else:
            return None

    def process_queue_schedule(self):
        queue = self.redis.lrange(self.queue_key, 0, 9)

    def remove_from_queue(self, user_id: str):
        """
        Remove a user from the queue and the uniqueness set.
        :param user_id: The unique ID of the user.
        :return: True if the user was removed, False otherwise.
        """
        self.redis.srem(self.unique_set_key, user_id)
        queue_users = self.redis.lrange(self.queue_key, 0, -1)
        if user_id.encode('utf-8') in queue_users:
            self.redis.lrem(self.queue_key, 0, user_id)
        return True

    def clear_queue(self):
        """
        Clear the entire queue and unique set for the event.
        """
        self.redis.delete(self.queue_key)
        self.redis.delete(self.unique_set_key)

    def get_queue_length(self):
        return self.redis.llen(self.queue_key)
