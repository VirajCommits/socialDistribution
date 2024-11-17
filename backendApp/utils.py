# import requests
# from requests.auth import HTTPBasicAuth
# from cryptography.fernet import InvalidToken


# def connect_to_remote_node(node):
#     """Test the connection to a remote node."""
#     try:
#         password = node.get_password()  # Validate decryption
#         response = requests.get(
#             f"{node.url}/service/api/",
#             auth=HTTPBasicAuth(node.username, password),
#             timeout=10,
#         )
#         if response.status_code == 200:
#             node.connected = True
#         else:
#             node.connected = False
#         node.save()
#         return node.connected
#     except InvalidToken:
#         raise ValueError("Invalid encrypted password or incorrect Fernet key.")
#     except requests.RequestException:
#         node.connected = False
#         node.save()
#         return False
