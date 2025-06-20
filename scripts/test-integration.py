#!/usr/bin/env python3
"""
Script de test d'intégration pour PeproScolaire
Tests de tous les endpoints API avec authentification JWT
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional
from datetime import datetime

class PeproScolaireAPITester:
    """Classe pour tester l'API PeproScolaire"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Logger avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": "\033[0;32m",   # Vert
            "ERROR": "\033[0;31m",  # Rouge
            "WARN": "\033[1;33m",   # Jaune
            "TEST": "\033[0;34m"    # Bleu
        }.get(level, "\033[0m")
        
        print(f"{color}[{timestamp}] {level}: {message}\033[0m")
    
    def test_api_call(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, expected_status: int = 200,
                     test_name: str = "") -> Dict[str, Any]:
        """Effectue un appel API et enregistre le résultat"""
        
        url = f"{self.base_url}{endpoint}"
        test_headers = {"Content-Type": "application/json"}
        
        if headers:
            test_headers.update(headers)
            
        if self.access_token:
            test_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=test_headers, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=test_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=test_headers)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=test_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            success = response.status_code == expected_status
            
            result = {
                "test_name": test_name or f"{method} {endpoint}",
                "url": url,
                "method": method.upper(),
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_time": response.elapsed.total_seconds(),
                "response_data": None
            }
            
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text
            
            self.test_results.append(result)
            
            if success:
                self.log(f"✅ {test_name}: {response.status_code}", "TEST")
            else:
                self.log(f"❌ {test_name}: {response.status_code} (attendu: {expected_status})", "ERROR")
                self.log(f"   Réponse: {result['response_data']}", "ERROR")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Erreur de connexion pour {test_name}: {e}", "ERROR")
            result = {
                "test_name": test_name,
                "url": url,
                "method": method.upper(),
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            return result
    
    def authenticate(self) -> bool:
        """Authentification avec JWT"""
        self.log("🔐 Test d'authentification JWT...")
        
        # Test avec admin
        auth_data = {
            "email": "admin@peproscolaire.fr",
            "password": "admin123"
        }
        
        result = self.test_api_call(
            "POST", 
            "/auth/login/",
            data=auth_data,
            test_name="Authentification Admin"
        )
        
        if result["success"] and "access" in result["response_data"]:
            self.access_token = result["response_data"]["access"]
            self.log("✅ Authentification réussie", "INFO")
            return True
        else:
            self.log("❌ Échec de l'authentification", "ERROR")
            return False
    
    def test_auth_endpoints(self):
        """Test des endpoints d'authentification"""
        self.log("🔐 Tests des endpoints d'authentification...")
        
        # Test de santé
        self.test_api_call("GET", "/auth/health/", test_name="Health Check")
        
        # Test de refresh token (si disponible)
        if hasattr(self, 'refresh_token'):
            self.test_api_call(
                "POST",
                "/auth/token/refresh/",
                data={"refresh": self.refresh_token},
                test_name="Refresh Token"
            )
    
    def test_schools_endpoints(self):
        """Test des endpoints du module schools"""
        self.log("🏫 Tests des endpoints Schools...")
        
        # Liste des écoles
        self.test_api_call("GET", "/schools/", test_name="Liste des écoles")
        
        # Années académiques
        self.test_api_call("GET", "/schools/academic-years/", test_name="Années académiques")
        
        # Niveaux
        self.test_api_call("GET", "/schools/levels/", test_name="Niveaux scolaires")
        
        # Classes
        self.test_api_call("GET", "/schools/classes/", test_name="Classes")
    
    def test_timetable_endpoints(self):
        """Test des endpoints du module timetable"""
        self.log("📅 Tests des endpoints Timetable...")
        
        # Créneaux horaires
        self.test_api_call("GET", "/timetable/time-slots/", test_name="Créneaux horaires")
        
        # Matières
        self.test_api_call("GET", "/timetable/subjects/", test_name="Matières")
        
        # Salles
        self.test_api_call("GET", "/timetable/rooms/", test_name="Salles")
        
        # Emplois du temps
        self.test_api_call("GET", "/timetable/schedules/", test_name="Emplois du temps")
    
    def test_attendance_endpoints(self):
        """Test des endpoints du module attendance"""
        self.log("👥 Tests des endpoints Attendance...")
        
        # Présences
        self.test_api_call("GET", "/attendance/", test_name="Présences")
        
        # Statistiques
        self.test_api_call("GET", "/attendance/stats/", test_name="Statistiques présences")
    
    def test_grades_endpoints(self):
        """Test des endpoints du module grades"""
        self.log("📝 Tests des endpoints Grades...")
        
        # Évaluations
        self.test_api_call("GET", "/grades/evaluations/", test_name="Évaluations")
        
        # Notes
        self.test_api_call("GET", "/grades/grades/", test_name="Notes")
        
        # Bulletins
        self.test_api_call("GET", "/grades/bulletins/", test_name="Bulletins")
    
    def test_homework_endpoints(self):
        """Test des endpoints du module homework"""
        self.log("📚 Tests des endpoints Homework...")
        
        # Devoirs
        self.test_api_call("GET", "/homework/", test_name="Devoirs")
        
        # Types de devoirs
        self.test_api_call("GET", "/homework/types/", test_name="Types de devoirs")
    
    def test_messaging_endpoints(self):
        """Test des endpoints du module messaging"""
        self.log("💬 Tests des endpoints Messaging...")
        
        # Conversations
        self.test_api_call("GET", "/messaging/conversations/", test_name="Conversations")
        
        # Messages
        self.test_api_call("GET", "/messaging/messages/", test_name="Messages")
    
    def test_student_records_endpoints(self):
        """Test des endpoints du module student records"""
        self.log("📋 Tests des endpoints Student Records...")
        
        # Dossiers élèves
        self.test_api_call("GET", "/student-records/", test_name="Dossiers élèves")
        
        # Documents
        self.test_api_call("GET", "/student-records/documents/", test_name="Documents")
    
    def test_ai_analytics_endpoints(self):
        """Test des endpoints du module AI analytics"""
        self.log("🤖 Tests des endpoints AI Analytics...")
        
        # Profils de risque
        self.test_api_call("GET", "/ai-analytics/risk-profiles/", test_name="Profils de risque")
        
        # Alertes
        self.test_api_call("GET", "/ai-analytics/alerts/", test_name="Alertes")
        
        # Analyses
        self.test_api_call("GET", "/ai-analytics/analyses/", test_name="Analyses")
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests"""
        self.log("🚀 Démarrage des tests d'intégration API", "INFO")
        
        # Vérifier que l'API est accessible
        try:
            response = requests.get(f"{self.base_url}/auth/health/", timeout=10)
            if response.status_code != 200:
                self.log("❌ L'API n'est pas accessible", "ERROR")
                return False
        except:
            self.log("❌ Impossible de se connecter à l'API", "ERROR")
            return False
        
        # Authentification
        if not self.authenticate():
            return False
        
        # Tests des modules
        test_modules = [
            self.test_auth_endpoints,
            self.test_schools_endpoints,
            self.test_timetable_endpoints,
            self.test_attendance_endpoints,
            self.test_grades_endpoints,
            self.test_homework_endpoints,
            self.test_messaging_endpoints,
            self.test_student_records_endpoints,
            self.test_ai_analytics_endpoints
        ]
        
        for test_module in test_modules:
            try:
                test_module()
            except Exception as e:
                self.log(f"❌ Erreur dans {test_module.__name__}: {e}", "ERROR")
        
        return self.generate_report()
    
    def generate_report(self) -> bool:
        """Génère un rapport de test"""
        self.log("📊 Génération du rapport de test...", "INFO")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("📊 RAPPORT DE TESTS D'INTÉGRATION API")
        print("="*60)
        print(f"📈 Total des tests : {total_tests}")
        print(f"✅ Tests réussis : {successful_tests}")
        print(f"❌ Tests échoués : {failed_tests}")
        print(f"📊 Taux de réussite : {success_rate:.1f}%")
        print("="*60)
        
        if failed_tests > 0:
            print("\n❌ TESTS ÉCHOUÉS :")
            for result in self.test_results:
                if not result.get("success", False):
                    print(f"  - {result['test_name']}: {result.get('status_code', 'ERROR')}")
        
        print("\n⏱️  TEMPS DE RÉPONSE MOYEN :")
        response_times = [r.get("response_time", 0) for r in self.test_results if "response_time" in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"  Moyenne : {avg_time:.3f}s")
            print(f"  Max : {max(response_times):.3f}s")
            print(f"  Min : {min(response_times):.3f}s")
        
        # Sauvegarder le rapport JSON
        report_file = f"/home/walid/peproscolaire/logs/integration-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        self.log(f"📄 Rapport sauvegardé : {report_file}", "INFO")
        
        return failed_tests == 0

def main():
    """Fonction principale"""
    print("🧪 PeproScolaire - Tests d'Intégration API")
    print("=" * 50)
    
    # Attendre que les services soient prêts
    print("⏳ Attente du démarrage des services...")
    time.sleep(5)
    
    tester = PeproScolaireAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tous les tests d'intégration ont réussi !")
        sys.exit(0)
    else:
        print("\n💥 Certains tests ont échoué. Vérifiez les logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()