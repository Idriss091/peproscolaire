<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile menu overlay -->
    <Transition name="fade">
      <div 
        v-if="sidebarOpen" 
        @click="sidebarOpen = false"
        class="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
      />
    </Transition>

    <!-- Mobile sidebar -->
    <Transition name="slide">
      <div 
        v-if="sidebarOpen"
        class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl lg:hidden"
      >
        <div class="flex items-center justify-between h-16 px-4 border-b">
          <img 
            v-if="tenantLogo" 
            :src="tenantLogo" 
            alt="Logo" 
            class="h-8 w-auto"
          >
          <span v-else class="text-xl font-bold text-indigo-600">
            PeproScolaire
          </span>
          <button
            @click="sidebarOpen = false"
            class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        <nav class="mt-5 px-2">
          <NavigationMenu :items="menuItems" @navigate="sidebarOpen = false" />
        </nav>
      </div>
    </Transition>

    <!-- Desktop sidebar -->
    <div class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div class="flex flex-col flex-1 bg-white border-r border-gray-200">
        <div class="flex items-center h-16 px-4 border-b">
          <img 
            v-if="tenantLogo" 
            :src="tenantLogo" 
            alt="Logo" 
            class="h-8 w-auto"
          >
          <span v-else class="text-xl font-bold text-indigo-600">
            PeproScolaire
          </span>
        </div>
        <nav class="flex-1 mt-5 px-2 pb-4 space-y-1 overflow-y-auto">
          <NavigationMenu :items="menuItems" />
        </nav>
        <div class="flex-shrink-0 flex border-t border-gray-200 p-4">
          <a href="#" class="flex-shrink-0 group block">
            <div class="flex items-center">
              <div>
                <img
                  class="inline-block h-9 w-9 rounded-full"
                  :src="userAvatar"
                  alt=""
                >
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-700 group-hover:text-gray-900">
                  {{ userFullName }}
                </p>
                <p class="text-xs font-medium text-gray-500 group-hover:text-gray-700">
                  {{ userTypeLabel }}
                </p>
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="lg:pl-64 flex flex-col flex-1">
      <!-- Top header -->
      <header class="sticky top-0 z-30 bg-white shadow-sm">
        <div class="px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Mobile menu button -->
            <button
              @click="sidebarOpen = true"
              class="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
            >
              <Bars3Icon class="h-6 w-6" />
            </button>

            <!-- Page title -->
            <h1 class="text-2xl font-semibold text-gray-900">
              {{ pageTitle }}
            </h1>

            <!-- Right side actions -->
            <div class="flex items-center space-x-4">
              <!-- Notifications -->
              <button
                @click="showNotifications = !showNotifications"
                class="relative p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-full"
              >
                <BellIcon class="h-6 w-6" />
                <span 
                  v-if="unreadNotifications > 0"
                  class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"
                />
              </button>

              <!-- User menu -->
              <div class="relative">
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="flex items-center p-2 text-sm rounded-full hover:bg-gray-100"
                >
                  <img
                    class="h-8 w-8 rounded-full"
                    :src="userAvatar"
                    alt=""
                  >
                </button>

                <!-- Dropdown -->
                <Transition name="dropdown">
                  <div
                    v-if="showUserMenu"
                    class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5"
                  >
                    <router-link
                      to="/profile"
                      @click="showUserMenu = false"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Mon profil
                    </router-link>
                    <router-link
                      to="/settings"
                      @click="showUserMenu = false"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Paramètres
                    </router-link>
                    <hr class="my-1">
                    <button
                      @click="handleLogout"
                      class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Déconnexion
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1">
        <div class="py-6 px-4 sm:px-6 lg:px-8">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Notifications panel -->
    <NotificationPanel 
      v-if="showNotifications" 
      @close="showNotifications = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import NavigationMenu from '@/components/layout/NavigationMenu.vue'
import NotificationPanel from '@/components/notifications/NotificationPanel.vue'
import { 
  Bars3Icon, 
  XMarkIcon, 
  BellIcon 
} from '@heroicons/vue/24/outline'
import {
  HomeIcon,
  CalendarIcon,
  BookOpenIcon,
  AcademicCapIcon,
  ClipboardDocumentListIcon,
  EnvelopeIcon,
  UserGroupIcon,
  ChartBarIcon,
  CogIcon,
  ExclamationTriangleIcon,
  BriefcaseIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

// UI state
const sidebarOpen = ref(false)
const showUserMenu = ref(false)
const showNotifications = ref(false)

// User info
const userFullName = computed(() => authStore.userFullName)
const userAvatar = computed(() => authStore.user?.profile?.profile_picture || '/default-avatar.png')
const userTypeLabel = computed(() => {
  const labels = {
    student: 'Élève',
    parent: 'Parent',
    teacher: 'Professeur',
    admin: 'Administration',
    superadmin: 'Super Admin'
  }
  return labels[authStore.userType || 'student']
})

// Notifications
const unreadNotifications = computed(() => notificationsStore.unreadCount)

// Tenant customization
const tenantLogo = computed(() => authStore.user?.school?.logo)

// Page title
const pageTitle = computed(() => route.meta.title || 'PeproScolaire')

// Menu items based on user role
const menuItems = computed(() => {
  const userType = authStore.userType
  
  const baseItems = [
    {
      name: 'Tableau de bord',
      href: `/${userType}/dashboard`,
      icon: HomeIcon,
    }
  ]

  switch (userType) {
    case 'teacher':
      return [
        ...baseItems,
        {
          name: 'Emploi du temps',
          href: '/teacher/timetable',
          icon: CalendarIcon,
        },
        {
          name: 'Cahier de textes',
          href: '/teacher/homework',
          icon: BookOpenIcon,
        },
        {
          name: 'Notes',
          href: '/teacher/grades',
          icon: AcademicCapIcon,
        },
        {
          name: 'Vie scolaire',
          href: '/teacher/attendance',
          icon: ClipboardDocumentListIcon,
        },
        {
          name: 'Messagerie',
          href: '/teacher/messages',
          icon: EnvelopeIcon,
        },
        {
          name: 'Élèves à risque',
          href: '/teacher/risk-detection',
          icon: ExclamationTriangleIcon,
        },
      ]
    
    case 'student':
      return [
        ...baseItems,
        {
          name: 'Emploi du temps',
          href: '/student/timetable',
          icon: CalendarIcon,
        },
        {
          name: 'Devoirs',
          href: '/student/homework',
          icon: BookOpenIcon,
        },
        {
          name: 'Notes',
          href: '/student/grades',
          icon: AcademicCapIcon,
        },
        {
          name: 'Messagerie',
          href: '/student/messages',
          icon: EnvelopeIcon,
        },
        {
          name: 'Stages',
          href: '/student/internships',
          icon: BriefcaseIcon,
        },
      ]
    
    case 'parent':
      return [
        ...baseItems,
        {
          name: 'Suivi enfants',
          href: '/parent/children',
          icon: UserGroupIcon,
        },
        {
          name: 'Emploi du temps',
          href: '/parent/timetable',
          icon: CalendarIcon,
        },
        {
          name: 'Notes',
          href: '/parent/grades',
          icon: AcademicCapIcon,
        },
        {
          name: 'Vie scolaire',
          href: '/parent/attendance',
          icon: ClipboardDocumentListIcon,
        },
        {
          name: 'Messagerie',
          href: '/parent/messages',
          icon: EnvelopeIcon,
        },
      ]
    
    case 'admin':
    case 'superadmin':
      return [
        ...baseItems,
        {
          name: 'Gestion école',
          href: '/admin/school',
          icon: CogIcon,
        },
        {
          name: 'Utilisateurs',
          href: '/admin/users',
          icon: UserGroupIcon,
        },
        {
          name: 'Emplois du temps',
          href: '/admin/timetable',
          icon: CalendarIcon,
        },
        {
          name: 'Statistiques',
          href: '/admin/statistics',
          icon: ChartBarIcon,
        },
        {
          name: 'Détection risques',
          href: '/admin/risk-detection',
          icon: ExclamationTriangleIcon,
        },
        {
          name: 'Paramètres',
          href: '/admin/settings',
          icon: CogIcon,
        },
      ]
    
    default:
      return baseItems
  }
})

// Handle logout
const handleLogout = async () => {
  showUserMenu.value = false
  await authStore.logout()
}

// Close dropdowns when clicking outside
watch(showUserMenu, (value) => {
  if (value) {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.relative')) {
        showUserMenu.value = false
        document.removeEventListener('click', handleClick)
      }
    }
    setTimeout(() => {
      document.addEventListener('click', handleClick)
    }, 0)
  }
})
</script>

<style scoped>
/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.2s;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>