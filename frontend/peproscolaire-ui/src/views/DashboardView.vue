<template>
  <div class="min-h-screen bg-gray-50">
    <div class="py-6 px-4 sm:px-6 lg:px-8">
      <!-- Page header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Tableau de bord
        </h1>
        <p class="mt-1 text-gray-600">
          Bienvenue {{ authStore.userFullName || 'Utilisateur' }}
        </p>
      </div>
      
      <!-- Quick stats -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard
          v-for="stat in quickStats"
          :key="stat.name"
          :title="stat.name"
          :value="stat.value"
          :icon="stat.icon"
          :color="stat.color"
          :change="stat.change"
        />
      </div>
      
      <!-- Content by user type -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Quick actions -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Actions rapides</h2>
          <div class="space-y-2">
            <router-link
              v-if="authStore.userType === 'teacher'"
              to="/timetable"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              📅 Voir l'emploi du temps
            </router-link>
            <router-link
              v-if="authStore.userType === 'teacher'"
              to="/attendance"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              ✓ Faire l'appel
            </router-link>
            <router-link
              to="/messaging"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              💬 Voir les messages
            </router-link>
            <router-link
              v-if="authStore.userType === 'student'"
              to="/homework"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              📚 Mes devoirs
            </router-link>
          </div>
        </div>
        
        <!-- Recent activity -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Activité récente</h2>
          <div class="space-y-3">
            <div class="flex items-center space-x-3">
              <div class="h-2 w-2 bg-green-400 rounded-full"></div>
              <p class="text-sm text-gray-600">Nouvelle note en Mathématiques</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="h-2 w-2 bg-blue-400 rounded-full"></div>
              <p class="text-sm text-gray-600">Message de M. Dupont</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="h-2 w-2 bg-yellow-400 rounded-full"></div>
              <p class="text-sm text-gray-600">Devoir à rendre demain</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Default content for other user types -->
      <div class="text-center py-12">
        <div class="mx-auto h-12 w-12 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Bienvenue dans PeproScolaire</h3>
        <p class="mt-1 text-sm text-gray-500">Votre tableau de bord personnalisé sera bientôt disponible.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/common/StatCard.vue'
import {
  AcademicCapIcon,
  BookOpenIcon,
  ClockIcon,
  UserGroupIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

// Quick stats based on user type
const quickStats = computed(() => {
  const userType = authStore.userType
  
  switch (userType) {
    case 'teacher':
      return [
        {
          name: 'Cours aujourd\'hui',
          value: '5',
          icon: ClockIcon,
          color: 'blue'
        },
        {
          name: 'Devoirs à corriger',
          value: '12',
          icon: BookOpenIcon,
          color: 'orange',
          change: 3
        },
        {
          name: 'Appels en attente',
          value: '2',
          icon: UserGroupIcon,
          color: 'red'
        },
        {
          name: 'Messages non lus',
          value: '7',
          icon: AcademicCapIcon,
          color: 'green'
        }
      ]
    
    case 'student':
      return [
        {
          name: 'Cours aujourd\'hui',
          value: '6',
          icon: ClockIcon,
          color: 'blue'
        },
        {
          name: 'Devoirs à rendre',
          value: '4',
          icon: BookOpenIcon,
          color: 'orange'
        },
        {
          name: 'Moyenne générale',
          value: '14.2',
          icon: AcademicCapIcon,
          color: 'green',
          change: 0.3
        },
        {
          name: 'Messages non lus',
          value: '2',
          icon: UserGroupIcon,
          color: 'purple'
        }
      ]
    
    case 'parent':
      return [
        {
          name: 'Enfants suivis',
          value: '2',
          icon: UserGroupIcon,
          color: 'blue'
        },
        {
          name: 'Cours cette semaine',
          value: '24',
          icon: ClockIcon,
          color: 'green'
        },
        {
          name: 'Nouvelles notes',
          value: '5',
          icon: AcademicCapIcon,
          color: 'orange'
        },
        {
          name: 'Messages importants',
          value: '1',
          icon: BookOpenIcon,
          color: 'red'
        }
      ]
    
    case 'admin':
      return [
        {
          name: 'Élèves totaux',
          value: '1,247',
          icon: UserGroupIcon,
          color: 'blue'
        },
        {
          name: 'Professeurs actifs',
          value: '68',
          icon: AcademicCapIcon,
          color: 'green'
        },
        {
          name: 'Classes',
          value: '42',
          icon: BookOpenIcon,
          color: 'purple'
        },
        {
          name: 'Incidents signalés',
          value: '3',
          icon: ClockIcon,
          color: 'red'
        }
      ]
    
    default:
      return []
  }
})

// Lifecycle
onMounted(() => {
  // Fetch dashboard data based on user type
  console.log('Dashboard mounted for user type:', authStore.userType)
})
</script>

<style scoped>
/* Dashboard specific styles */
</style>