<template>
  <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
    <table class="min-w-full divide-y divide-gray-300">
      <!-- Header -->
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            :class="[
              'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
              column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''
            ]"
            @click="column.sortable ? handleSort(column.key) : null"
          >
            <div class="flex items-center space-x-1">
              <span>{{ column.label }}</span>
              <div v-if="column.sortable" class="flex flex-col">
                <ChevronUpIcon
                  :class="[
                    'h-3 w-3',
                    sortBy === column.key && sortOrder === 'asc' 
                      ? 'text-gray-900' 
                      : 'text-gray-400'
                  ]"
                />
                <ChevronDownIcon
                  :class="[
                    'h-3 w-3 -mt-1',
                    sortBy === column.key && sortOrder === 'desc' 
                      ? 'text-gray-900' 
                      : 'text-gray-400'
                  ]"
                />
              </div>
            </div>
          </th>
          <th v-if="hasActions" scope="col" class="relative px-6 py-3">
            <span class="sr-only">Actions</span>
          </th>
        </tr>
      </thead>

      <!-- Body -->
      <tbody class="bg-white divide-y divide-gray-200">
        <tr
          v-for="(item, index) in sortedData"
          :key="getRowKey(item, index)"
          :class="[
            'hover:bg-gray-50',
            isRowSelected(item) ? 'bg-blue-50' : ''
          ]"
          @click="handleRowClick(item)"
        >
          <td
            v-for="column in columns"
            :key="`${getRowKey(item, index)}-${column.key}`"
            class="px-6 py-4 whitespace-nowrap"
          >
            <slot
              :name="`cell-${column.key}`"
              :item="item"
              :value="getValue(item, column.key)"
              :column="column"
            >
              <span :class="column.cellClass || 'text-sm text-gray-900'">
                {{ formatValue(getValue(item, column.key), column) }}
              </span>
            </slot>
          </td>
          
          <td v-if="hasActions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <slot name="actions" :item="item" :index="index">
              <!-- Default actions if none provided -->
            </slot>
          </td>
        </tr>
        
        <!-- Empty state -->
        <tr v-if="sortedData.length === 0">
          <td :colspan="columns.length + (hasActions ? 1 : 0)" class="px-6 py-12 text-center">
            <slot name="empty">
              <div class="text-gray-500">
                <component :is="emptyIcon" class="mx-auto h-12 w-12 text-gray-400" />
                <p class="mt-2 text-sm">{{ emptyMessage }}</p>
              </div>
            </slot>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Loading overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
    >
      <LoadingSpinner size="lg" />
    </div>
  </div>

  <!-- Pagination -->
  <div v-if="pagination && totalItems > 0" class="mt-4">
    <TablePagination
      :current-page="currentPage"
      :total-items="totalItems"
      :items-per-page="itemsPerPage"
      @page-change="$emit('page-change', $event)"
      @size-change="$emit('size-change', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronUpIcon, ChevronDownIcon, TableCellsIcon } from '@heroicons/vue/24/outline'
import LoadingSpinner from './LoadingSpinner.vue'
import TablePagination from './TablePagination.vue'

interface Column {
  key: string
  label: string
  sortable?: boolean
  sortType?: 'string' | 'number' | 'date'
  cellClass?: string
  formatter?: (value: any) => string
}

interface Props {
  columns: Column[]
  data: any[]
  loading?: boolean
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  selectable?: boolean
  selectedItems?: any[]
  rowKey?: string | ((item: any) => string)
  emptyMessage?: string
  emptyIcon?: any
  pagination?: boolean
  currentPage?: number
  totalItems?: number
  itemsPerPage?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  sortOrder: 'asc',
  selectable: false,
  selectedItems: () => [],
  rowKey: 'id',
  emptyMessage: 'Aucune donnée disponible',
  emptyIcon: TableCellsIcon,
  pagination: false,
  currentPage: 1,
  totalItems: 0,
  itemsPerPage: 10
})

const emit = defineEmits<{
  'sort-change': [{ key: string; order: 'asc' | 'desc' }]
  'row-click': [item: any]
  'selection-change': [items: any[]]
  'page-change': [page: number]
  'size-change': [size: number]
}>()

// State
const localSortBy = ref(props.sortBy || '')
const localSortOrder = ref<'asc' | 'desc'>(props.sortOrder)

// Computed
const hasActions = computed(() => !!props.$slots?.actions)

const sortedData = computed(() => {
  if (!localSortBy.value) return props.data

  const column = props.columns.find(col => col.key === localSortBy.value)
  if (!column?.sortable) return props.data

  return [...props.data].sort((a, b) => {
    const aVal = getValue(a, localSortBy.value)
    const bVal = getValue(b, localSortBy.value)

    let comparison = 0

    switch (column.sortType) {
      case 'number':
        comparison = (Number(aVal) || 0) - (Number(bVal) || 0)
        break
      case 'date':
        comparison = new Date(aVal).getTime() - new Date(bVal).getTime()
        break
      default:
        comparison = String(aVal).localeCompare(String(bVal))
    }

    return localSortOrder.value === 'desc' ? -comparison : comparison
  })
})

// Methods
const getValue = (item: any, key: string) => {
  return key.split('.').reduce((obj, k) => obj?.[k], item)
}

const getRowKey = (item: any, index: number) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item)
  }
  return getValue(item, props.rowKey) || index
}

const formatValue = (value: any, column: Column) => {
  if (column.formatter) {
    return column.formatter(value)
  }
  
  if (value === null || value === undefined) {
    return '-'
  }
  
  return String(value)
}

const handleSort = (key: string) => {
  if (localSortBy.value === key) {
    localSortOrder.value = localSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    localSortBy.value = key
    localSortOrder.value = 'asc'
  }

  emit('sort-change', { key: localSortBy.value, order: localSortOrder.value })
}

const handleRowClick = (item: any) => {
  emit('row-click', item)
}

const isRowSelected = (item: any) => {
  if (!props.selectable) return false
  const key = getRowKey(item, 0)
  return props.selectedItems.some(selected => getRowKey(selected, 0) === key)
}
</script>