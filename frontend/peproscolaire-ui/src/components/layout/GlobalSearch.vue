<template>
  <div class="global-search" ref="searchRef">
    <div class="search-input-container">
      <div class="search-icon">
        <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
      </div>
      
      <input
        ref="searchInput"
        v-model="searchQuery"
        type="text"
        placeholder="Rechercher..."
        class="search-input"
        @focus="showResults = true"
        @keydown.escape="closeSearch"
        @keydown.arrow-down.prevent="navigateDown"
        @keydown.arrow-up.prevent="navigateUp"
        @keydown.enter="selectResult"
      />
      
      <div v-if="searchQuery" class="search-clear">
        <button
          @click="clearSearch"
          class="clear-btn"
          aria-label="Effacer"
        >
          <XMarkIcon class="h-4 w-4" />
        </button>
      </div>
      
      <!-- Raccourci clavier -->
      <div v-if="!isMobile && !searchQuery" class="search-shortcut">
        <kbd class="kbd">⌘</kbd>
        <kbd class="kbd">K</kbd>
      </div>
    </div>
    
    <!-- Résultats de recherche -->
    <Transition name="search-results">
      <div v-if="showResults && (searchQuery || recentSearches.length > 0)" class="search-results">
        <div class="results-container">
          <!-- Recherches récentes (quand pas de query) -->
          <div v-if="!searchQuery && recentSearches.length > 0" class="results-section">
            <h3 class="section-title">Recherches récentes</h3>
            <div class="results-list">
              <button
                v-for="(recent, index) in recentSearches"
                :key="recent.id"
                @click="selectRecentSearch(recent)"
                :class="{ 'result-highlighted': focusedIndex === index }"
                class="search-result recent-result"
              >
                <ClockIcon class="result-icon" />
                <span class="result-text">{{ recent.query }}</span>
                <button
                  @click.stop="removeRecentSearch(recent.id)"
                  class="result-action"
                  aria-label="Supprimer"
                >
                  <XMarkIcon class="h-3 w-3" />
                </button>
              </button>
            </div>
          </div>
          
          <!-- Résultats de recherche -->
          <div v-if="searchQuery" class="results-section">
            <div v-if="isLoading" class="loading-state">
              <div class="loading-spinner" />
              <span>Recherche en cours...</span>
            </div>
            
            <div v-else-if="searchResults.length === 0" class="empty-state">
              <MagnifyingGlassIcon class="h-8 w-8 text-gray-400" />
              <span>Aucun résultat pour "{{ searchQuery }}"</span>
            </div>
            
            <div v-else>
              <!-- Résultats par catégorie -->
              <div
                v-for="category in categorizedResults"
                :key="category.type"
                class="results-section"
              >
                <h3 class="section-title">{{ category.label }}</h3>
                <div class="results-list">
                  <router-link
                    v-for="(result, index) in category.results"
                    :key="result.id"
                    :to="result.url"
                    @click="selectResult(result)"
                    :class="{ 'result-highlighted': focusedIndex === getGlobalIndex(category.type, index) }"
                    class="search-result"
                  >
                    <component :is="getResultIcon(result.type)" class="result-icon" />
                    <div class="result-content">
                      <span class="result-title" v-html="highlightMatch(result.title)" />
                      <span v-if="result.subtitle" class="result-subtitle">{{ result.subtitle }}</span>
                    </div>
                    <div class="result-meta">
                      <span class="result-type">{{ getTypeLabel(result.type) }}</span>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Suggestions de recherche -->
          <div v-if="!searchQuery" class="results-section">
            <h3 class="section-title">Suggestions</h3>
            <div class="suggestions-grid">
              <button
                v-for="suggestion in searchSuggestions"
                :key="suggestion.query"
                @click="applySuggestion(suggestion)"
                class="suggestion-chip"
              >
                <component :is="suggestion.icon" class="h-4 w-4" />
                {{ suggestion.query }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  MagnifyingGlassIcon,
  XMarkIcon,
  ClockIcon,
  UserIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'
import { useSearchStore } from '@/stores/search'
import { debounce } from '@/utils/helpers'

interface SearchResult {
  id: string
  title: string
  subtitle?: string
  url: string
  type: 'user' | 'course' | 'document' | 'event' | 'message' | 'page'
  score: number
}

interface RecentSearch {
  id: string
  query: string
  timestamp: number
}

const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()

const searchRef = ref<HTMLElement>()
const searchInput = ref<HTMLInputElement>()
const searchQuery = ref('')
const showResults = ref(false)
const isLoading = ref(false)
const focusedIndex = ref(-1)
const isMobile = ref(false)

const searchResults = ref<SearchResult[]>([])
const recentSearches = ref<RecentSearch[]>([])

// Suggestions de recherche prédéfinies
const searchSuggestions = ref([
  { query: 'Mes notes', icon: AcademicCapIcon },
  { query: 'Emploi du temps', icon: CalendarIcon },
  { query: 'Messages', icon: ChatBubbleLeftRightIcon },
  { query: 'Documents', icon: DocumentTextIcon }
])

const categorizedResults = computed(() => {
  const categories = {
    user: { type: 'user', label: 'Utilisateurs', results: [] as SearchResult[] },
    course: { type: 'course', label: 'Cours', results: [] as SearchResult[] },
    document: { type: 'document', label: 'Documents', results: [] as SearchResult[] },
    event: { type: 'event', label: 'Événements', results: [] as SearchResult[] },
    page: { type: 'page', label: 'Pages', results: [] as SearchResult[] }
  }
  
  searchResults.value.forEach(result => {
    if (categories[result.type]) {
      categories[result.type].results.push(result)
    }
  })
  
  return Object.values(categories).filter(cat => cat.results.length > 0)
})

// Méthodes
const performSearch = debounce(async (query: string) => {
  if (!query.trim()) {
    searchResults.value = []
    isLoading.value = false
    return
  }
  
  isLoading.value = true
  
  try {
    const results = await searchStore.search(query)
    searchResults.value = results
  } catch (error) {
    console.error('Erreur de recherche:', error)
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}, 300)

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  focusedIndex.value = -1
  searchInput.value?.focus()
}

const closeSearch = () => {
  showResults.value = false
  focusedIndex.value = -1
}

const navigateDown = () => {
  const totalResults = getTotalResultsCount()
  if (totalResults > 0) {
    focusedIndex.value = Math.min(focusedIndex.value + 1, totalResults - 1)
  }
}

const navigateUp = () => {
  focusedIndex.value = Math.max(focusedIndex.value - 1, -1)
}

const selectResult = (result?: SearchResult) => {
  if (result) {
    addToRecentSearches(searchQuery.value)
    router.push(result.url)
    closeSearch()
    clearSearch()
  } else {
    // Sélectionner le résultat actuel si pas de résultat spécifique
    const currentResult = getCurrentResult()
    if (currentResult) {
      selectResult(currentResult)
    }
  }
}

const selectRecentSearch = (recent: RecentSearch) => {
  searchQuery.value = recent.query
  showResults.value = true
  performSearch(recent.query)
}

const removeRecentSearch = (id: string) => {
  recentSearches.value = recentSearches.value.filter(search => search.id !== id)
  saveRecentSearches()
}

const applySuggestion = (suggestion: any) => {
  searchQuery.value = suggestion.query
  performSearch(suggestion.query)
}

const addToRecentSearches = (query: string) => {
  if (!query.trim()) return
  
  const existing = recentSearches.value.findIndex(search => search.query === query)
  if (existing >= 0) {
    recentSearches.value.splice(existing, 1)
  }
  
  recentSearches.value.unshift({
    id: Date.now().toString(),
    query,
    timestamp: Date.now()
  })
  
  // Garder seulement les 10 dernières recherches
  recentSearches.value = recentSearches.value.slice(0, 10)
  saveRecentSearches()
}

const saveRecentSearches = () => {
  localStorage.setItem('recent-searches', JSON.stringify(recentSearches.value))
}

const loadRecentSearches = () => {
  try {
    const saved = localStorage.getItem('recent-searches')
    if (saved) {
      recentSearches.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Erreur chargement recherches récentes:', error)
  }
}

const getTotalResultsCount = () => {
  return searchResults.value.length + recentSearches.value.length
}

const getGlobalIndex = (categoryType: string, localIndex: number) => {
  let globalIndex = 0
  
  for (const category of categorizedResults.value) {
    if (category.type === categoryType) {
      return globalIndex + localIndex
    }
    globalIndex += category.results.length
  }
  
  return globalIndex + localIndex
}

const getCurrentResult = () => {
  if (focusedIndex.value < 0) return null
  
  let currentIndex = 0
  for (const category of categorizedResults.value) {
    if (focusedIndex.value < currentIndex + category.results.length) {
      return category.results[focusedIndex.value - currentIndex]
    }
    currentIndex += category.results.length
  }
  
  return null
}

const getResultIcon = (type: string) => {
  const icons = {
    user: UserIcon,
    course: AcademicCapIcon,
    document: DocumentTextIcon,
    event: CalendarIcon,
    message: ChatBubbleLeftRightIcon,
    page: Cog6ToothIcon
  }
  return icons[type] || DocumentTextIcon
}

const getTypeLabel = (type: string) => {
  const labels = {
    user: 'Utilisateur',
    course: 'Cours',
    document: 'Document',
    event: 'Événement',
    message: 'Message',
    page: 'Page'
  }
  return labels[type] || type
}

const highlightMatch = (text: string) => {
  if (!searchQuery.value) return text
  
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark class="search-highlight">$1</mark>')
}

const handleKeyboardShortcut = (event: KeyboardEvent) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
    showResults.value = true
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (!searchRef.value?.contains(event.target as Node)) {
    closeSearch()
  }
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

// Watchers
watch(searchQuery, (newQuery) => {
  performSearch(newQuery)
})

// Lifecycle
onMounted(() => {
  loadRecentSearches()
  handleResize()
  
  document.addEventListener('keydown', handleKeyboardShortcut)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboardShortcut)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.global-search {
  @apply relative;
}

.search-input-container {
  @apply relative flex items-center;
}

.search-icon {
  @apply absolute left-3 z-10;
}

.search-input {
  @apply w-80 pl-10 pr-20 py-2 bg-white border border-gray-300 rounded-lg text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200;
}

@media (max-width: 768px) {
  .search-input {
    @apply w-full;
  }
}

.search-clear {
  @apply absolute right-12 z-10;
}

.clear-btn {
  @apply w-6 h-6 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors;
}

.search-shortcut {
  @apply absolute right-3 flex items-center gap-1;
}

.kbd {
  @apply px-1.5 py-0.5 text-xs font-mono bg-gray-100 border border-gray-300 rounded text-gray-600;
}

.search-results {
  @apply absolute top-full left-0 right-0 mt-2 bg-white rounded-lg border border-gray-200 shadow-xl z-50 max-h-96 overflow-hidden;
}

.results-container {
  @apply max-h-96 overflow-y-auto;
}

.results-section {
  @apply border-b border-gray-100 last:border-b-0;
}

.section-title {
  @apply px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50 border-b border-gray-100;
}

.results-list {
  @apply py-2;
}

.search-result {
  @apply flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left w-full;
}

.result-highlighted {
  @apply bg-primary-50 text-blue-900;
}

.recent-result {
  @apply justify-between;
}

.result-icon {
  @apply h-5 w-5 text-gray-400 flex-shrink-0;
}

.result-content {
  @apply flex-1 min-w-0;
}

.result-title {
  @apply block font-medium text-gray-900 truncate;
}

.result-subtitle {
  @apply block text-sm text-gray-600 truncate;
}

.result-text {
  @apply flex-1 text-gray-700;
}

.result-action {
  @apply w-5 h-5 rounded hover:bg-gray-200 flex items-center justify-center text-gray-400 hover:text-gray-600;
}

.result-meta {
  @apply flex-shrink-0;
}

.result-type {
  @apply text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full;
}

.loading-state {
  @apply flex items-center gap-3 px-4 py-8 text-gray-600;
}

.loading-spinner {
  @apply w-5 h-5 border-2 border-gray-300 border-t-primary-600 rounded-full animate-spin;
}

.empty-state {
  @apply flex flex-col items-center gap-3 px-4 py-8 text-gray-600;
}

.suggestions-grid {
  @apply flex flex-wrap gap-2 p-4;
}

.suggestion-chip {
  @apply inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-sm font-medium transition-colors;
}

:deep(.search-highlight) {
  @apply bg-yellow-200 text-yellow-900 font-semibold;
}

/* Transitions */
.search-results-enter-active,
.search-results-leave-active {
  transition: all 0.2s ease;
}

.search-results-enter-from,
.search-results-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>