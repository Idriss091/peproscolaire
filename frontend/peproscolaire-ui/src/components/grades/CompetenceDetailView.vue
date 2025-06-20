<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ competence.code }}</h2>
        <p class="mt-1 text-gray-600">{{ competence.description }}</p>
      </div>
      <div class="flex items-center space-x-2">
        <BaseBadge :variant="getStatusColor(competence.status)">
          {{ getStatusLabel(competence.status) }}
        </BaseBadge>
        <BaseBadge variant="secondary">{{ competence.level }}</BaseBadge>
      </div>
    </div>

    <!-- Informations générales -->
    <BaseCard>
      <h3 class="text-lg font-medium text-gray-900 mb-4">Informations générales</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <dt class="text-sm font-medium text-gray-500">Matière</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ competence.subject_name }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-gray-500">Domaine</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ getDomainLabel(competence.domain) }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-gray-500">Niveau</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ competence.level }}</dd>
        </div>
        <div>
          <dt class="text-sm font-medium text-gray-500">Statut</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ getStatusLabel(competence.status) }}</dd>
        </div>
      </div>
    </BaseCard>

    <!-- Critères d'évaluation -->
    <BaseCard v-if="competence.criteria && competence.criteria.length > 0">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Critères d'évaluation</h3>
      <ul class="space-y-2">
        <li
          v-for="(criterion, index) in competence.criteria"
          :key="index"
          class="flex items-start space-x-2"
        >
          <CheckCircleIcon class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
          <span class="text-sm text-gray-700">{{ criterion }}</span>
        </li>
      </ul>
    </BaseCard>

    <!-- Statistiques d'évaluation -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard
        title="Évaluations"
        :value="competence.evaluations_count || 0"
        color="blue"
        :icon="DocumentTextIcon"
      />
      <StatCard
        title="Élèves évalués"
        :value="competence.students_count || 0"
        color="green"
        :icon="UsersIcon"
      />
      <StatCard
        title="Maîtrise moyenne"
        :value="`${competence.average_mastery || 0}%`"
        :color="getMasteryColor(competence.average_mastery || 0)"
        :icon="ChartBarIcon"
      />
    </div>

    <!-- Graphique de maîtrise -->
    <BaseCard v-if="competence.average_mastery > 0">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Répartition de la maîtrise</h3>
      <div class="space-y-4">
        <!-- Barre de progression globale -->
        <div>
          <div class="flex justify-between text-sm text-gray-600 mb-2">
            <span>Maîtrise globale</span>
            <span>{{ competence.average_mastery }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3">
            <div 
              class="h-3 rounded-full transition-all duration-300"
              :class="getMasteryColorClass(competence.average_mastery)"
              :style="{ width: `${competence.average_mastery}%` }"
            />
          </div>
        </div>

        <!-- Répartition détaillée (simulée) -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div class="p-3 bg-red-50 rounded-lg">
            <div class="text-lg font-semibold text-red-700">{{ masteryDistribution.insufficient }}%</div>
            <div class="text-xs text-red-600">Insuffisant</div>
          </div>
          <div class="p-3 bg-yellow-50 rounded-lg">
            <div class="text-lg font-semibold text-yellow-700">{{ masteryDistribution.fragile }}%</div>
            <div class="text-xs text-yellow-600">Fragile</div>
          </div>
          <div class="p-3 bg-blue-50 rounded-lg">
            <div class="text-lg font-semibold text-blue-700">{{ masteryDistribution.satisfactory }}%</div>
            <div class="text-xs text-blue-600">Satisfaisant</div>
          </div>
          <div class="p-3 bg-green-50 rounded-lg">
            <div class="text-lg font-semibold text-green-700">{{ masteryDistribution.good }}%</div>
            <div class="text-xs text-green-600">Très bon</div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Historique des évaluations -->
    <BaseCard v-if="recentEvaluations.length > 0">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Évaluations récentes</h3>
      <div class="space-y-3">
        <div
          v-for="evaluation in recentEvaluations"
          :key="evaluation.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div>
            <div class="text-sm font-medium text-gray-900">{{ evaluation.name }}</div>
            <div class="text-xs text-gray-500">{{ formatDate(evaluation.date) }}</div>
          </div>
          <div class="text-right">
            <div class="text-sm font-medium text-gray-900">
              {{ evaluation.students_evaluated }} élèves
            </div>
            <div class="text-xs text-gray-500">
              Moyenne: {{ evaluation.average_score }}%
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Actions -->
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Fermer
      </BaseButton>
      <BaseButton
        variant="outline"
        @click="$emit('edit', competence)"
        class="flex items-center gap-2"
      >
        <PencilIcon class="w-4 h-4" />
        Modifier
      </BaseButton>
      <BaseButton
        variant="primary"
        @click="$emit('evaluate', competence)"
        class="flex items-center gap-2"
      >
        <ClipboardDocumentCheckIcon class="w-4 h-4" />
        Évaluer
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import {
  CheckCircleIcon,
  DocumentTextIcon,
  UsersIcon,
  ChartBarIcon,
  PencilIcon,
  ClipboardDocumentCheckIcon
} from '@heroicons/vue/24/outline'

import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import StatCard from '@/components/common/StatCard.vue'

const props = defineProps<{
  competence: any
}>()

const emit = defineEmits(['close', 'edit', 'evaluate'])

// Données simulées pour la répartition de maîtrise
const masteryDistribution = computed(() => {
  const mastery = props.competence.average_mastery || 0
  // Simulation basée sur la moyenne
  if (mastery >= 80) {
    return { insufficient: 5, fragile: 15, satisfactory: 35, good: 45 }
  } else if (mastery >= 60) {
    return { insufficient: 10, fragile: 25, satisfactory: 40, good: 25 }
  } else if (mastery >= 40) {
    return { insufficient: 20, fragile: 35, satisfactory: 30, good: 15 }
  } else {
    return { insufficient: 40, fragile: 30, satisfactory: 20, good: 10 }
  }
})

// Évaluations récentes simulées
const recentEvaluations = computed(() => [
  {
    id: '1',
    name: 'Contrôle sur les fractions',
    date: new Date('2024-01-15'),
    students_evaluated: 25,
    average_score: 78
  },
  {
    id: '2',
    name: 'Évaluation pratique',
    date: new Date('2024-01-08'),
    students_evaluated: 23,
    average_score: 82
  }
])

// Utilitaires
const domains = {
  nombres: 'Nombres et calculs',
  geometrie: 'Géométrie',
  mesures: 'Grandeurs et mesures',
  donnees: 'Organisation et gestion de données'
}

const getDomainLabel = (domain: string) => {
  return domains[domain as keyof typeof domains] || domain
}

const getStatusColor = (status: string) => {
  const colors = {
    active: 'success',
    inactive: 'secondary'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusLabel = (status: string) => {
  const labels = {
    active: 'Active',
    inactive: 'Inactive'
  }
  return labels[status as keyof typeof labels] || status
}

const getMasteryColor = (mastery: number) => {
  if (mastery >= 80) return 'green'
  if (mastery >= 60) return 'blue'
  if (mastery >= 40) return 'yellow'
  return 'red'
}

const getMasteryColorClass = (mastery: number) => {
  if (mastery >= 80) return 'bg-green-500'
  if (mastery >= 60) return 'bg-blue-500'
  if (mastery >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

const formatDate = (date: Date) => {
  return format(date, 'dd MMMM yyyy', { locale: fr })
}
</script>