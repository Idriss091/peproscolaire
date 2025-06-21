<template>
  <div class="ai-homework-generator">
    <div class="bg-white rounded-lg shadow-md border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center gap-2">
          <svg class="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Générateur de devoirs IA</h3>
        </div>
      </div>
      <div class="px-6 py-4">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Matière</label>
            <select v-model="selectedSubject" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
              <option value="">Sélectionner une matière</option>
              <option value="math">Mathématiques</option>
              <option value="french">Français</option>
              <option value="history">Histoire-Géographie</option>
              <option value="science">Sciences</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Niveau</label>
            <select v-model="selectedLevel" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
              <option value="">Sélectionner un niveau</option>
              <option value="6e">6ème</option>
              <option value="5e">5ème</option>
              <option value="4e">4ème</option>
              <option value="3e">3ème</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Thème / Chapitre</label>
            <input 
              v-model="theme" 
              type="text" 
              placeholder="Ex: Les fractions, La révolution française..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Type d'exercice</label>
            <select v-model="exerciseType" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
              <option value="">Sélectionner un type</option>
              <option value="exercise">Exercices</option>
              <option value="essay">Rédaction</option>
              <option value="quiz">QCM</option>
              <option value="research">Recherche</option>
            </select>
          </div>
          
          <div class="flex justify-end gap-3 pt-4">
            <button 
              @click="resetForm"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors"
            >
              Réinitialiser
            </button>
            <button 
              @click="generateHomework"
              :disabled="!canGenerate || isGenerating"
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <svg v-if="isGenerating" class="animate-spin h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isGenerating ? 'Génération...' : 'Générer le devoir' }}
            </button>
          </div>
        </div>
        
        <div v-if="generatedHomework" class="mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <h4 class="font-medium text-purple-900 mb-2">Devoir généré :</h4>
          <div class="text-sm text-purple-800 whitespace-pre-wrap">{{ generatedHomework }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const selectedSubject = ref('')
const selectedLevel = ref('')
const theme = ref('')
const exerciseType = ref('')
const isGenerating = ref(false)
const generatedHomework = ref('')

const canGenerate = computed(() => {
  return selectedSubject.value && selectedLevel.value && theme.value && exerciseType.value
})

const generateHomework = async () => {
  if (!canGenerate.value) return
  
  isGenerating.value = true
  
  // Simulation de génération IA
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  generatedHomework.value = `Devoir de ${selectedSubject.value} - ${selectedLevel.value}

Thème : ${theme.value}
Type : ${exerciseType.value}

Exercice généré automatiquement par l'IA :

1. Exercice principal sur le thème "${theme.value}"
2. Questions de compréhension
3. Application pratique
4. Exercices d'approfondissement

Durée estimée : 45 minutes
Niveau de difficulté : Adapté à la classe de ${selectedLevel.value}

[Contenu détaillé généré par l'IA...]`
  
  isGenerating.value = false
}

const resetForm = () => {
  selectedSubject.value = ''
  selectedLevel.value = ''
  theme.value = ''
  exerciseType.value = ''
  generatedHomework.value = ''
}
</script>

<style scoped>
.ai-homework-generator {
  /* Styles pour le générateur de devoirs IA */
}
</style>