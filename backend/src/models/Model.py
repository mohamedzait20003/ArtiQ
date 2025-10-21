import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")


class Model:
    table_name: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def table(cls):
        return dynamodb.Table(cls.table_name)

    def save(self):
        item = self.__dict__
        try:
            self.table().put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving item: {e}")
            return False

    @classmethod
    def get(cls, key: dict):
        try:
            response = cls.table().get_item(Key=key)
            item = response.get("Item")
            if item:
                return cls(**item)
            return None
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None

    def delete(self):
        key = {k: getattr(self, k) for k in self.primary_key()}
        try:
            self.table().delete_item(Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting item: {e}")
            return False

    @classmethod
    def primary_key(cls):
        raise NotImplementedError
