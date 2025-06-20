import api from './api'
import type { 
  Company, 
  InternshipOffer, 
  InternshipApplication, 
  Internship,
  InternshipSearch 
} from '@/types/internships'

export const internshipApi = {
  // Entreprises
  async getCompanies(params?: any) {
    const response = await api.get('/internships/companies/', { params })
    return response.data
  },

  async getCompany(companyId: string) {
    const response = await api.get(`/internships/companies/${companyId}/`)
    return response.data
  },

  async getCompanyOffers(companyId: string) {
    const response = await api.get(`/internships/companies/${companyId}/offers/`)
    return response.data
  },

  async getCompanyStats(companyId: string) {
    const response = await api.get(`/internships/companies/${companyId}/stats/`)
    return response.data
  },

  // Offres de stage
  async getOffers(params?: any) {
    const response = await api.get('/internships/offers/', { params })
    return response.data
  },

  async getOffer(offerId: string) {
    const response = await api.get(`/internships/offers/${offerId}/`)
    return response.data
  },

  async searchOffers(data: InternshipSearch) {
    const response = await api.post('/internships/offers/search/', data)
    return response.data
  },

  async getSimilarOffers(offerId: string) {
    const response = await api.get(`/internships/offers/${offerId}/similar/`)
    return response.data
  },

  async applyToOffer(offerId: string, data: any) {
    const response = await api.post(`/internships/offers/${offerId}/apply/`, data)
    return response.data
  },

  // Candidatures
  async getApplications(params?: any) {
    const response = await api.get('/internships/applications/', { params })
    return response.data
  },

  async getApplication(applicationId: string) {
    const response = await api.get(`/internships/applications/${applicationId}/`)
    return response.data
  },

  async createApplication(data: Partial<InternshipApplication>) {
    const response = await api.post('/internships/applications/', data)
    return response.data
  },

  async updateApplication(applicationId: string, data: Partial<InternshipApplication>) {
    const response = await api.patch(`/internships/applications/${applicationId}/`, data)
    return response.data
  },

  async submitApplication(applicationId: string) {
    const response = await api.post(`/internships/applications/${applicationId}/submit/`)
    return response.data
  },

  async withdrawApplication(applicationId: string) {
    const response = await api.post(`/internships/applications/${applicationId}/withdraw/`)
    return response.data
  },

  // Stages
  async getInternships(params?: any) {
    const response = await api.get('/internships/internships/', { params })
    return response.data
  },

  async getInternship(internshipId: string) {
    const response = await api.get(`/internships/internships/${internshipId}/`)
    return response.data
  },

  async getInternshipDocuments(internshipId: string) {
    const response = await api.get(`/internships/internships/${internshipId}/documents/`)
    return response.data
  },

  async uploadReport(internshipId: string, formData: FormData) {
    const response = await api.post(
      `/internships/internships/${internshipId}/upload_report/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  async rateCompany(internshipId: string, data: { rating: number }) {
    const response = await api.post(`/internships/internships/${internshipId}/rate_company/`, data)
    return response.data
  },

  // Visites de stage
  async getVisits(params?: any) {
    const response = await api.get('/internships/visits/', { params })
    return response.data
  },

  async getVisit(visitId: string) {
    const response = await api.get(`/internships/visits/${visitId}/`)
    return response.data
  },

  // Évaluations
  async getEvaluations(params?: any) {
    const response = await api.get('/internships/evaluations/', { params })
    return response.data
  },

  async getEvaluation(evaluationId: string) {
    const response = await api.get(`/internships/evaluations/${evaluationId}/`)
    return response.data
  },

  async createEvaluation(data: any) {
    const response = await api.post('/internships/evaluations/', data)
    return response.data
  },

  async updateEvaluation(evaluationId: string, data: any) {
    const response = await api.patch(`/internships/evaluations/${evaluationId}/`, data)
    return response.data
  },

  // Statistiques
  async getStats() {
    const response = await api.get('/internships/stats/global_stats/')
    return response.data
  },

  async getDashboard() {
    const response = await api.get('/internships/stats/dashboard/')
    return response.data
  },

  async generateReport(data: { start_date: string; end_date: string }) {
    const response = await api.post('/internships/stats/report/', data)
    return response.data
  }
}