<template>
  <div class="max-w-4xl mx-auto">
    <div class="bg-white">
      <!-- En-tête du bulletin -->
      <div class="text-center mb-8 pb-6 border-b">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">BULLETIN SCOLAIRE</h1>
        <div class="text-lg text-gray-700">
          {{ bulletin.period }} - Année {{ bulletin.year }}
        </div>
      </div>

      <!-- Informations élève et établissement -->
      <div class="grid grid-cols-2 gap-8 mb-8">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Informations élève</h3>
          <div class="space-y-2 text-sm">
            <div><strong>Nom:</strong> {{ bulletin.student_name }}</div>
            <div><strong>Classe:</strong> {{ bulletin.class_name }}</div>
            <div><strong>Effectif:</strong> {{ bulletin.class_size }} élèves</div>
            <div><strong>Professeur principal:</strong> {{ bulletin.main_teacher || 'Non défini' }}</div>
          </div>
        </div>
        
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Résultats généraux</h3>
          <div class="space-y-2 text-sm">
            <div><strong>Moyenne générale:</strong> 
              <span class="text-lg font-bold" :class="getAverageColorClass(bulletin.general_average)">
                {{ bulletin.general_average }}/20
              </span>
            </div>
            <div><strong>Rang:</strong> {{ bulletin.rank }}{{ getOrdinalSuffix(bulletin.rank) }} sur {{ bulletin.class_size }}</div>
            <div><strong>Moyenne de classe:</strong> {{ bulletin.class_average || 'N/A' }}/20</div>
            <div><strong>Mention:</strong> {{ getMention(bulletin.general_average) }}</div>
          </div>
        </div>
      </div>

      <!-- Notes par matière -->
      <div class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Résultats par matière</h3>
        <div class="overflow-x-auto">
          <table class="min-w-full border border-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-900">
                  Matières
                </th>
                <th class="border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-900">
                  Moyenne élève
                </th>
                <th class="border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-900">
                  Moyenne classe
                </th>
                <th class="border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-900">
                  Coefficient
                </th>
                <th class="border border-gray-300 px-4 py-2 text-left text-sm font-medium text-gray-900">
                  Appréciation
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subject in bulletin.subject_averages" :key="subject.subject_id" 
                  class="hover:bg-gray-50">
                <td class="border border-gray-300 px-4 py-2 text-sm font-medium">
                  {{ subject.subject_name }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-center text-sm font-semibold"
                    :class="getAverageColorClass(subject.average)">
                  {{ subject.average }}/20
                </td>
                <td class="border border-gray-300 px-4 py-2 text-center text-sm">
                  {{ subject.class_average || 'N/A' }}/20
                </td>
                <td class="border border-gray-300 px-4 py-2 text-center text-sm">
                  {{ subject.coefficient || 1 }}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-sm">
                  {{ subject.teacher_comment || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Vie scolaire -->
      <div class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Vie scolaire</h3>
        <div class="grid grid-cols-3 gap-6">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-red-600">{{ bulletin.absences_count }}</div>
            <div class="text-sm text-gray-600">Demi-journées d'absence</div>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-yellow-600">{{ bulletin.tardiness_count }}</div>
            <div class="text-sm text-gray-600">Retards</div>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ bulletin.sanctions_count || 0 }}</div>
            <div class="text-sm text-gray-600">Sanctions</div>
          </div>
        </div>
      </div>

      <!-- Compétences (si incluses) -->
      <div v-if="bulletin.competences && bulletin.competences.length > 0" class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Évaluation des compétences</h3>
        <div class="space-y-3">
          <div v-for="competence in bulletin.competences" :key="competence.id" 
               class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex-1">
              <div class="font-medium text-sm">{{ competence.code }}</div>
              <div class="text-xs text-gray-600">{{ competence.description }}</div>
            </div>
            <div class="flex items-center space-x-2">
              <div class="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all"
                  :class="getCompetenceLevelColor(competence.level)"
                  :style="{ width: `${(competence.level / 4) * 100}%` }"
                />
              </div>
              <span class="text-sm font-medium">{{ getCompetenceLabel(competence.level) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Appréciation générale -->
      <div class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Appréciation générale</h3>
        <div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p class="text-sm text-blue-900 leading-relaxed">
            {{ bulletin.general_comment || 'Aucune appréciation générale.' }}
          </p>
        </div>
      </div>

      <!-- Signatures -->
      <div class="grid grid-cols-2 gap-8 pt-6 border-t">
        <div class="text-center">
          <div class="text-sm font-medium text-gray-900 mb-4">Le professeur principal</div>
          <div class="h-16 border-b border-gray-300"></div>
          <div class="text-xs text-gray-600 mt-2">{{ bulletin.main_teacher || 'Non défini' }}</div>
        </div>
        <div class="text-center">
          <div class="text-sm font-medium text-gray-900 mb-4">Le responsable légal</div>
          <div class="h-16 border-b border-gray-300"></div>
          <div class="text-xs text-gray-600 mt-2">Signature</div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-8 pt-4 border-t text-xs text-gray-500">
        <p>Bulletin généré le {{ formatDateTime(bulletin.created_at) }}</p>
        <p>Établissement: {{ bulletin.school_name || 'École PeproScolaire' }}</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-center space-x-4 mt-8 pt-6 border-t no-print">
      <BaseButton
        variant="secondary"
        @click="$emit('download', bulletin)"
        class="flex items-center gap-2"
      >
        <DocumentArrowDownIcon class="w-4 h-4" />
        Télécharger PDF
      </BaseButton>
      
      <BaseButton
        v-if="bulletin.status === 'draft'"
        variant="success"
        @click="$emit('publish', bulletin.id)"
        class="flex items-center gap-2"
      >
        <CheckIcon class="w-4 h-4" />
        Publier
      </BaseButton>
      
      <BaseButton
        v-if="bulletin.status === 'published'"
        variant="primary"
        @click="$emit('send', bulletin.id)"
        class="flex items-center gap-2"
      >
        <PaperAirplaneIcon class="w-4 h-4" />
        Envoyer aux parents
      </BaseButton>
      
      <BaseButton
        variant="outline"
        @click="$emit('close')"
      >
        Fermer
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  DocumentArrowDownIcon,
  CheckIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'

interface Props {
  bulletin: any
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  download: [bulletin: any]
  publish: [bulletinId: string]
  send: [bulletinId: string]
}>()

// Utilitaires
const getAverageColorClass = (average: number) => {
  if (average >= 16) return 'text-green-600'
  if (average >= 14) return 'text-blue-600'
  if (average >= 12) return 'text-yellow-600'
  if (average >= 10) return 'text-orange-600'
  return 'text-red-600'
}

const getMention = (average: number) => {
  if (average >= 16) return 'Très bien'
  if (average >= 14) return 'Bien'
  if (average >= 12) return 'Assez bien'
  if (average >= 10) return 'Passable'
  return 'Insuffisant'
}

const getOrdinalSuffix = (rank: number) => {
  if (rank === 1) return 'er'
  return 'ème'
}

const getCompetenceLevelColor = (level: number) => {
  switch (level) {
    case 4: return 'bg-green-500'
    case 3: return 'bg-blue-500'
    case 2: return 'bg-yellow-500'
    case 1: return 'bg-red-500'
    default: return 'bg-gray-300'
  }
}

const getCompetenceLabel = (level: number) => {
  const labels = {
    4: 'Maîtrisé',
    3: 'Satisfaisant',
    2: 'Fragile',
    1: 'Insuffisant'
  }
  return labels[level as keyof typeof labels] || 'Non évalué'
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
  
  .max-w-4xl {
    max-width: none !important;
  }
  
  .mx-auto {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }
}
</style>