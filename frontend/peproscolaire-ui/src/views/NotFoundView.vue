<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 text-center">
      <div>
        <h1 class="text-9xl font-bold text-blue-600">404</h1>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          Page non trouvée
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          La page que vous recherchez n'existe pas ou a été déplacée.
        </p>
      </div>
      
      <div class="space-y-4">
        <BaseButton
          variant="primary"
          size="lg"
          @click="goHome"
        >
          Retourner à l'accueil
        </BaseButton>
        
        <BaseButton
          variant="secondary"
          size="lg"
          @click="goBack"
        >
          Retour
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.back()
}
</script>