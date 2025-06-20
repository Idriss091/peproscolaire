<template>
  <div class="flex items-center justify-between">
    <!-- Results info -->
    <div class="flex items-center text-sm text-gray-500">
      <span>
        Affichage de {{ startItem }} à {{ endItem }} sur {{ totalItems }} résultats
      </span>
      
      <!-- Items per page selector -->
      <div class="ml-4 flex items-center space-x-2">
        <label for="page-size" class="text-sm text-gray-500">
          Par page:
        </label>
        <select
          id="page-size"
          :value="itemsPerPage"
          @change="handleSizeChange"
          class="border-gray-300 rounded text-sm focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>

    <!-- Pagination controls -->
    <div class="flex items-center space-x-2">
      <!-- Previous button -->
      <button
        type="button"
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)"
        class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ChevronLeftIcon class="h-5 w-5" />
        <span class="sr-only">Page précédente</span>
      </button>

      <!-- Page numbers -->
      <div class="flex space-x-1">
        <!-- First page -->
        <button
          v-if="showFirstPage"
          type="button"
          @click="goToPage(1)"
          :class="[
            'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
            currentPage === 1
              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
          ]"
        >
          1
        </button>

        <!-- First ellipsis -->
        <span
          v-if="showFirstEllipsis"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
        >
          ...
        </span>

        <!-- Visible pages -->
        <button
          v-for="page in visiblePages"
          :key="page"
          type="button"
          @click="goToPage(page)"
          :class="[
            'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
            currentPage === page
              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
          ]"
        >
          {{ page }}
        </button>

        <!-- Last ellipsis -->
        <span
          v-if="showLastEllipsis"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
        >
          ...
        </span>

        <!-- Last page -->
        <button
          v-if="showLastPage"
          type="button"
          @click="goToPage(totalPages)"
          :class="[
            'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
            currentPage === totalPages
              ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
          ]"
        >
          {{ totalPages }}
        </button>
      </div>

      <!-- Next button -->
      <button
        type="button"
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)"
        class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ChevronRightIcon class="h-5 w-5" />
        <span class="sr-only">Page suivante</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

interface Props {
  currentPage: number
  totalItems: number
  itemsPerPage: number
  maxVisiblePages?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxVisiblePages: 5
})

const emit = defineEmits<{
  'page-change': [page: number]
  'size-change': [size: number]
}>()

// Computed
const totalPages = computed(() => {
  return Math.ceil(props.totalItems / props.itemsPerPage)
})

const startItem = computed(() => {
  return (props.currentPage - 1) * props.itemsPerPage + 1
})

const endItem = computed(() => {
  return Math.min(props.currentPage * props.itemsPerPage, props.totalItems)
})

const visiblePages = computed(() => {
  const delta = Math.floor(props.maxVisiblePages / 2)
  let start = Math.max(1, props.currentPage - delta)
  let end = Math.min(totalPages.value, start + props.maxVisiblePages - 1)

  // Adjust start if we're near the end
  if (end - start + 1 < props.maxVisiblePages) {
    start = Math.max(1, end - props.maxVisiblePages + 1)
  }

  // Don't show pages that would be covered by first/last
  if (start <= 2) start = 1
  if (end >= totalPages.value - 1) end = totalPages.value

  const pages = []
  for (let i = start; i <= end; i++) {
    // Skip first and last page as they're handled separately
    if (i !== 1 && i !== totalPages.value) {
      pages.push(i)
    }
  }

  return pages
})

const showFirstPage = computed(() => {
  return totalPages.value > 1 && !visiblePages.value.includes(1)
})

const showLastPage = computed(() => {
  return totalPages.value > 1 && !visiblePages.value.includes(totalPages.value)
})

const showFirstEllipsis = computed(() => {
  return showFirstPage.value && visiblePages.value.length > 0 && visiblePages.value[0] > 2
})

const showLastEllipsis = computed(() => {
  return showLastPage.value && visiblePages.value.length > 0 && 
         visiblePages.value[visiblePages.value.length - 1] < totalPages.value - 1
})

// Methods
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('page-change', page)
  }
}

const handleSizeChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newSize = parseInt(target.value)
  emit('size-change', newSize)
}
</script>