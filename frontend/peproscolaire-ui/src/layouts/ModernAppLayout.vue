<template>
  <div :class="layoutClasses" class="app-layout">
    <!-- Sidebar Navigation -->
    <Transition name="slide-x">
      <nav
        v-if="showSidebar"
        :class="sidebarClasses"
        class="app-sidebar"
      >
        <!-- Logo et titre -->
        <div class="sidebar-header">
          <div class="logo-container">
            <img src="/logo.svg" alt="PeproScolaire" class="logo" />
            <h1 v-if="!isCollapsed" class="app-title">PeproScolaire</h1>
          </div>
          
          <!-- Toggle collapse -->
          <button
            v-if="!isMobile"
            @click="toggleCollapse"
            class="collapse-btn"
            aria-label="Réduire la navigation"
          >
            <ChevronLeftIcon
              :class="{ 'rotate-180': isCollapsed }"
              class="h-5 w-5 transition-transform duration-200"
            />
          </button>
        </div>

        <!-- Navigation principale -->
        <div class="sidebar-nav">
          <div class="nav-section">
            <h2 v-if="!isCollapsed" class="nav-section-title">Principal</h2>
            
            <NavLink
              v-for="item in mainNavItems"
              :key="item.to"
              :to="item.to"
              :icon="item.icon"
              :label="item.label"
              :badge="item.badge"
              :collapsed="isCollapsed"
              @click="handleNavClick"
            />
          </div>

          <div class="nav-section">
            <h2 v-if="!isCollapsed" class="nav-section-title">Modules IA</h2>
            
            <NavLink
              v-for="item in aiNavItems"
              :key="item.to"
              :to="item.to"
              :icon="item.icon"
              :label="item.label"
              :badge="item.badge"
              :collapsed="isCollapsed"
              :ai="true"
              @click="handleNavClick"
            />
          </div>

          <div class="nav-section">
            <h2 v-if="!isCollapsed" class="nav-section-title">Outils</h2>
            
            <NavLink
              v-for="item in toolsNavItems"
              :key="item.to"
              :to="item.to"
              :icon="item.icon"
              :label="item.label"
              :collapsed="isCollapsed"
              @click="handleNavClick"
            />
          </div>
        </div>

        <!-- Utilisateur et paramètres -->
        <div class="sidebar-footer">
          <BaseDropdown
            placement="top-start"
            :width="isCollapsed ? 'auto' : 'trigger'"
          >
            <template #trigger>
              <div :class="userMenuClasses" class="user-menu-trigger">
                <UserAvatar
                  :user="userStore.currentUser"
                  :size="isCollapsed ? 'sm' : 'md'"
                />
                <div v-if="!isCollapsed" class="user-info">
                  <p class="user-name">{{ userStore.currentUser?.full_name }}</p>
                  <p class="user-role">{{ getUserRole() }}</p>
                </div>
                <ChevronUpIcon v-if="!isCollapsed" class="h-4 w-4 text-neutral-400" />
              </div>
            </template>

            <div class="py-1">
              <router-link to="/profil" class="dropdown-item">
                <UserIcon class="h-4 w-4" />
                Mon profil
              </router-link>
              <router-link to="/parametres" class="dropdown-item">
                <Cog6ToothIcon class="h-4 w-4" />
                Paramètres
              </router-link>
              <div class="dropdown-divider" />
              <button @click="toggleTheme" class="dropdown-item">
                <component :is="themeIcon" class="h-4 w-4" />
                {{ themeStore.isDark ? 'Mode clair' : 'Mode sombre' }}
              </button>
              <div class="dropdown-divider" />
              <button @click="logout" class="dropdown-item dropdown-item-danger">
                <ArrowRightOnRectangleIcon class="h-4 w-4" />
                Déconnexion
              </button>
            </div>
          </BaseDropdown>
        </div>
      </nav>
    </Transition>

    <!-- Overlay mobile -->
    <Transition name="fade">
      <div
        v-if="isMobile && showSidebar"
        @click="closeMobileSidebar"
        class="mobile-overlay"
      />
    </Transition>

    <!-- Contenu principal -->
    <div :class="mainClasses" class="app-main">
      <!-- Header -->
      <header class="app-header">
        <div class="header-left">
          <!-- Menu mobile -->
          <button
            v-if="isMobile"
            @click="toggleMobileSidebar"
            class="mobile-menu-btn"
            aria-label="Menu"
          >
            <Bars3Icon class="h-6 w-6" />
          </button>

          <!-- Breadcrumb -->
          <nav class="breadcrumb">
            <ol class="breadcrumb-list">
              <li
                v-for="(crumb, index) in breadcrumbs"
                :key="crumb.to || crumb.label"
                class="breadcrumb-item"
              >
                <router-link
                  v-if="crumb.to && index < breadcrumbs.length - 1"
                  :to="crumb.to"
                  class="breadcrumb-link"
                >
                  {{ crumb.label }}
                </router-link>
                <span v-else class="breadcrumb-current">
                  {{ crumb.label }}
                </span>
                <ChevronRightIcon
                  v-if="index < breadcrumbs.length - 1"
                  class="breadcrumb-separator"
                />
              </li>
            </ol>
          </nav>
        </div>

        <div class="header-right">
          <!-- Recherche globale -->
          <GlobalSearch />

          <!-- Notifications -->
          <NotificationCenter />

          <!-- Quick actions -->
          <QuickActions />
        </div>
      </header>

      <!-- Zone de contenu -->
      <main class="app-content">
        <router-view v-slot="{ Component, route }">
          <Transition :name="pageTransition" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </router-view>
      </main>

      <!-- Footer -->
      <footer class="app-footer">
        <div class="footer-content">
          <p class="footer-text">
            © 2024 PeproScolaire. Système de gestion scolaire intelligent.
          </p>
          <div class="footer-links">
            <a href="/aide" class="footer-link">Aide</a>
            <a href="/support" class="footer-link">Support</a>
            <a href="/confidentialite" class="footer-link">Confidentialité</a>
          </div>
        </div>
      </footer>
    </div>

    <!-- Chatbot Widget -->
    <ChatbotWidget v-if="showChatbot" />

    <!-- Toast Container -->
    <div id="toast-container" class="toast-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useNotificationsStore } from '@/stores/notifications'
import {
  Bars3Icon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  HomeIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  CalendarIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  SparklesIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import BaseDropdown from '@/components/ui/BaseDropdown.vue'
import NavLink from '@/components/layout/NavLink.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import GlobalSearch from '@/components/layout/GlobalSearch.vue'
import NotificationCenter from '@/components/layout/NotificationCenter.vue'
import QuickActions from '@/components/layout/QuickActions.vue'
import ChatbotWidget from '@/components/chatbot/ChatbotWidget.vue'

const route = useRoute()
const userStore = useAuthStore()
const themeStore = useThemeStore()
const notificationsStore = useNotificationsStore()

// État local
const isCollapsed = ref(false)
const showSidebar = ref(true)
const isMobile = ref(false)
const pageTransition = ref('slide-right')

// Navigation items
const mainNavItems = computed(() => [
  {
    to: '/dashboard',
    icon: HomeIcon,
    label: 'Tableau de bord'
  },
  {
    to: '/notes',
    icon: AcademicCapIcon,
    label: 'Notes & Évaluations'
  },
  {
    to: '/emploi-du-temps',
    icon: CalendarIcon,
    label: 'Emploi du temps'
  },
  {
    to: '/devoirs',
    icon: ClipboardDocumentListIcon,
    label: 'Devoirs',
    badge: 3 // Exemple
  },
  {
    to: '/presence',
    icon: UserGroupIcon,
    label: 'Présences'
  },
  {
    to: '/messages',
    icon: ChatBubbleLeftRightIcon,
    label: 'Messages',
    badge: notificationsStore.unreadCount
  }
])

const aiNavItems = computed(() => [
  {
    to: '/ia/detection-risque',
    icon: ChartBarIcon,
    label: 'Détection de risque'
  },
  {
    to: '/ia/appreciations',
    icon: SparklesIcon,
    label: 'Appréciations IA'
  },
  {
    to: '/stages',
    icon: BriefcaseIcon,
    label: 'Gestion des stages'
  }
])

const toolsNavItems = computed(() => [
  {
    to: '/dossiers',
    icon: DocumentTextIcon,
    label: 'Dossiers scolaires'
  },
  {
    to: '/parametres',
    icon: CogIcon,
    label: 'Paramètres'
  }
])

// Computed classes
const layoutClasses = computed(() => [
  'app-layout',
  {
    'layout-mobile': isMobile.value,
    'layout-collapsed': isCollapsed.value && !isMobile.value,
    'layout-dark': themeStore.isDark
  }
])

const sidebarClasses = computed(() => [
  'app-sidebar',
  {
    'sidebar-collapsed': isCollapsed.value,
    'sidebar-mobile': isMobile.value
  }
])

const mainClasses = computed(() => [
  'app-main',
  {
    'main-shifted': !isCollapsed.value && !isMobile.value,
    'main-collapsed': isCollapsed.value && !isMobile.value
  }
])

const userMenuClasses = computed(() => [
  'user-menu-trigger',
  {
    'user-menu-collapsed': isCollapsed.value
  }
])

const showChatbot = computed(() => {
  // Afficher le chatbot selon la route
  return !route.path.includes('/auth/')
})

const themeIcon = computed(() => {
  return themeStore.isDark ? SunIcon : MoonIcon
})

// Breadcrumbs
const breadcrumbs = computed(() => {
  const pathSegments = route.path.split('/').filter(Boolean)
  const crumbs = [{ label: 'Accueil', to: '/dashboard' }]
  
  // Mapper les segments vers des labels lisibles
  const segmentLabels: Record<string, string> = {
    'dashboard': 'Tableau de bord',
    'notes': 'Notes',
    'emploi-du-temps': 'Emploi du temps',
    'devoirs': 'Devoirs',
    'presence': 'Présences',
    'messages': 'Messages',
    'ia': 'Intelligence Artificielle',
    'detection-risque': 'Détection de risque',
    'appreciations': 'Appréciations',
    'stages': 'Stages',
    'dossiers': 'Dossiers scolaires',
    'parametres': 'Paramètres'
  }
  
  pathSegments.forEach((segment, index) => {
    const label = segmentLabels[segment] || segment
    const to = index === pathSegments.length - 1 ? undefined : `/${pathSegments.slice(0, index + 1).join('/')}`
    crumbs.push({ label, to })
  })
  
  return crumbs.slice(1) // Remove duplicate home
})

// Méthodes
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar-collapsed', isCollapsed.value.toString())
}

const toggleMobileSidebar = () => {
  showSidebar.value = !showSidebar.value
}

const closeMobileSidebar = () => {
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleNavClick = () => {
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const handleResize = () => {
  const mobile = window.innerWidth < 1024
  
  if (mobile !== isMobile.value) {
    isMobile.value = mobile
    
    if (mobile) {
      showSidebar.value = false
      isCollapsed.value = false
    } else {
      showSidebar.value = true
      // Restaurer l'état depuis localStorage
      const saved = localStorage.getItem('sidebar-collapsed')
      isCollapsed.value = saved === 'true'
    }
  }
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const getUserRole = () => {
  const user = userStore.currentUser
  if (!user) return ''
  
  const roleLabels: Record<string, string> = {
    'student': 'Étudiant',
    'teacher': 'Enseignant',
    'parent': 'Parent',
    'admin': 'Administrateur'
  }
  
  return roleLabels[user.role] || user.role
}

const logout = async () => {
  try {
    await userStore.logout()
    // La redirection sera gérée par le guard de navigation
  } catch (error) {
    console.error('Erreur déconnexion:', error)
  }
}

// Gestion des transitions de page
watch(() => route.path, (newPath, oldPath) => {
  if (!oldPath) return
  
  // Détecter la direction de navigation
  const newDepth = newPath.split('/').length
  const oldDepth = oldPath.split('/').length
  
  pageTransition.value = newDepth > oldDepth ? 'slide-left' : 'slide-right'
})

// Lifecycle
onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  
  // Restaurer l'état de la sidebar
  const saved = localStorage.getItem('sidebar-collapsed')
  if (saved && !isMobile.value) {
    isCollapsed.value = saved === 'true'
  }
  
  // Charger les notifications
  notificationsStore.loadNotifications()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.app-layout {
  @apply flex h-screen bg-neutral-50 overflow-hidden;
}

/* Sidebar */
.app-sidebar {
  @apply fixed lg:relative z-30 h-full bg-white border-r border-neutral-200 flex flex-col transition-all duration-300;
  width: 280px;
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-mobile {
  @apply shadow-xl;
}

.sidebar-header {
  @apply flex items-center justify-between p-4 border-b border-neutral-200;
}

.logo-container {
  @apply flex items-center gap-3;
}

.logo {
  @apply h-8 w-8 flex-shrink-0;
}

.app-title {
  @apply text-xl font-bold text-neutral-900 transition-opacity duration-200;
}

.sidebar-collapsed .app-title {
  @apply opacity-0;
}

.collapse-btn {
  @apply w-8 h-8 rounded-lg bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center text-neutral-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500;
}

.sidebar-nav {
  @apply flex-1 overflow-y-auto py-4 space-y-6;
}

.nav-section {
  @apply px-4 space-y-2;
}

.nav-section-title {
  @apply text-xs font-semibold text-neutral-500 uppercase tracking-wider px-3 py-2;
}

.sidebar-collapsed .nav-section-title {
  @apply hidden;
}

.sidebar-footer {
  @apply p-4 border-t border-neutral-200;
}

.user-menu-trigger {
  @apply flex items-center gap-3 w-full p-3 rounded-lg hover:bg-neutral-100 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary-500;
}

.user-menu-collapsed {
  @apply justify-center;
}

.user-info {
  @apply flex-1 min-w-0;
}

.user-name {
  @apply font-medium text-neutral-900 truncate;
}

.user-role {
  @apply text-sm text-neutral-600;
}

.sidebar-collapsed .user-info {
  @apply hidden;
}

/* Mobile overlay */
.mobile-overlay {
  @apply fixed inset-0 bg-black/50 z-20 lg:hidden;
}

/* Main content */
.app-main {
  @apply flex-1 flex flex-col min-w-0 transition-all duration-300;
}

.main-shifted {
  @apply lg:ml-0;
}

.main-collapsed {
  @apply lg:ml-0;
}

/* Header */
.app-header {
  @apply flex items-center justify-between px-6 py-4 bg-white border-b border-neutral-200;
}

.header-left {
  @apply flex items-center gap-4;
}

.mobile-menu-btn {
  @apply w-10 h-10 rounded-lg bg-neutral-100 hover:bg-neutral-200 flex items-center justify-center text-neutral-600 transition-colors lg:hidden focus:outline-none focus:ring-2 focus:ring-primary-500;
}

.breadcrumb-list {
  @apply flex items-center space-x-2;
}

.breadcrumb-item {
  @apply flex items-center;
}

.breadcrumb-link {
  @apply text-neutral-600 hover:text-neutral-900 transition-colors;
}

.breadcrumb-current {
  @apply font-medium text-neutral-900;
}

.breadcrumb-separator {
  @apply h-4 w-4 text-neutral-400 mx-2;
}

.header-right {
  @apply flex items-center gap-4;
}

/* Content */
.app-content {
  @apply flex-1 overflow-auto;
}

/* Footer */
.app-footer {
  @apply bg-white border-t border-neutral-200 px-6 py-4;
}

.footer-content {
  @apply flex items-center justify-between;
}

.footer-text {
  @apply text-sm text-neutral-600;
}

.footer-links {
  @apply flex items-center gap-4;
}

.footer-link {
  @apply text-sm text-neutral-600 hover:text-neutral-900 transition-colors;
}

/* Transitions */
.slide-x-enter-active,
.slide-x-leave-active {
  transition: transform 0.3s ease;
}

.slide-x-enter-from {
  transform: translateX(-100%);
}

.slide-x-leave-to {
  transform: translateX(-100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Page transitions */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}

.slide-right-enter-from {
  transform: translateX(-30px);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(30px);
  opacity: 0;
}

/* Toast container */
.toast-container {
  @apply fixed top-4 right-4 z-50 space-y-2;
}

/* Responsive */
@media (max-width: 1023px) {
  .app-sidebar {
    @apply -translate-x-full;
    width: 280px;
  }
  
  .app-sidebar.sidebar-mobile {
    @apply translate-x-0;
  }
  
  .app-main {
    @apply ml-0;
  }
  
  .breadcrumb {
    @apply hidden sm:block;
  }
  
  .footer-content {
    @apply flex-col items-start gap-2;
  }
}

/* Dark mode */
.layout-dark {
  @apply bg-neutral-900;
}

.layout-dark .app-sidebar {
  @apply bg-neutral-800 border-neutral-700;
}

.layout-dark .app-header {
  @apply bg-neutral-800 border-neutral-700;
}

.layout-dark .app-footer {
  @apply bg-neutral-800 border-neutral-700;
}
</style>