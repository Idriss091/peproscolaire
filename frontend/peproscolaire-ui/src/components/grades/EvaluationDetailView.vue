<template>
  <div class="space-y-6">
    <!-- En-tête avec statut -->
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ evaluation.name }}</h2>
        <p v-if="evaluation.description" class="mt-1 text-gray-600">{{ evaluation.description }}</p>
      </div>
      <BaseBadge :variant="getStatusColor(evaluation.status)">
        {{ getStatusLabel(evaluation.status) }}
      </BaseBadge>
    </div>

    <!-- Informations générales -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="bg-gray-50 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Détails</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Matière:</span>
            <span class="font-medium">{{ evaluation.subject_name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Classe:</span>
            <span class="font-medium">{{ evaluation.class_name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Type:</span>
            <span class="font-medium">{{ getTypeLabel(evaluation.type) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Date:</span>
            <span class="font-medium">{{ formatDate(evaluation.date) }}</span>
          </div>
          <div v-if="evaluation.duration" class="flex justify-between">
            <span class="text-gray-600">Durée:</span>
            <span class="font-medium">{{ evaluation.duration }}</span>
          </div>
        </div>
      </div>

      <div class="bg-gray-50 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Notation</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Note maximum:</span>
            <span class="font-medium">{{ evaluation.max_value }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Coefficient:</span>
            <span class="font-medium">{{ evaluation.coefficient }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Période:</span>
            <span class="font-medium">{{ evaluation.period }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Publiée:</span>
            <span class="font-medium">{{ evaluation.is_published ? 'Oui' : 'Non' }}</span>
          </div>
        </div>
      </div>

      <div class="bg-gray-50 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-700 mb-2">Progression</h3>
        <div class="space-y-3">
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">Notes saisies</span>
              <span class="font-medium">{{ evaluation.grades_count || 0 }}/{{ evaluation.students_count || 0 }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${getCompletionPercentage()}%` }"
              />
            </div>
          </div>
          <div v-if="evaluation.average" class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ evaluation.average }}/{{ evaluation.max_value }}</div>
            <div class="text-xs text-gray-600">Moyenne de classe</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions rapides -->
    <div class="flex flex-wrap gap-3">
      <BaseButton
        v-if="evaluation.status === 'planned'"
        variant="primary"
        @click="$emit('start', evaluation)"
        class="flex items-center gap-2"
      >
        <PlayIcon class="w-4 h-4" />
        Commencer l'évaluation
      </BaseButton>

      <BaseButton
        v-if="evaluation.status === 'in_progress' || evaluation.status === 'completed'"
        variant="success"
        @click="openGradeEntry"
        class="flex items-center gap-2"
      >
        <PencilIcon class="w-4 h-4" />
        Saisir les notes
      </BaseButton>

      <BaseButton
        v-if="evaluation.status === 'completed'"
        variant="secondary"
        @click="$emit('view-results', evaluation)"
        class="flex items-center gap-2"
      >
        <ChartBarIcon class="w-4 h-4" />
        Voir les résultats
      </BaseButton>

      <BaseButton
        variant="outline"
        @click="$emit('edit', evaluation)"
        class="flex items-center gap-2"
      >
        <PencilSquareIcon class="w-4 h-4" />
        Modifier
      </BaseButton>

      <BaseButton
        variant="secondary"
        @click="exportEvaluation"
        class="flex items-center gap-2"
      >
        <DocumentArrowDownIcon class="w-4 h-4" />
        Exporter
      </BaseButton>
    </div>

    <!-- Statistiques détaillées -->
    <div v-if="evaluation.status !== 'planned'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Répartition des notes -->
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Répartition des notes</h3>
        </template>
        
        <div class="space-y-4">
          <div v-for="range in gradeRanges" :key="range.label" class="flex items-center">
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-1">
                <span>{{ range.label }}</span>
                <span class="font-medium">{{ range.count }} élèves</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-300"
                  :class="range.colorClass"
                  :style="{ width: `${range.percentage}%` }"
                />
              </div>
            </div>
            <div class="ml-4 text-sm font-medium text-gray-600">
              {{ range.percentage }}%
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Élèves en difficulté -->
      <BaseCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900">Points d'attention</h3>
        </template>
        
        <div class="space-y-3">
          <div v-if="strugglingStudents.length > 0">
            <h4 class="text-sm font-medium text-red-700 mb-2">Élèves en difficulté (< 10/20)</h4>
            <div class="space-y-2">
              <div v-for="student in strugglingStudents" :key="student.id" 
                   class="flex justify-between items-center text-sm">
                <span>{{ student.name }}</span>
                <span class="font-medium text-red-600">{{ student.grade }}/{{ evaluation.max_value }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="excellentStudents.length > 0" class="pt-3 border-t">
            <h4 class="text-sm font-medium text-green-700 mb-2">Excellents résultats (≥ 16/20)</h4>
            <div class="space-y-2">
              <div v-for="student in excellentStudents" :key="student.id" 
                   class="flex justify-between items-center text-sm">
                <span>{{ student.name }}</span>
                <span class="font-medium text-green-600">{{ student.grade }}/{{ evaluation.max_value }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="absentStudents.length > 0" class="pt-3 border-t">
            <h4 class="text-sm font-medium text-yellow-700 mb-2">Élèves absents</h4>
            <div class="space-y-2">
              <div v-for="student in absentStudents" :key="student.id" 
                   class="flex justify-between items-center text-sm">
                <span>{{ student.name }}</span>
                <BaseBadge variant="warning" size="sm">Absent</BaseBadge>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>

    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
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
import { computed } from 'vue'
import {
  PlayIcon,
  PencilIcon,
  PencilSquareIcon,
  ChartBarIcon,
  DocumentArrowDownIcon
} from '@heroicons/vue/24/outline'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'

interface Props {
  evaluation: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  edit: [evaluation: any]
  start: [evaluation: any]
  'view-results': [evaluation: any]
}>()

// Données simulées pour les statistiques
const mockGrades = [
  { student_name: 'Marie Dubois', grade: 18 },
  { student_name: 'Pierre Martin', grade: 12 },
  { student_name: 'Sophie Blanc', grade: 8 },
  { student_name: 'Lucas Moreau', grade: 16 },
  { student_name: 'Emma Leroy', grade: 14 }
]

const mockAbsents = [
  { name: 'Jean Dupont' },
  { name: 'Léa Bernard' }
]

// Computed
const getCompletionPercentage = () => {
  if (!props.evaluation.students_count) return 0
  return Math.round((props.evaluation.grades_count / props.evaluation.students_count) * 100)
}

const gradeRanges = computed(() => {
  const totalStudents = props.evaluation.students_count || 0
  if (totalStudents === 0) return []

  // Simulation des données de répartition
  const ranges = [
    { label: 'Excellent (16-20)', count: 2, colorClass: 'bg-green-500' },
    { label: 'Bien (14-16)', count: 1, colorClass: 'bg-blue-500' },
    { label: 'Assez bien (12-14)', count: 1, colorClass: 'bg-yellow-500' },
    { label: 'Passable (10-12)', count: 0, colorClass: 'bg-orange-500' },
    { label: 'Insuffisant (<10)', count: 1, colorClass: 'bg-red-500' }
  ]

  return ranges.map(range => ({
    ...range,
    percentage: totalStudents > 0 ? Math.round((range.count / totalStudents) * 100) : 0
  }))
})

const strugglingStudents = computed(() => {
  return mockGrades.filter(g => g.grade < 10).map(g => ({
    id: g.student_name,
    name: g.student_name,
    grade: g.grade
  }))
})

const excellentStudents = computed(() => {
  return mockGrades.filter(g => g.grade >= 16).map(g => ({
    id: g.student_name,
    name: g.student_name,
    grade: g.grade
  }))
})

const absentStudents = computed(() => {
  return mockAbsents.map((s, index) => ({
    id: `absent-${index}`,
    name: s.name
  }))
})

// Méthodes
const openGradeEntry = () => {
  // TODO: Ouvrir l'interface de saisie des notes
  console.log('Ouvrir la saisie des notes pour:', props.evaluation.id)
}

const exportEvaluation = () => {
  // TODO: Exporter les données de l'évaluation
  console.log('Exporter l\'évaluation:', props.evaluation.id)
  
  const csvContent = generateEvaluationCSV()
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `evaluation-${props.evaluation.name}-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const generateEvaluationCSV = () => {
  const headers = ['Élève', 'Note', 'Commentaire']
  const rows = [headers.join(',')]
  
  mockGrades.forEach(grade => {
    const row = [
      grade.student_name,
      `${grade.grade}/${props.evaluation.max_value}`,
      ''
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// Utilitaires
const getStatusColor = (status: string) => {
  const colors = {
    planned: 'secondary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    planned: 'Planifiée',
    in_progress: 'En cours',
    completed: 'Terminée',
    cancelled: 'Annulée'
  }
  return labels[status as keyof typeof labels] || status
}

const getTypeLabel = (type: string) => {
  const labels = {
    controle: 'Contrôle',
    devoir: 'Devoir',
    interrogation: 'Interrogation',
    examen: 'Examen'
  }
  return labels[type as keyof typeof labels] || type
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>