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
        

        # Get the node we're connecting to
        node = ToWhichItsConnected.objects.get(url=base_url, active=True)

        print("&&&&&&&&&&" , node.username , node.password)
        
        # Create auth header with node's credentials
        credentials = base64.b64encode(
            f"{node.username}:{node.password}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        
        # Combine base URL and endpoint
        full_url = urljoin(base_url, endpoint)
        print("This is the full url:" , full_url , headers)
        
        if method.upper() == 'GET':
            response = requests.get(full_url, headers=headers)
            print("this response:" , response.json())
        elif method.upper() == 'POST':
            print("HEADERS THAT WERE SENT:" , headers)
            response = requests.post(full_url, json=data, headers=headers)
            print("This post response:" , response.json())
        else:
            response = None

        return response
        
    except ToWhichItsConnected.DoesNotExist:
        error_message = f"No connection configuration found for {base_url}"
        raise Exception(error_message)