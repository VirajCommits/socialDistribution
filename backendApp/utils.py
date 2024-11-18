import base64
import requests
from urllib.parse import urljoin
from .models import ToWhichItsConnected

def make_node_request(base_url, endpoint, method='GET', data=None):
    """
    Make authenticated request to another node using ToWhichItsConnected credentials
    @param base_url: The base URL of the target node (e.g., 'https://other-team.herokuapp.com/')
    @param endpoint: The API endpoint (e.g., 'service/api/authors/')
    """
    try:
        print(f"Attempting to connect to node with base URL: {base_url}")
        
        # Print all objects in ToWhichItsConnected
        all_nodes = ToWhichItsConnected.objects.all()
        for node in all_nodes:
            print(f"Node URL: {node.url}, Username: {node.username}, Active: {node.active}")

        # Get the node we're connecting to
        node = ToWhichItsConnected.objects.get(url=base_url, active=True)
        print(f"Node found: {node.url}, Username: {node.username}")
        
        # Create auth header with node's credentials
        credentials = base64.b64encode(
            f"{node.username}:{node.password}".encode()
        ).decode()
        print(f"Encoded credentials: {credentials}")
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        print(f"Request headers: {headers}")
        
        # Combine base URL and endpoint
        full_url = urljoin(base_url, endpoint)
        print(f"Full URL: {full_url}")
        
        if method.upper() == 'GET':
            print(f"Making GET request to {full_url}")
            response = requests.get(full_url, headers=headers)
        elif method.upper() == 'POST':
            print(f"Making POST request to {full_url} with data: {data}")
            response = requests.post(full_url, json=data, headers=headers)
        else:
            print(f"HTTP method {method} not implemented")
            response = None
            
        print(f"Response received: {response.status_code} - {response.text}")
        return response
        
    except ToWhichItsConnected.DoesNotExist:
        error_message = f"No connection configuration found for {base_url}"
        print(error_message)
        raise Exception(error_message)