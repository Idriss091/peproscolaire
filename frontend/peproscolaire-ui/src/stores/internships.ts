import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { internshipApi } from '@/services/internships'
import type { 
  Company, 
  InternshipOffer, 
  InternshipApplication, 
  Internship,
  InternshipStats 
} from '@/types/internships'

export const useInternshipsStore = defineStore('internships', () => {
  // État des entreprises
  const companies = ref<Company[]>([])
  const currentCompany = ref<Company | null>(null)
  
  // État des offres
  const offers = ref<InternshipOffer[]>([])
  const currentOffer = ref<InternshipOffer | null>(null)
  const totalOffers = ref(0)
  
  // État des candidatures
  const applications = ref<InternshipApplication[]>([])
  const currentApplication = ref<InternshipApplication | null>(null)
  
  // État des stages
  const internships = ref<Internship[]>([])
  const currentInternship = ref<Internship | null>(null)
  
  // Statistiques
  const stats = ref<InternshipStats | null>(null)
  
  // État de l'interface
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')
  const selectedFilters = ref({
    sector: '',
    city: '',
    offerType: '',
    isPaid: null as boolean | null,
    remotePossible: null as boolean | null,
    startDateFrom: '',
    startDateTo: ''
  })

  // Getters
  const filteredOffers = computed(() => {
    let filtered = offers.value

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(offer => 
        offer.title.toLowerCase().includes(query) ||
        offer.company_name.toLowerCase().includes(query) ||
        offer.description.toLowerCase().includes(query)
      )
    }

    if (selectedFilters.value.sector) {
      filtered = filtered.filter(offer => 
        offer.company_details?.sector === selectedFilters.value.sector
      )
    }

    if (selectedFilters.value.city) {
      filtered = filtered.filter(offer => 
        offer.company_details?.city?.toLowerCase().includes(
          selectedFilters.value.city.toLowerCase()
        )
      )
    }

    if (selectedFilters.value.offerType) {
      filtered = filtered.filter(offer => 
        offer.offer_type === selectedFilters.value.offerType
      )
    }

    if (selectedFilters.value.isPaid !== null) {
      filtered = filtered.filter(offer => 
        offer.is_paid === selectedFilters.value.isPaid
      )
    }

    if (selectedFilters.value.remotePossible !== null) {
      filtered = filtered.filter(offer => 
        offer.remote_possible === selectedFilters.value.remotePossible
      )
    }

    return filtered
  })

  const myApplications = computed(() => 
    applications.value.filter(app => app.status !== 'withdrawn')
  )

  const pendingApplications = computed(() => 
    applications.value.filter(app => 
      ['submitted', 'under_review'].includes(app.status)
    )
  )

  const acceptedApplications = computed(() => 
    applications.value.filter(app => app.status === 'accepted')
  )

  const currentInternshipProgress = computed(() => {
    if (!currentInternship.value || currentInternship.value.status !== 'ongoing') {
      return null
    }
    return {
      percentage: currentInternship.value.progress_percentage,
      status: currentInternship.value.status,
      startDate: currentInternship.value.start_date,
      endDate: currentInternship.value.end_date
    }
  })

  // Actions - Entreprises
  const loadCompanies = async (filters: any = {}) => {
    try {
      loading.value = true
      error.value = null
      const data = await internshipApi.getCompanies(filters)
      companies.value = data.results || data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des entreprises'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadCompany = async (companyId: string) => {
    try {
      loading.value = true
      const company = await internshipApi.getCompany(companyId)
      currentCompany.value = company
      return company
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement de l\'entreprise'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Actions - Offres
  const loadOffers = async (filters: any = {}) => {
    try {
      loading.value = true
      error.value = null
      const data = await internshipApi.getOffers(filters)
      offers.value = data.results || data
      totalOffers.value = data.count || data.length
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des offres'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadOffer = async (offerId: string) => {
    try {
      loading.value = true
      const offer = await internshipApi.getOffer(offerId)
      currentOffer.value = offer
      return offer
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement de l\'offre'
      throw err
    } finally {
      loading.value = false
    }
  }

  const searchOffers = async (searchParams: any) => {
    try {
      loading.value = true
      error.value = null
      const data = await internshipApi.searchOffers(searchParams)
      offers.value = data.results || data
      totalOffers.value = data.total || data.length
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la recherche'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSimilarOffers = async (offerId: string) => {
    try {
      const similarOffers = await internshipApi.getSimilarOffers(offerId)
      return similarOffers
    } catch (err: any) {
      console.error('Erreur lors du chargement des offres similaires:', err)
      return []
    }
  }

  // Actions - Candidatures
  const loadApplications = async () => {
    try {
      loading.value = true
      error.value = null
      const data = await internshipApi.getApplications()
      applications.value = data.results || data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des candidatures'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadApplication = async (applicationId: string) => {
    try {
      loading.value = true
      const application = await internshipApi.getApplication(applicationId)
      currentApplication.value = application
      return application
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement de la candidature'
      throw err
    } finally {
      loading.value = false
    }
  }

  const applyToOffer = async (offerId: string, applicationData: any) => {
    try {
      loading.value = true
      error.value = null
      const application = await internshipApi.applyToOffer(offerId, applicationData)
      
      // Ajouter la candidature à la liste
      applications.value.unshift(application)
      
      return application
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la candidature'
      throw err
    } finally {
      loading.value = false
    }
  }

  const submitApplication = async (applicationId: string) => {
    try {
      loading.value = true
      const response = await internshipApi.submitApplication(applicationId)
      
      // Mettre à jour le statut dans la liste
      const index = applications.value.findIndex(app => app.id === applicationId)
      if (index >= 0) {
        applications.value[index].status = response.status
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la soumission'
      throw err
    } finally {
      loading.value = false
    }
  }

  const withdrawApplication = async (applicationId: string) => {
    try {
      loading.value = true
      const response = await internshipApi.withdrawApplication(applicationId)
      
      // Mettre à jour le statut dans la liste
      const index = applications.value.findIndex(app => app.id === applicationId)
      if (index >= 0) {
        applications.value[index].status = response.status
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du retrait'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Actions - Stages
  const loadInternships = async () => {
    try {
      loading.value = true
      error.value = null
      const data = await internshipApi.getInternships()
      internships.value = data.results || data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des stages'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadInternship = async (internshipId: string) => {
    try {
      loading.value = true
      const internship = await internshipApi.getInternship(internshipId)
      currentInternship.value = internship
      return internship
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du stage'
      throw err
    } finally {
      loading.value = false
    }
  }

  const uploadReport = async (internshipId: string, file: File) => {
    try {
      loading.value = true
      const formData = new FormData()
      formData.append('report_file', file)
      
      const response = await internshipApi.uploadReport(internshipId, formData)
      
      // Mettre à jour le stage dans la liste
      const index = internships.value.findIndex(int => int.id === internshipId)
      if (index >= 0) {
        internships.value[index] = { ...internships.value[index], final_report: response.file_url }
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'upload'
      throw err
    } finally {
      loading.value = false
    }
  }

  const rateCompany = async (internshipId: string, rating: number) => {
    try {
      loading.value = true
      const response = await internshipApi.rateCompany(internshipId, { rating })
      
      // Mettre à jour le stage dans la liste
      const index = internships.value.findIndex(int => int.id === internshipId)
      if (index >= 0) {
        internships.value[index].student_rating = rating
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'évaluation'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Actions - Statistiques
  const loadStats = async () => {
    try {
      loading.value = true
      const data = await internshipApi.getStats()
      stats.value = data
      return data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des statistiques'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadDashboard = async () => {
    try {
      loading.value = true
      const data = await internshipApi.getDashboard()
      stats.value = data
      return data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du tableau de bord'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Actions - Filtres et recherche
  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const updateFilters = (newFilters: Partial<typeof selectedFilters.value>) => {
    selectedFilters.value = { ...selectedFilters.value, ...newFilters }
  }

  const clearFilters = () => {
    selectedFilters.value = {
      sector: '',
      city: '',
      offerType: '',
      isPaid: null,
      remotePossible: null,
      startDateFrom: '',
      startDateTo: ''
    }
    searchQuery.value = ''
  }

  // Actions - Gestion d'état
  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    companies.value = []
    currentCompany.value = null
    offers.value = []
    currentOffer.value = null
    applications.value = []
    currentApplication.value = null
    internships.value = []
    currentInternship.value = null
    stats.value = null
    error.value = null
    clearFilters()
  }

  return {
    // État
    companies,
    currentCompany,
    offers,
    currentOffer,
    totalOffers,
    applications,
    currentApplication,
    internships,
    currentInternship,
    stats,
    loading,
    error,
    searchQuery,
    selectedFilters,

    // Getters
    filteredOffers,
    myApplications,
    pendingApplications,
    acceptedApplications,
    currentInternshipProgress,

    // Actions - Entreprises
    loadCompanies,
    loadCompany,

    // Actions - Offres
    loadOffers,
    loadOffer,
    searchOffers,
    getSimilarOffers,

    // Actions - Candidatures
    loadApplications,
    loadApplication,
    applyToOffer,
    submitApplication,
    withdrawApplication,

    // Actions - Stages
    loadInternships,
    loadInternship,
    uploadReport,
    rateCompany,

    // Actions - Statistiques
    loadStats,
    loadDashboard,

    // Actions - Interface
    setSearchQuery,
    updateFilters,
    clearFilters,
    clearError,
    reset
  }
})