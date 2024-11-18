import base64
import requests
from .models import ToWhichItsConnected

def make_node_request(target_url, method='GET', data=None):
    """
    Make authenticated request to another node using ToWhichItsConnected credentials
    """
    try:
        print(f"Attempting to connect to node with URL: {target_url}")
        
        # Get the node we're connecting to
        node = ToWhichItsConnected.objects.get(url=target_url, active=True)
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
        
        if method.upper() == 'GET':
            print(f"Making GET request to {target_url}")
            response = requests.get(target_url, headers=headers)
        elif method.upper() == 'POST':
            print(f"Making POST request to {target_url} with data: {data}")
            response = requests.post(target_url, json=data, headers=headers)
        else:
            print(f"HTTP method {method} not implemented")
            response = None
        # Add other methods as needed
        
        print(f"Response received: {response.status_code} - {response.text}")
        return response
        
    except ToWhichItsConnected.DoesNotExist:
        error_message = f"No connection configuration found for {target_url}"
        print(error_message)
        raise Exception(error_message)
        
    except ToWhichItsConnected.DoesNotExist:
        raise Exception(f"No connection configuration found for {target_url}")