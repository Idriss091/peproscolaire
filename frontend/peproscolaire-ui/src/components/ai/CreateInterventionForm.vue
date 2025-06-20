<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Type d'intervention *
        </label>
        <select
          v-model="form.type"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">Sélectionner le type</option>
          <option value="academic">Soutien académique</option>
          <option value="behavioral">Accompagnement comportemental</option>
          <option value="social">Aide sociale</option>
          <option value="psychological">Suivi psychologique</option>
          <option value="family">Médiation familiale</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Priorité *
        </label>
        <select
          v-model="form.priority"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="high">Élevée</option>
          <option value="medium">Moyenne</option>
          <option value="low">Faible</option>
        </select>
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Objectifs de l'intervention *
      </label>
      <textarea
        v-model="form.objectives"
        required
        rows="3"
        placeholder="Décrivez les objectifs spécifiques de cette intervention..."
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
      />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Responsable de l'intervention *
      </label>
      <select
        v-model="form.responsibleId"
        required
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
      >
        <option value="">Sélectionner un responsable</option>
        <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
          {{ teacher.name }}
        </option>
      </select>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Date de début prévue *
        </label>
        <input
          v-model="form.startDate"
          type="date"
          required
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Date de fin prévue
        </label>
        <input
          v-model="form.endDate"
          type="date"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        Actions spécifiques
      </label>
      <div class="space-y-2">
        <div
          v-for="(action, index) in form.actions"
          :key="index"
          class="flex items-center space-x-2"
        >
          <input
            v-model="action.title"
            type="text"
            placeholder="Action à mettre en place..."
            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
          <BaseButton
            type="button"
            variant="outline"
            size="sm"
            @click="removeAction(index)"
          >
            Supprimer
          </BaseButton>
        </div>
        <BaseButton
          type="button"
          variant="outline"
          size="sm"
          @click="addAction"
        >
          Ajouter une action
        </BaseButton>
      </div>
    </div>

    <div class="flex justify-end space-x-3 pt-6 border-t">
      <BaseButton
        type="button"
        variant="secondary"
        @click="$emit('close')"
      >
        Annuler
      </BaseButton>
      
      <BaseButton
        type="submit"
        variant="primary"
        :loading="saving"
      >
        Créer l'intervention
      </BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

interface Props {
  studentIds: string[]
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const saving = ref(false)

const teachers = ref([
  { id: '1', name: 'M. Dupont' },
  { id: '2', name: 'Mme Martin' },
  { id: '3', name: 'M. Bernard' }
])

const form = reactive({
  type: '',
  priority: 'medium',
  objectives: '',
  responsibleId: '',
  startDate: '',
  endDate: '',
  actions: [
    { title: '' }
  ]
})

const addAction = () => {
  form.actions.push({ title: '' })
}

const removeAction = (index: number) => {
  if (form.actions.length > 1) {
    form.actions.splice(index, 1)
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    // TODO: Créer l'intervention via l'API
    console.log('Création intervention:', form)
    await new Promise(resolve => setTimeout(resolve, 1000))
    emit('saved')
  } catch (error) {
    console.error('Erreur lors de la création:', error)
  } finally {
    saving.value = false
  }
}
</script>