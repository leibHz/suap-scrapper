import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title.upper()} ".center(50, "="))
    print(f"{'='*50}\n")

def test_endpoint(method, path, data=None):
    url = f"{BASE_URL}{path}"
    print(f"Testing {method} {url}...")
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            print("Response (JSON):")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        elif "text/csv" in content_type:
            print("Response (CSV - first 5 lines):")
            lines = response.text.splitlines()
            for line in lines[:5]:
                print(f"  {line}")
            if len(lines) > 5:
                print(f"  ... ({len(lines) - 5} more lines)")
        else:
            print("Response (Raw):")
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Is it running?")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")

def main():
    print_header("SUAP Scrapper API Tester")
    
    # Check health first
    test_endpoint("GET", "/health")
    
    # Get credentials
    usuario = input("\nDigite seu usuário (ex: BP123456): ").strip().upper()
    senha = input("Digite sua senha: ").strip()
    disciplina = input("Digite a disciplina (opcional, Enter para 'todas'): ").strip() or "todas"
    
    creds = {"usuario": usuario, "senha": senha}
    advanced_creds = {"usuario": usuario, "senha": senha, "disciplina": disciplina}
    
    endpoints = [
        ("POST", "/validar-login", creds),
        ("POST", "/perfil", creds),
        ("POST", "/disciplinas", creds),
        ("POST", "/boletim", creds),
        ("POST", "/criterios-avaliacao", advanced_creds),
        ("POST", "/plano-de-aulas", advanced_creds),
    ]
    
    for method, path, data in endpoints:
        print_header(f"Testing {path}")
        test_endpoint(method, path, data)
        input("\nPressione Enter para o próximo teste...")

    print_header("Testes concluídos")

if __name__ == "__main__":
    main()
