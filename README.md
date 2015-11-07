# PingMePy
This is a wrapper around the MongoDB OpsManager / Cloud Manager API. It simplifies accessing the API allowing easy access to all endpoints. There are differences between the [OpsManager API](https://docs.opsmanager.mongodb.com/current/reference/api) and the [Cloud Manager API](https://docs.cloud.mongodb.com/reference/api). These should be kept in mind when using this wrapper. Some methods are simply not available in Cloud Manager. Each method call should have appropriate documentation links included in the comments.

# Usage
Import the `PingMePy` library and create a new `PingMeClient`.
```python
from PingMePy import PingMeClient

client = PingMeClient("joe@example.com", "2ddec171-6ea2-4ff9-be3f-556865290f3d", "opsManager.example.com")
```
The rest of the method calls are named similar (or identical to) the names in the [documentation](https://docs.opsmanager.mongodb.com/current/reference/api).

## Get Groups Available to the User
```python
client.get_groups()
```