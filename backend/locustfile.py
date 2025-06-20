from locust import HttpUser, task, between


class AIModuleUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        if response.status_code == 200:
            self.token = response.json().get('access')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})
    
    @task(3)
    def get_model_status(self):
        self.client.get('/api/v1/ai-analytics/ai/model/status/')
    
    @task(2) 
    def get_dashboard_metrics(self):
        self.client.get('/api/v1/ai-analytics/ai/dashboard/metrics/')
    
    @task(1)
    def get_risk_profiles(self):
        self.client.get('/api/v1/ai-analytics/risk-profiles/')