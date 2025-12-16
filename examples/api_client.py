"""
Example API client for ShopeeFlashBot SaaS
Demonstrates how to interact with the API
"""
import requests
from typing import Dict, Optional

class ShopeeFlashBotClient:
    """Client for interacting with ShopeeFlashBot SaaS API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        self.token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, email: str, username: str, password: str) -> Dict:
        """Register a new user"""
        url = f"{self.base_url}{self.api_prefix}/auth/register"
        data = {
            "email": email,
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> Dict:
        """Login and store access token"""
        url = f"{self.base_url}{self.api_prefix}/auth/login"
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        self.token = result["access_token"]
        return result
    
    def get_me(self) -> Dict:
        """Get current user information"""
        url = f"{self.base_url}{self.api_prefix}/auth/me"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def create_task(self, name: str, url: str, target_time: str, 
                   config: Optional[Dict] = None) -> Dict:
        """Create a new bot task"""
        api_url = f"{self.base_url}{self.api_prefix}/tasks"
        data = {
            "name": name,
            "url": url,
            "target_time": target_time,
            "config": config or {}
        }
        response = requests.post(api_url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self) -> list:
        """List all tasks for current user"""
        url = f"{self.base_url}{self.api_prefix}/tasks"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: int) -> Dict:
        """Get a specific task"""
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def run_task(self, task_id: int) -> Dict:
        """Run a bot task"""
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}/run"
        response = requests.post(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def cancel_task(self, task_id: int) -> Dict:
        """Cancel a running task"""
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}/cancel"
        response = requests.post(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def delete_task(self, task_id: int) -> Dict:
        """Delete a task"""
        url = f"{self.base_url}{self.api_prefix}/tasks/{task_id}"
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the API client"""
    
    # Initialize client
    client = ShopeeFlashBotClient(base_url="http://localhost:8000")
    
    # Register a new user
    print("Registering user...")
    try:
        user = client.register(
            email="john@example.com",
            username="johndoe",
            password="securepassword123"
        )
        print(f"User registered: {user['email']}")
    except requests.exceptions.HTTPError as e:
        print(f"Registration failed: {e}")
        # User might already exist, continue to login
    
    # Login
    print("\nLogging in...")
    login_result = client.login(
        email="john@example.com",
        password="securepassword123"
    )
    print(f"Login successful! Token: {login_result['access_token'][:20]}...")
    
    # Get current user info
    print("\nGetting user info...")
    me = client.get_me()
    print(f"Current user: {me['username']} ({me['email']})")
    print(f"Subscription tier: {me['subscription_tier']}")
    
    # Create a bot task
    print("\nCreating bot task...")
    task = client.create_task(
        name="Flash Sale - Red Shirt",
        url="https://shopee.co.id/product/123456",
        target_time="00:00:00",
        config={
            "product_option": "Red",
            "payment_method": "ShopeePay",
            "use_voucher": True,
            "auto_confirm": False  # Don't auto-confirm in example
        }
    )
    print(f"Task created: {task['name']} (ID: {task['id']})")
    
    # List all tasks
    print("\nListing all tasks...")
    tasks = client.list_tasks()
    print(f"Total tasks: {len(tasks)}")
    for t in tasks:
        print(f"  - {t['name']} (Status: {t['status']})")
    
    # Get specific task details
    print(f"\nGetting task details for task {task['id']}...")
    task_detail = client.get_task(task['id'])
    print(f"Task: {task_detail['name']}")
    print(f"URL: {task_detail['url']}")
    print(f"Target time: {task_detail['target_time']}")
    print(f"Status: {task_detail['status']}")
    
    # Note: Don't actually run the task in this example
    # To run: client.run_task(task['id'])
    print("\nNote: Task created but not executed (remove auto_confirm=False to enable)")
    
    # Clean up - delete the task
    print(f"\nDeleting task {task['id']}...")
    delete_result = client.delete_task(task['id'])
    print(f"Task deleted: {delete_result['message']}")


if __name__ == "__main__":
    example_usage()
