<template>
  <AppLayout>
    <div class="max-w-3xl mx-auto space-y-6">
      <!-- Page header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          Mon profil
        </h1>
        <p class="text-gray-600">
          Gérez vos informations personnelles et paramètres de compte
        </p>
      </div>

      <!-- Profile form -->
      <BaseCard title="Informations personnelles">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <BaseInput
              v-model="form.first_name"
              label="Prénom"
              required
              :error="errors.first_name"
              :disabled="isLoading"
            />
            
            <BaseInput
              v-model="form.last_name"
              label="Nom"
              required
              :error="errors.last_name"
              :disabled="isLoading"
            />
          </div>
          
          <BaseInput
            v-model="form.email"
            type="email"
            label="Adresse email"
            required
            :error="errors.email"
            :disabled="isLoading"
          />
          
          <div class="flex justify-end space-x-3">
            <BaseButton
              type="button"
              variant="secondary"
              @click="resetForm"
              :disabled="isLoading"
            >
              Annuler
            </BaseButton>
            
            <BaseButton
              type="submit"
              variant="primary"
              :loading="isLoading"
              :disabled="!hasChanges"
            >
              Enregistrer
            </BaseButton>
          </div>
        </form>
      </BaseCard>

      <!-- Change password -->
      <BaseCard title="Changer le mot de passe">
        <form @submit.prevent="handlePasswordChange" class="space-y-6">
          <BaseInput
            v-model="passwordForm.old_password"
            type="password"
            label="Mot de passe actuel"
            required
            :error="passwordErrors.old_password"
            :disabled="isLoadingPassword"
          />
          
          <BaseInput
            v-model="passwordForm.new_password"
            type="password"
            label="Nouveau mot de passe"
            required
            :error="passwordErrors.new_password"
            :disabled="isLoadingPassword"
            hint="Au moins 8 caractères"
          />
          
          <BaseInput
            v-model="passwordForm.new_password_confirm"
            type="password"
            label="Confirmer le nouveau mot de passe"
            required
            :error="passwordErrors.new_password_confirm"
            :disabled="isLoadingPassword"
          />
          
          <div class="flex justify-end">
            <BaseButton
              type="submit"
              variant="primary"
              :loading="isLoadingPassword"
              :disabled="!isPasswordFormValid"
            >
              Changer le mot de passe
            </BaseButton>
          </div>
        </form>
      </BaseCard>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { toast } from 'vue-sonner'

const authStore = useAuthStore()

// State
const isLoading = ref(false)
const isLoadingPassword = ref(false)

const form = ref({
  first_name: '',
  last_name: '',
  email: ''
})

const errors = ref({
  first_name: '',
  last_name: '',
  email: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const passwordErrors = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const originalForm = ref({
  first_name: '',
  last_name: '',
  email: ''
})

// Computed
const hasChanges = computed(() => {
  return Object.keys(form.value).some(key => 
    form.value[key] !== originalForm.value[key]
  )
})

const isPasswordFormValid = computed(() => {
  return passwordForm.value.old_password &&
         passwordForm.value.new_password &&
         passwordForm.value.new_password_confirm &&
         passwordForm.value.new_password === passwordForm.value.new_password_confirm
})

// Methods
const initializeForm = () => {
  if (authStore.user) {
    const userData = {
      first_name: authStore.user.first_name || '',
      last_name: authStore.user.last_name || '',
      email: authStore.user.email || ''
    }
    
    form.value = { ...userData }
    originalForm.value = { ...userData }
  }
}

const validateForm = () => {
  errors.value = {
    first_name: '',
    last_name: '',
    email: ''
  }
  
  let isValid = true
  
  if (!form.value.first_name.trim()) {
    errors.value.first_name = 'Le prénom est requis'
    isValid = false
  }
  
  if (!form.value.last_name.trim()) {
    errors.value.last_name = 'Le nom est requis'
    isValid = false
  }
  
  if (!form.value.email.trim()) {
    errors.value.email = 'L\'email est requis'
    isValid = false
  } else if (!form.value.email.includes('@')) {
    errors.value.email = 'Format d\'email invalide'
    isValid = false
  }
  
  return isValid
}

const validatePasswordForm = () => {
  passwordErrors.value = {
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  }
  
  let isValid = true
  
  if (!passwordForm.value.old_password) {
    passwordErrors.value.old_password = 'Le mot de passe actuel est requis'
    isValid = false
  }
  
  if (!passwordForm.value.new_password) {
    passwordErrors.value.new_password = 'Le nouveau mot de passe est requis'
    isValid = false
  } else if (passwordForm.value.new_password.length < 8) {
    passwordErrors.value.new_password = 'Le mot de passe doit contenir au moins 8 caractères'
    isValid = false
  }
  
  if (!passwordForm.value.new_password_confirm) {
    passwordErrors.value.new_password_confirm = 'La confirmation est requise'
    isValid = false
  } else if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    passwordErrors.value.new_password_confirm = 'Les mots de passe ne correspondent pas'
    isValid = false
  }
  
  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  try {
    const success = await authStore.updateProfile({
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email
    })
    
    if (success) {
      toast.success('Profil mis à jour avec succès')
      originalForm.value = { ...form.value }
    } else {
      toast.error('Erreur lors de la mise à jour du profil')
    }
  } finally {
    isLoading.value = false
  }
}

const handlePasswordChange = async () => {
  if (!validatePasswordForm()) return
  
  isLoadingPassword.value = true
  
  try {
    const success = await authStore.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      new_password_confirm: passwordForm.value.new_password_confirm
    })
    
    if (success) {
      toast.success('Mot de passe changé avec succès')
      // Reset form
      passwordForm.value = {
        old_password: '',
        new_password: '',
        new_password_confirm: ''
      }
    } else {
      toast.error('Erreur lors du changement de mot de passe')
    }
  } finally {
    isLoadingPassword.value = false
  }
}

const resetForm = () => {
  form.value = { ...originalForm.value }
  errors.value = {
    first_name: '',
    last_name: '',
    email: ''
  }
}

// Lifecycle
onMounted(() => {
  initializeForm()
})
</script>