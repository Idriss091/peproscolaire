#!/usr/bin/env python3
"""
Script pour corriger les imports manquants dans tous les fichiers views.py
"""
import os
import re

def fix_views_imports(file_path):
    """Corrige les imports dans un fichier views.py"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le fichier utilise @api_view ou @permission_classes
        if '@api_view' in content or '@permission_classes' in content:
            # Vérifier si les imports sont déjà présents
            needs_api_view = '@api_view' in content and 'api_view' not in content.split('\n')[0:20]
            needs_permission_classes = '@permission_classes' in content and 'permission_classes' not in content.split('\n')[0:20]
            
            if needs_api_view or needs_permission_classes:
                # Chercher la ligne d'import existante des decorators
                lines = content.split('\n')
                found = False
                
                for i, line in enumerate(lines):
                    if 'from rest_framework.decorators import' in line:
                        # Ajouter les imports manquants
                        imports = []
                        if 'action' in line:
                            imports.append('action')
                        if needs_api_view and 'api_view' not in line:
                            imports.append('api_view')
                        if needs_permission_classes and 'permission_classes' not in line:
                            imports.append('permission_classes')
                        
                        if len(imports) > 0:
                            lines[i] = f"from rest_framework.decorators import {', '.join(imports)}"
                            found = True
                            break
                
                if not found:
                    # Ajouter l'import après les autres imports rest_framework
                    for i, line in enumerate(lines):
                        if 'from rest_framework import' in line:
                            imports = []
                            if needs_api_view:
                                imports.append('api_view')
                            if needs_permission_classes:
                                imports.append('permission_classes')
                            
                            if len(imports) > 0:
                                lines.insert(i+1, f"from rest_framework.decorators import {', '.join(imports)}")
                                break
                
                # Écrire le fichier corrigé
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Corrigé: {file_path}")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Erreur pour {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 Correction des imports dans les fichiers views.py...")
    
    backend_path = "/home/walid/peproscolaire/backend/apps"
    fixed_count = 0
    
    # Parcourir tous les dossiers d'apps
    for app_dir in os.listdir(backend_path):
        app_path = os.path.join(backend_path, app_dir)
        if os.path.isdir(app_path):
            views_file = os.path.join(app_path, "views.py")
            if os.path.exists(views_file):
                if fix_views_imports(views_file):
                    fixed_count += 1
    
    print(f"\n📊 {fixed_count} fichier(s) corrigé(s)")
    print("✅ Correction terminée")

if __name__ == "__main__":
    main()