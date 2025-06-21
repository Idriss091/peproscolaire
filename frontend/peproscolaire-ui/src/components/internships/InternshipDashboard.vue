<template>
  <div class="internship-dashboard">
    <!-- Header avec statistiques -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="dashboard-title">Gestion des Stages</h1>
          <p class="dashboard-subtitle">
            Gérez vos candidatures, stages et évaluations en un seul endroit
          </p>
        </div>
        
        <div class="header-actions">
          <button
            @click="showSearchModal = true"
            class="btn btn-primary btn-lg"
          >
            <MagnifyingGlassIcon class="h-5 w-5" />
            Rechercher un stage
          </button>
        </div>
      </div>

      <!-- Statistiques rapides -->
      <div class="stats-grid">
        <StatCard
          v-for="stat in statsCards"
          :key="stat.label"
          :title="stat.label"
          :value="stat.value"
          :change="stat.change"
          :trend="stat.trend"
          :icon="stat.icon"
          :color="stat.color"
          :loading="internshipsStore.loading"
        />
      </div>
    </div>

    <!-- Navigation par onglets -->
    <div class="dashboard-nav">
      <nav class="nav-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'nav-tab',
            { 'nav-tab-active': activeTab === tab.id }
          ]"
        >
          <component :is="tab.icon" class="h-5 w-5" />
          {{ tab.label }}
          <span
            v-if="tab.badge"
            :class="[
              'nav-badge',
              `nav-badge-${tab.badgeColor || 'primary'}`
            ]"
          >
            {{ tab.badge }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Contenu des onglets -->
    <div class="dashboard-content">
      <!-- Onglet Vue d'ensemble -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="content-grid">
          <!-- Stage en cours -->
          <div class="current-internship-card" v-if="currentInternship">
            <div class="card card-gradient">
              <div class="card-header">
                <h3 class="card-title">Stage en cours</h3>
                <BaseDropdown placement="bottom-end">
                  <template #trigger>
                    <button class="btn btn-ghost btn-sm">
                      <EllipsisVerticalIcon class="h-4 w-4" />
                    </button>
                  </template>
                  <div class="py-1">
                    <button class="dropdown-item">Voir les détails</button>
                    <button class="dropdown-item">Télécharger convention</button>
                    <div class="dropdown-divider" />
                    <button class="dropdown-item">Contacter tuteur</button>
                  </div>
                </BaseDropdown>
              </div>
              
              <div class="card-body">
                <div class="internship-info">
                  <div class="company-info">
                    <h4 class="company-name">{{ currentInternship.company_name }}</h4>
                    <p class="internship-period">
                      {{ formatDate(currentInternship.start_date) }} - 
                      {{ formatDate(currentInternship.end_date) }}
                    </p>
                  </div>
                  
                  <div class="progress-section">
                    <div class="progress-header">
                      <span class="progress-label">Progression</span>
                      <span class="progress-value">{{ currentInternship.progress_percentage }}%</span>
                    </div>
                    <BaseProgress
                      :value="currentInternship.progress_percentage"
                      variant="success"
                      size="lg"
                      :animated="true"
                      class="mt-2"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Candidatures récentes -->
          <div class="recent-applications">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">Candidatures récentes</h3>
                <router-link to="/stages/candidatures" class="btn btn-ghost btn-sm">
                  Voir tout
                </router-link>
              </div>
              
              <div class="card-body">
                <div v-if="recentApplications.length === 0" class="empty-state">
                  <BriefcaseIcon class="h-12 w-12 text-gray-400" />
                  <p class="empty-text">Aucune candidature récente</p>
                  <button
                    @click="showSearchModal = true"
                    class="btn btn-primary btn-sm"
                  >
                    Rechercher des stages
                  </button>
                </div>
                
                <div v-else class="applications-list">
                  <ApplicationCard
                    v-for="application in recentApplications"
                    :key="application.id"
                    :application="application"
                    @view="viewApplication"
                    @withdraw="withdrawApplication"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Offres recommandées -->
          <div class="recommended-offers">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">
                  <SparklesIcon class="h-5 w-5 text-ai-500" />
                  Offres recommandées pour vous
                </h3>
              </div>
              
              <div class="card-body">
                <div v-if="recommendedOffers.length === 0" class="empty-state">
                  <MagnifyingGlassIcon class="h-12 w-12 text-gray-400" />
                  <p class="empty-text">Aucune recommandation disponible</p>
                </div>
                
                <div v-else class="offers-list">
                  <OfferCard
                    v-for="offer in recommendedOffers"
                    :key="offer.id"
                    :offer="offer"
                    :compact="true"
                    @view="viewOffer"
                    @apply="applyToOffer"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Alertes et notifications -->
          <div class="alerts-section">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">
                  <BellIcon class="h-5 w-5 text-warning-500" />
                  Alertes importantes
                </h3>
              </div>
              
              <div class="card-body">
                <div class="alerts-list">
                  <BaseAlert
                    v-for="alert in importantAlerts"
                    :key="alert.id"
                    :variant="alert.type"
                    :title="alert.title"
                    :message="alert.message"
                    :closable="false"
                    size="sm"
                    class="mb-3 last:mb-0"
                  />
                  
                  <div v-if="importantAlerts.length === 0" class="empty-state-small">
                    <CheckCircleIcon class="h-8 w-8 text-green-500" />
                    <p class="text-sm text-gray-600">Tout est à jour !</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglet Offres -->
      <div v-if="activeTab === 'offers'" class="tab-content">
        <InternshipOffers />
      </div>

      <!-- Onglet Candidatures -->
      <div v-if="activeTab === 'applications'" class="tab-content">
        <InternshipApplications />
      </div>

      <!-- Onglet Mes Stages -->
      <div v-if="activeTab === 'internships'" class="tab-content">
        <MyInternships />
      </div>

      <!-- Onglet Entreprises -->
      <div v-if="activeTab === 'companies'" class="tab-content">
        <CompaniesDirectory />
      </div>
    </div>

    <!-- Modal de recherche -->
    <InternshipSearchModal
      v-model="showSearchModal"
      @search="handleSearch"
      @apply="handleQuickApply"
    />

    <!-- Chatbot Widget -->
    <ChatbotWidget theme="education" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useInternshipsStore } from '@/stores/internships'
import {
  MagnifyingGlassIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  AcademicCapIcon,
  SparklesIcon,
  BellIcon,
  CheckCircleIcon,
  EllipsisVerticalIcon
} from '@heroicons/vue/24/outline'
import StatCard from '@/components/common/StatCard.vue'
import BaseAlert from '@/components/ui/BaseAlert.vue'
import BaseProgress from '@/components/ui/BaseProgress.vue'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import ChatbotWidget from '@/components/chatbot/ChatbotWidget.vue'

// Composants lazy (chargés à la demande)
const InternshipOffers = defineAsyncComponent(() => import('./InternshipOffers.vue'))
const InternshipApplications = defineAsyncComponent(() => import('./InternshipApplications.vue'))
const MyInternships = defineAsyncComponent(() => import('./MyInternships.vue'))
const CompaniesDirectory = defineAsyncComponent(() => import('./CompaniesDirectory.vue'))
const InternshipSearchModal = defineAsyncComponent(() => import('./InternshipSearchModal.vue'))
const ApplicationCard = defineAsyncComponent(() => import('./ApplicationCard.vue'))
const OfferCard = defineAsyncComponent(() => import('./OfferCard.vue'))

const internshipsStore = useInternshipsStore()

// État local
const activeTab = ref('overview')
const showSearchModal = ref(false)

// Onglets de navigation
const tabs = computed(() => [
  {
    id: 'overview',
    label: 'Vue d\'ensemble',
    icon: AcademicCapIcon
  },
  {
    id: 'offers',
    label: 'Offres',
    icon: MagnifyingGlassIcon,
    badge: internshipsStore.totalOffers || null
  },
  {
    id: 'applications',
    label: 'Candidatures',
    icon: DocumentTextIcon,
    badge: internshipsStore.pendingApplications.length || null,
    badgeColor: 'warning'
  },
  {
    id: 'internships',
    label: 'Mes Stages',
    icon: BriefcaseIcon,
    badge: internshipsStore.internships.filter(i => i.status === 'ongoing').length || null,
    badgeColor: 'success'
  },
  {
    id: 'companies',
    label: 'Entreprises',
    icon: BuildingOfficeIcon
  }
])

// Cartes de statistiques
const statsCards = computed(() => {
  const stats = internshipsStore.stats
  if (!stats) return []

  return [
    {
      label: 'Candidatures',
      value: stats.total_applications,
      change: '+12%',
      trend: 'up',
      icon: DocumentTextIcon,
      color: 'primary'
    },
    {
      label: 'En attente',
      value: stats.pending_applications,
      change: '-5%',
      trend: 'down',
      icon: ClockIcon,
      color: 'warning'
    },
    {
      label: 'Acceptées',
      value: stats.accepted_applications,
      change: '+8%',
      trend: 'up',
      icon: CheckCircleIcon,
      color: 'success'
    },
    {
      label: 'Stages actifs',
      value: stats.ongoing_internships,
      change: 'Stable',
      trend: 'neutral',
      icon: BriefcaseIcon,
      color: 'education'
    }
  ]
})

// Stage en cours
const currentInternship = computed(() => {
  return internshipsStore.internships.find(i => i.status === 'ongoing')
})

// Candidatures récentes
const recentApplications = computed(() => {
  return internshipsStore.applications
    .slice(0, 5)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// Offres recommandées (simulées avec IA)
const recommendedOffers = computed(() => {
  return internshipsStore.offers.slice(0, 3)
})

// Alertes importantes
const importantAlerts = computed(() => {
  const alerts = []

  // Vérifier les dates limites de candidature
  const urgentOffers = internshipsStore.offers.filter(offer => {
    const deadline = new Date(offer.application_deadline)
    const now = new Date()
    const diffDays = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    return diffDays <= 3 && diffDays > 0
  })

  if (urgentOffers.length > 0) {
    alerts.push({
      id: 'urgent-deadlines',
      type: 'warning',
      title: 'Dates limites approchent',
      message: `${urgentOffers.length} offres ferment bientôt. Candidatez rapidement !`
    })
  }

  // Vérifier les documents manquants
  const incompleteApplications = internshipsStore.applications.filter(app => 
    app.status === 'draft' || !app.cv_file
  )

  if (incompleteApplications.length > 0) {
    alerts.push({
      id: 'incomplete-applications',
      type: 'info',
      title: 'Candidatures incomplètes',
      message: `${incompleteApplications.length} candidatures nécessitent des documents.`
    })
  }

  // Vérifier les entretiens programmés
  const upcomingInterviews = internshipsStore.applications.filter(app => 
    app.status === 'interview_scheduled' && app.interview_date
  )

  if (upcomingInterviews.length > 0) {
    alerts.push({
      id: 'upcoming-interviews',
      type: 'success',
      title: 'Entretiens programmés',
      message: `Vous avez ${upcomingInterviews.length} entretiens à venir.`
    })
  }

  return alerts
})

// Méthodes
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const viewApplication = (applicationId: string) => {
  // Navigation vers les détails de la candidature
  console.log('Voir candidature:', applicationId)
}

const withdrawApplication = async (applicationId: string) => {
  try {
    await internshipsStore.withdrawApplication(applicationId)
    // Afficher un toast de succès
  } catch (error) {
    // Afficher un toast d'erreur
    console.error('Erreur retrait candidature:', error)
  }
}

const viewOffer = (offerId: string) => {
  // Navigation vers les détails de l'offre
  console.log('Voir offre:', offerId)
}

const applyToOffer = (offerId: string) => {
  // Navigation vers le formulaire de candidature
  console.log('Candidater à l\'offre:', offerId)
}

const handleSearch = (searchParams: any) => {
  activeTab.value = 'offers'
  // Appliquer les filtres de recherche
  console.log('Recherche:', searchParams)
}

const handleQuickApply = (offerId: string) => {
  applyToOffer(offerId)
  showSearchModal.value = false
}

// Lifecycle
onMounted(async () => {
  try {
    // Charger les données en parallèle
    await Promise.all([
      internshipsStore.loadDashboard(),
      internshipsStore.loadApplications(),
      internshipsStore.loadInternships(),
      internshipsStore.loadOffers({ limit: 10 })
    ])
  } catch (error) {
    console.error('Erreur chargement dashboard:', error)
  }
})
</script>

<style scoped>
.internship-dashboard {
  @apply min-h-screen bg-gray-50;
}

/* Header */
.dashboard-header {
  @apply bg-white border-b border-gray-200 px-6 py-8;
}

.header-content {
  @apply flex items-center justify-between mb-8;
}

.header-text {
  @apply flex-1;
}

.dashboard-title {
  @apply text-3xl font-bold text-gray-900 mb-2;
}

.dashboard-subtitle {
  @apply text-lg text-gray-600;
}

.header-actions {
  @apply flex items-center gap-4;
}

.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6;
}

/* Navigation */
.dashboard-nav {
  @apply bg-white border-b border-gray-200 px-6;
}

.nav-tabs {
  @apply flex space-x-8 overflow-x-auto;
}

.nav-tab {
  @apply flex items-center gap-2 px-4 py-4 text-sm font-medium text-gray-600 hover:text-gray-900 border-b-2 border-transparent hover:border-gray-300 transition-all duration-200 whitespace-nowrap;
}

.nav-tab-active {
  @apply text-education-600 border-education-600 hover:text-education-700 hover:border-education-700;
}

.nav-badge {
  @apply px-2 py-1 text-xs font-semibold rounded-full;
}

.nav-badge-primary {
  @apply bg-primary-100 text-blue-800;
}

.nav-badge-warning {
  @apply bg-warning-100 text-warning-800;
}

.nav-badge-success {
  @apply bg-green-100 text-green-800;
}

/* Contenu */
.dashboard-content {
  @apply p-6;
}

.tab-content {
  @apply space-y-6;
}

.content-grid {
  @apply grid grid-cols-1 lg:grid-cols-3 gap-6;
}

/* Stage en cours */
.current-internship-card {
  @apply lg:col-span-2;
}

.internship-info {
  @apply space-y-4;
}

.company-info {
  @apply space-y-1;
}

.company-name {
  @apply text-xl font-semibold text-gray-900;
}

.internship-period {
  @apply text-gray-600;
}

.progress-section {
  @apply space-y-2;
}

.progress-header {
  @apply flex items-center justify-between;
}

.progress-label {
  @apply text-sm font-medium text-gray-700;
}

.progress-value {
  @apply text-sm font-semibold text-green-600;
}

/* Candidatures et offres */
.recent-applications,
.recommended-offers,
.alerts-section {
  @apply lg:col-span-1;
}

.applications-list,
.offers-list,
.alerts-list {
  @apply space-y-3;
}

/* États vides */
.empty-state {
  @apply flex flex-col items-center justify-center py-8 text-center;
}

.empty-state-small {
  @apply flex flex-col items-center justify-center py-4 text-center;
}

.empty-text {
  @apply text-gray-600 mb-4;
}

/* Responsive */
@media (max-width: 1024px) {
  .content-grid {
    @apply grid-cols-1;
  }
  
  .current-internship-card,
  .recent-applications,
  .recommended-offers,
  .alerts-section {
    @apply lg:col-span-1;
  }
}

@media (max-width: 640px) {
  .dashboard-header {
    @apply px-4 py-6;
  }
  
  .header-content {
    @apply flex-col items-start gap-4;
  }
  
  .dashboard-nav {
    @apply px-4;
  }
  
  .dashboard-content {
    @apply p-4;
  }
  
  .stats-grid {
    @apply grid-cols-2;
  }
}
</style>