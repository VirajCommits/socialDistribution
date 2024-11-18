import base64
import requests
from .models import ToWhichItsConnected

def make_node_request(target_url, method='GET', data=None):
    """
    Make authenticated request to another node using ToWhichItsConnected credentials
    """
    try:
        # Get the node we're connecting to
        node = ToWhichItsConnected.objects.get(url=target_url, active=True)
        
        # Create auth header with node's credentials
        credentials = base64.b64encode(
            f"{node.username}:{node.password}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        
        if method.upper() == 'GET':
            response = requests.get(target_url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(target_url, json=data, headers=headers)
        # Add other methods as needed
        
        return response
        
    except ToWhichItsConnected.DoesNotExist:
        raise Exception(f"No connection configuration found for {target_url}")