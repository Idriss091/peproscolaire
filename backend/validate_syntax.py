#!/usr/bin/env python3
"""
Script de validation de la syntaxe Python pour tous les fichiers du projet
"""
import ast
import os
import sys
from pathlib import Path

def validate_python_file(file_path):
    """Valide la syntaxe d'un fichier Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilation du code pour vérifier la syntaxe
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Erreur de syntaxe ligne {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Erreur: {e}"

def find_python_files(directory):
    """Trouve tous les fichiers Python dans un répertoire"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Ignorer les répertoires de cache et environnements virtuels
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Fonction principale"""
    print("🐍 Validation de la syntaxe Python - PeproScolaire Backend")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    python_files = find_python_files(base_dir)
    
    print(f"📝 {len(python_files)} fichiers Python trouvés\n")
    
    valid_files = 0
    invalid_files = 0
    errors = []
    
    for file_path in sorted(python_files):
        relative_path = os.path.relpath(file_path, base_dir)
        is_valid, error_msg = validate_python_file(file_path)
        
        if is_valid:
            print(f"✅ {relative_path}")
            valid_files += 1
        else:
            print(f"❌ {relative_path}")
            print(f"   └─ {error_msg}")
            invalid_files += 1
            errors.append((relative_path, error_msg))
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DE LA VALIDATION")
    print("=" * 60)
    print(f"✅ Fichiers valides : {valid_files}")
    print(f"❌ Fichiers invalides : {invalid_files}")
    print(f"📈 Taux de réussite : {(valid_files / len(python_files) * 100):.1f}%")
    
    if invalid_files > 0:
        print(f"\n🔍 DÉTAIL DES ERREURS:")
        for file_path, error_msg in errors:
            print(f"\n❌ {file_path}")
            print(f"   {error_msg}")
        
        return 1
    else:
        print("\n🎉 Tous les fichiers Python ont une syntaxe valide !")
        return 0

if __name__ == '__main__':
    sys.exit(main())