<template>
  <div :class="avatarClasses" class="user-avatar">
    <img
      v-if="user?.avatar_url"
      :src="user.avatar_url"
      :alt="displayName"
      class="avatar-image"
      @error="showInitials = true"
    />
    
    <div v-else class="avatar-initials">
      {{ initials }}
    </div>
    
    <!-- Indicateur de statut -->
    <div v-if="showStatus" :class="statusClasses" class="status-indicator" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface User {
  id: string
  full_name?: string
  first_name?: string
  last_name?: string
  email: string
  avatar_url?: string
  is_online?: boolean
  role?: string
}

interface Props {
  user: User | null
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  showStatus?: boolean
  shape?: 'circle' | 'square'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showStatus: false,
  shape: 'circle'
})

const showInitials = ref(false)

const displayName = computed(() => {
  if (!props.user) return 'Utilisateur'
  return props.user.full_name || 
         `${props.user.first_name || ''} ${props.user.last_name || ''}`.trim() || 
         props.user.email
})

const initials = computed(() => {
  if (!props.user) return 'U'
  
  const name = displayName.value
  const parts = name.split(' ').filter(Boolean)
  
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
  }
  
  return name.substring(0, 2).toUpperCase()
})

const avatarClasses = computed(() => [
  'user-avatar',
  `avatar-${props.size}`,
  `avatar-${props.shape}`,
  {
    'avatar-online': props.user?.is_online,
    'avatar-with-status': props.showStatus
  }
])

const statusClasses = computed(() => [
  'status-indicator',
  {
    'status-online': props.user?.is_online,
    'status-offline': !props.user?.is_online
  }
])
</script>

<style scoped>
.user-avatar {
  @apply relative inline-flex items-center justify-center bg-neutral-200 text-neutral-600 font-semibold overflow-hidden;
}

.avatar-circle {
  @apply rounded-full;
}

.avatar-square {
  @apply rounded-lg;
}

.avatar-xs {
  @apply w-6 h-6 text-xs;
}

.avatar-sm {
  @apply w-8 h-8 text-sm;
}

.avatar-md {
  @apply w-10 h-10 text-base;
}

.avatar-lg {
  @apply w-12 h-12 text-lg;
}

.avatar-xl {
  @apply w-16 h-16 text-xl;
}

.avatar-image {
  @apply w-full h-full object-cover;
}

.avatar-initials {
  @apply flex items-center justify-center w-full h-full;
}

.status-indicator {
  @apply absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white;
}

.avatar-xs .status-indicator {
  @apply w-2 h-2 border;
}

.avatar-sm .status-indicator {
  @apply w-2.5 h-2.5 border;
}

.avatar-lg .status-indicator,
.avatar-xl .status-indicator {
  @apply w-4 h-4;
}

.status-online {
  @apply bg-success-500;
}

.status-offline {
  @apply bg-neutral-400;
}

/* Couleurs de rôle */
.user-avatar[data-role="admin"] {
  @apply bg-danger-100 text-danger-700;
}

.user-avatar[data-role="teacher"] {
  @apply bg-primary-100 text-primary-700;
}

.user-avatar[data-role="student"] {
  @apply bg-education-100 text-education-700;
}

.user-avatar[data-role="parent"] {
  @apply bg-secondary-100 text-secondary-700;
}
</style>