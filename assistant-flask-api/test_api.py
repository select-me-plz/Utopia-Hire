"""
API Test Suite
Tests all endpoints of the Phi-3 LoRA Adapter API
"""

import requests
import json
from typing import Dict, Any
import time

# API Base URL
BASE_URL = "http://localhost:5000"


class APITester:
    """Test helper class for API endpoints."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Test health check endpoint."""
        print("\n" + "="*60)
        print("TEST 1: Health Check")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200 and data.get("model_loaded"):
                print("✅ Health check PASSED")
                return True
            else:
                print("❌ Health check FAILED")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_list_adapters(self) -> bool:
        """Test list adapters endpoint."""
        print("\n" + "="*60)
        print("TEST 2: List Available Adapters")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/adapters")
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200 and data.get("count", 0) > 0:
                print("✅ List adapters PASSED")
                return True
            else:
                print("❌ List adapters FAILED")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_job_match(self) -> bool:
        """Test job matching endpoint."""
        print("\n" + "="*60)
        print("TEST 3: Job Matching")
        print("="*60)
        
        payload = {
            "resume_json": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "skills": ["Python", "Machine Learning", "PyTorch", "Data Science"],
                "experience": "Senior ML Engineer with 5 years experience",
                "education": "MS Computer Science"
            },
            "job_offers_json": [
                {
                    "title": "Senior ML Engineer",
                    "company": "TechCorp",
                    "required_skills": ["Python", "ML", "Deep Learning"],
                    "salary": "$150K-180K"
                },
                {
                    "title": "Data Scientist",
                    "company": "DataInc",
                    "required_skills": ["Python", "Statistics", "SQL"],
                    "salary": "$120K-140K"
                }
            ]
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/run/job_match",
                json=payload,
                timeout=60  # Reduced from 120
            )
            elapsed = time.time() - start_time
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            data = response.json()
            print(f"Adapter: {data.get('adapter')}")
            print(f"Response Preview: {data.get('response', '')[:200]}...")
            
            if response.status_code == 200 and data.get("status") == "success":
                print("✅ Job matching PASSED")
                return True
            else:
                print("❌ Job matching FAILED")
                print(f"Full response: {json.dumps(data, indent=2)}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_resume_eval(self) -> bool:
        """Test resume evaluation endpoint."""
        print("\n" + "="*60)
        print("TEST 4: Resume Evaluation")
        print("="*60)
        
        payload = {
            "resume_json": {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "phone": "+1-555-123-4567",
                "skills": ["Java", "Spring Boot", "SQL", "AWS"],
                "experience": [
                    {
                        "title": "Senior Backend Engineer",
                        "company": "TechCorp",
                        "duration": "3 years",
                        "description": "Led development of microservices architecture"
                    }
                ],
                "education": "BS Computer Science",
                "certifications": ["AWS Solutions Architect", "Java Programmer"]
            }
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/run/resume_eval",
                json=payload,
                timeout=60  # Reduced from 120
            )
            elapsed = time.time() - start_time
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            data = response.json()
            print(f"Adapter: {data.get('adapter')}")
            print(f"Response Preview: {data.get('response', '')[:200]}...")
            
            if response.status_code == 200 and data.get("status") == "success":
                print("✅ Resume evaluation PASSED")
                return True
            else:
                print("❌ Resume evaluation FAILED")
                print(f"Full response: {json.dumps(data, indent=2)}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_latex_resume(self) -> bool:
        """Test LaTeX resume generation endpoint."""
        print("\n" + "="*60)
        print("TEST 5: LaTeX Resume Generation")
        print("="*60)
        
        payload = {
            "resume_json": {
                "name": "Carol White",
                "email": "carol@example.com",
                "skills": ["Python", "JavaScript", "React", "Node.js"],
                "experience": "Full Stack Developer with 4 years experience",
                "projects": [
                    {"name": "E-commerce Platform", "tech": "React, Node.js, MongoDB"},
                    {"name": "AI Assistant", "tech": "Python, FastAPI, Transformers"}
                ]
            }
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/run/latex_resume",
                json=payload,
                timeout=60  # Reduced from 120
            )
            elapsed = time.time() - start_time
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            data = response.json()
            print(f"Adapter: {data.get('adapter')}")
            print(f"Response Preview: {data.get('response', '')[:200]}...")
            
            if response.status_code == 200 and data.get("status") == "success":
                print("✅ LaTeX resume generation PASSED")
                return True
            else:
                print("❌ LaTeX resume generation FAILED")
                print(f"Full response: {json.dumps(data, indent=2)}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_recruiter_dialog(self) -> bool:
        """Test recruiter dialog endpoint."""
        print("\n" + "="*60)
        print("TEST 6: Recruiter Dialog")
        print("="*60)
        
        payload = {
            "message": "What are the key qualifications needed for a Senior ML Engineer role?"
        }
        
        print(f"Request payload:")
        print(json.dumps(payload, indent=2))
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/run/recruiter_dialog",
                json=payload,
                timeout=60  # Reduced from 120
            )
            elapsed = time.time() - start_time
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            data = response.json()
            print(f"Adapter: {data.get('adapter')}")
            print(f"Response Preview: {data.get('response', '')[:200]}...")
            
            if response.status_code == 200 and data.get("status") == "success":
                print("✅ Recruiter dialog PASSED")
                return True
            else:
                print("❌ Recruiter dialog FAILED")
                print(f"Full response: {json.dumps(data, indent=2)}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling."""
        print("\n" + "="*60)
        print("TEST 7: Error Handling")
        print("="*60)
        
        # Test missing required field
        print("\n7a. Testing missing required field...")
        payload = {"resume_json": {}}  # Missing job_offers_json
        
        try:
            response = self.session.post(
                f"{self.base_url}/run/job_match",
                json=payload,
                timeout=10
            )
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 400:
                print("✅ Error handling PASSED (400 for missing field)")
                return True
            else:
                print("❌ Expected 400 status code")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*60)
        print("PHI-3 LORA API TEST SUITE")
        print("="*60)
        
        results = {
            "Health Check": self.test_health(),
            "List Adapters": self.test_list_adapters(),
            "Error Handling": self.test_error_handling(),
            "Job Matching": self.test_job_match(),
            "Resume Evaluation": self.test_resume_eval(),
            "LaTeX Resume": self.test_latex_resume(),
            "Recruiter Dialog": self.test_recruiter_dialog(),
        }
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print("="*60 + "\n")
        
        return results
        return results


    # ---------------- Assistant Tests ----------------
    def _post_assistant(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """Helper to POST to /assistant and return parsed JSON (or error dict)."""
        try:
            start = time.time()
            resp = self.session.post(f"{self.base_url}/assistant", json=payload, timeout=timeout)
            elapsed = time.time() - start
            print(f"Status Code: {resp.status_code}  (elapsed: {elapsed:.2f}s)")
            data = resp.json()
            print(f"Response (preview): {str(data)[:300]}")
            return {"status_code": resp.status_code, "data": data}
        except Exception as e:
            print(f"❌ Assistant request error: {e}")
            return {"status_code": None, "error": str(e)}

    def test_assistant_general(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: General Chat")
        print("="*60)
        payload = {"message": "Hello! Tell me something interesting."}
        r = self._post_assistant(payload, timeout=60)
        ok = r.get("status_code") == 200 and isinstance(r.get("data", {}).get("response"), str)
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok

    def test_assistant_career(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: Career Advice")
        print("="*60)
        payload = {"message": "How can I improve my resume and interview skills for ML roles?"}
        r = self._post_assistant(payload, timeout=60)
        ok = r.get("status_code") == 200 and r.get("data", {}).get("mode") in ("career", "general")
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok

    def test_assistant_resume_eval(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: Resume Eval via /assistant")
        print("="*60)
        payload = {"message": "Please evaluate my resume", "resume_json": {"name": "Test User", "skills": ["Python"]}}
        r = self._post_assistant(payload, timeout=90)
        ok = r.get("status_code") == 200 and r.get("data", {}).get("mode") in ("resume_eval", "job_match")
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok

    def test_assistant_job_match(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: Job Match via /assistant")
        print("="*60)
        payload = {
            "message": "Which job is best for me?",
            "resume_json": {"name": "Test User", "skills": ["Python", "ML"]},
            "job_offers_json": [{"title": "ML Engineer", "company": "A"}, {"title": "Data Scientist", "company": "B"}]
        }
        r = self._post_assistant(payload, timeout=90)
        ok = r.get("status_code") == 200 and r.get("data", {}).get("mode") == "job_match"
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok

    def test_assistant_recruiter(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: Recruiter Simulation via /assistant")
        print("="*60)
        payload = {"message": "Simulate interviewer: ask me a technical question about ML."}
        r = self._post_assistant(payload, timeout=60)
        ok = r.get("status_code") == 200 and r.get("data", {}).get("mode") in ("recruiter", "general")
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok

    def test_assistant_latex(self) -> bool:
        print("\n" + "="*60)
        print("ASSISTANT TEST: LaTeX Resume via /assistant")
        print("="*60)
        payload = {"message": "Generate resume in LaTeX", "resume_json": {"name": "Jane Doe", "skills": ["Python"]}}
        r = self._post_assistant(payload, timeout=90)
        ok = r.get("status_code") == 200 and r.get("data", {}).get("mode") == "latex_resume"
        print("✅ PASSED" if ok else "❌ FAILED")
        return ok


def main():
    """Main function."""
    import sys
    
    print("Starting Phi-3 LoRA API Tests...")
    print(f"Target: {BASE_URL}")
    
    # Check if API is reachable
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ API is reachable\n")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {BASE_URL}")
        print("Make sure the Flask app is running: python app.py")
        sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL)
    #tester.run_all_tests()
    print("\nRunning assistant-specific tests...")
    # Run assistant tests (these exercise the router and model paths)
    tester.test_assistant_general()
    tester.test_assistant_career()
    tester.test_assistant_resume_eval()
    tester.test_assistant_job_match()
    tester.test_assistant_recruiter()
    tester.test_assistant_latex()


if __name__ == "__main__":
    main()
