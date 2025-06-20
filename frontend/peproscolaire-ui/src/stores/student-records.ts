import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { studentRecordsApi } from '@/api/student-records'
import type { 
  StudentRecord,
  Document,
  DocumentCategory,
  TransferRecord 
} from '@/types'

export const useStudentRecordsStore = defineStore('studentRecords', () => {
  // État
  const studentRecords = ref<StudentRecord[]>([])
  const currentStudentRecord = ref<StudentRecord | null>(null)
  const documents = ref<Document[]>([])
  const documentCategories = ref<DocumentCategory[]>([])
  const documentTypes = ref<any[]>([])
  const transferHistory = ref<TransferRecord[]>([])
  
  const loading = ref({
    studentRecords: false,
    documents: false,
    upload: false,
    categories: false,
    stats: false
  })
  
  const error = ref<string | null>(null)
  
  // Pagination
  const studentRecordsPagination = ref({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    current_page: 1
  })
  
  const documentsPagination = ref({
    count: 0,
    next: null as string | null,
    previous: null as string | null,
    current_page: 1
  })
  
  // Computed
  const activeStudentRecords = computed(() => {
    return studentRecords.value.filter(record => record.status === 'active')
  })
  
  const documentsByStatus = computed(() => {
    const grouped = {
      pending: 0,
      approved: 0,
      rejected: 0,
      expired: 0
    }
    
    documents.value.forEach(doc => {
      if (doc.status in grouped) {
        grouped[doc.status as keyof typeof grouped]++
      }
    })
    
    return grouped
  })
  
  const requiredDocuments = computed(() => {
    return documents.value.filter(doc => doc.is_required)
  })
  
  const expiredDocuments = computed(() => {
    const now = new Date()
    return documents.value.filter(doc => {
      if (!doc.expiry_date) return false
      return new Date(doc.expiry_date) < now
    })
  })
  
  const documentsByCategory = computed(() => {
    const grouped: Record<string, Document[]> = {}
    
    documents.value.forEach(doc => {
      if (!grouped[doc.category]) {
        grouped[doc.category] = []
      }
      grouped[doc.category].push(doc)
    })
    
    return grouped
  })
  
  // Actions - Student Records
  const fetchStudentRecords = async (params?: {
    student?: string
    academic_year?: string
    search?: string
    status?: string
    limit?: number
    offset?: number
  }) => {
    loading.value.studentRecords = true
    error.value = null
    
    try {
      const response = await studentRecordsApi.getStudentRecords(params)
      
      if (params?.offset && params.offset > 0) {
        studentRecords.value.push(...response.results)
      } else {
        studentRecords.value = response.results
      }
      
      studentRecordsPagination.value = {
        count: response.count,
        next: response.next,
        previous: response.previous,
        current_page: Math.floor((params?.offset || 0) / (params?.limit || 20)) + 1
      }
      
    } catch (err) {
      error.value = 'Erreur lors du chargement des dossiers élèves'
      console.error('Fetch student records error:', err)
    } finally {
      loading.value.studentRecords = false
    }
  }
  
  const fetchStudentRecord = async (id: string) => {
    try {
      const studentRecord = await studentRecordsApi.getStudentRecord(id)
      currentStudentRecord.value = studentRecord
      
      // Mettre à jour dans la liste aussi
      const index = studentRecords.value.findIndex(sr => sr.id === id)
      if (index !== -1) {
        studentRecords.value[index] = studentRecord
      }
      
      return studentRecord
    } catch (err) {
      error.value = 'Erreur lors du chargement du dossier élève'
      console.error('Fetch student record error:', err)
      throw err
    }
  }
  
  const createStudentRecord = async (data: {
    student: string
    academic_year: string
    class_group: string
    enrollment_date: string
    status?: 'active' | 'inactive' | 'transferred' | 'graduated'
    notes?: string
  }) => {
    loading.value.studentRecords = true
    error.value = null
    
    try {
      const newStudentRecord = await studentRecordsApi.createStudentRecord(data)
      studentRecords.value.unshift(newStudentRecord)
      return newStudentRecord
    } catch (err) {
      error.value = 'Erreur lors de la création du dossier élève'
      console.error('Create student record error:', err)
      throw err
    } finally {
      loading.value.studentRecords = false
    }
  }
  
  const updateStudentRecord = async (id: string, data: Partial<StudentRecord>) => {
    try {
      const updatedStudentRecord = await studentRecordsApi.updateStudentRecord(id, data)
      
      const index = studentRecords.value.findIndex(sr => sr.id === id)
      if (index !== -1) {
        studentRecords.value[index] = updatedStudentRecord
      }
      
      if (currentStudentRecord.value?.id === id) {
        currentStudentRecord.value = updatedStudentRecord
      }
      
      return updatedStudentRecord
    } catch (err) {
      error.value = 'Erreur lors de la modification du dossier élève'
      console.error('Update student record error:', err)
      throw err
    }
  }
  
  const deleteStudentRecord = async (id: string) => {
    try {
      await studentRecordsApi.deleteStudentRecord(id)
      studentRecords.value = studentRecords.value.filter(sr => sr.id !== id)
      
      if (currentStudentRecord.value?.id === id) {
        currentStudentRecord.value = null
      }
    } catch (err) {
      error.value = 'Erreur lors de la suppression du dossier élève'
      console.error('Delete student record error:', err)
      throw err
    }
  }
  
  const transferStudent = async (id: string, data: {
    new_class: string
    transfer_date: string
    reason: string
    notes?: string
  }) => {
    try {
      const updatedRecord = await studentRecordsApi.transferStudent(id, data)
      
      const index = studentRecords.value.findIndex(sr => sr.id === id)
      if (index !== -1) {
        studentRecords.value[index] = updatedRecord
      }
      
      if (currentStudentRecord.value?.id === id) {
        currentStudentRecord.value = updatedRecord
      }
      
      return updatedRecord
    } catch (err) {
      error.value = 'Erreur lors du transfert de l\'élève'
      console.error('Transfer student error:', err)
      throw err
    }
  }
  
  const graduateStudent = async (id: string, data: {
    graduation_date: string
    next_level?: string
    notes?: string
  }) => {
    try {
      const updatedRecord = await studentRecordsApi.graduateStudent(id, data)
      
      const index = studentRecords.value.findIndex(sr => sr.id === id)
      if (index !== -1) {
        studentRecords.value[index] = updatedRecord
      }
      
      if (currentStudentRecord.value?.id === id) {
        currentStudentRecord.value = updatedRecord
      }
      
      return updatedRecord
    } catch (err) {
      error.value = 'Erreur lors de la graduation de l\'élève'
      console.error('Graduate student error:', err)
      throw err
    }
  }
  
  const fetchStudentHistory = async (studentId: string) => {
    try {
      const history = await studentRecordsApi.getStudentHistory(studentId)
      transferHistory.value = history
      return history
    } catch (err) {
      error.value = 'Erreur lors du chargement de l\'historique'
      console.error('Fetch student history error:', err)
      throw err
    }
  }
  
  // Actions - Documents
  const fetchDocuments = async (params?: {
    student_record?: string
    category?: string
    document_type?: string
    is_required?: boolean
    status?: 'pending' | 'approved' | 'rejected' | 'expired'
    search?: string
    limit?: number
    offset?: number
  }) => {
    loading.value.documents = true
    error.value = null
    
    try {
      const response = await studentRecordsApi.getDocuments(params)
      
      if (params?.offset && params.offset > 0) {
        documents.value.push(...response.results)
      } else {
        documents.value = response.results
      }
      
      documentsPagination.value = {
        count: response.count,
        next: response.next,
        previous: response.previous,
        current_page: Math.floor((params?.offset || 0) / (params?.limit || 20)) + 1
      }
      
    } catch (err) {
      error.value = 'Erreur lors du chargement des documents'
      console.error('Fetch documents error:', err)
    } finally {
      loading.value.documents = false
    }
  }
  
  const uploadDocument = async (data: {
    student_record: string
    category: string
    document_type: string
    title: string
    file: File
    description?: string
    expiry_date?: string
    is_required?: boolean
  }) => {
    loading.value.upload = true
    error.value = null
    
    try {
      const newDocument = await studentRecordsApi.uploadDocument(data)
      documents.value.unshift(newDocument)
      
      // Mettre à jour le dossier élève si c'est le dossier actuel
      if (currentStudentRecord.value?.id === data.student_record) {
        currentStudentRecord.value.documents.unshift(newDocument)
      }
      
      return newDocument
    } catch (err) {
      error.value = 'Erreur lors du téléchargement du document'
      console.error('Upload document error:', err)
      throw err
    } finally {
      loading.value.upload = false
    }
  }
  
  const updateDocument = async (id: string, data: Partial<Document>) => {
    try {
      const updatedDocument = await studentRecordsApi.updateDocument(id, data)
      
      const index = documents.value.findIndex(doc => doc.id === id)
      if (index !== -1) {
        documents.value[index] = updatedDocument
      }
      
      // Mettre à jour dans le dossier élève si nécessaire
      if (currentStudentRecord.value) {
        const docIndex = currentStudentRecord.value.documents.findIndex(doc => doc.id === id)
        if (docIndex !== -1) {
          currentStudentRecord.value.documents[docIndex] = updatedDocument
        }
      }
      
      return updatedDocument
    } catch (err) {
      error.value = 'Erreur lors de la modification du document'
      console.error('Update document error:', err)
      throw err
    }
  }
  
  const deleteDocument = async (id: string) => {
    try {
      await studentRecordsApi.deleteDocument(id)
      documents.value = documents.value.filter(doc => doc.id !== id)
      
      // Mettre à jour dans le dossier élève si nécessaire
      if (currentStudentRecord.value) {
        currentStudentRecord.value.documents = currentStudentRecord.value.documents.filter(doc => doc.id !== id)
      }
    } catch (err) {
      error.value = 'Erreur lors de la suppression du document'
      console.error('Delete document error:', err)
      throw err
    }
  }
  
  const downloadDocument = async (id: string, filename?: string) => {
    try {
      const blob = await studentRecordsApi.downloadDocument(id)
      
      // Créer un lien de téléchargement
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || `document-${id}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors du téléchargement du document'
      console.error('Download document error:', err)
      throw err
    }
  }
  
  const approveDocument = async (id: string, notes?: string) => {
    try {
      const approvedDocument = await studentRecordsApi.approveDocument(id, { notes })
      
      const index = documents.value.findIndex(doc => doc.id === id)
      if (index !== -1) {
        documents.value[index] = approvedDocument
      }
      
      return approvedDocument
    } catch (err) {
      error.value = 'Erreur lors de l\'approbation du document'
      console.error('Approve document error:', err)
      throw err
    }
  }
  
  const rejectDocument = async (id: string, reason: string, notes?: string) => {
    try {
      const rejectedDocument = await studentRecordsApi.rejectDocument(id, { reason, notes })
      
      const index = documents.value.findIndex(doc => doc.id === id)
      if (index !== -1) {
        documents.value[index] = rejectedDocument
      }
      
      return rejectedDocument
    } catch (err) {
      error.value = 'Erreur lors du rejet du document'
      console.error('Reject document error:', err)
      throw err
    }
  }
  
  const requestDocument = async (studentRecordId: string, data: {
    category: string
    document_type: string
    title: string
    description?: string
    due_date?: string
  }) => {
    try {
      const requestedDocument = await studentRecordsApi.requestDocument(studentRecordId, data)
      documents.value.unshift(requestedDocument)
      return requestedDocument
    } catch (err) {
      error.value = 'Erreur lors de la demande de document'
      console.error('Request document error:', err)
      throw err
    }
  }
  
  // Actions - Categories & Types
  const fetchDocumentCategories = async () => {
    loading.value.categories = true
    error.value = null
    
    try {
      const categories = await studentRecordsApi.getDocumentCategories()
      documentCategories.value = categories
    } catch (err) {
      error.value = 'Erreur lors du chargement des catégories'
      console.error('Fetch document categories error:', err)
    } finally {
      loading.value.categories = false
    }
  }
  
  const fetchDocumentTypes = async (categoryId?: string) => {
    try {
      const types = await studentRecordsApi.getDocumentTypes(categoryId)
      documentTypes.value = types
      return types
    } catch (err) {
      error.value = 'Erreur lors du chargement des types de documents'
      console.error('Fetch document types error:', err)
      throw err
    }
  }
  
  // Actions - Bulk Operations
  const bulkUploadDocuments = async (files: {
    file: File
    student_record: string
    category: string
    document_type: string
    title: string
  }[]) => {
    loading.value.upload = true
    error.value = null
    
    try {
      const uploadedDocuments = await studentRecordsApi.bulkUploadDocuments(files)
      documents.value.unshift(...uploadedDocuments)
      return uploadedDocuments
    } catch (err) {
      error.value = 'Erreur lors du téléchargement en masse'
      console.error('Bulk upload documents error:', err)
      throw err
    } finally {
      loading.value.upload = false
    }
  }
  
  const bulkApproveDocuments = async (documentIds: string[], notes?: string) => {
    try {
      const approvedDocuments = await studentRecordsApi.bulkApproveDocuments(documentIds, notes)
      
      // Mettre à jour les documents dans la liste
      approvedDocuments.forEach(updatedDoc => {
        const index = documents.value.findIndex(doc => doc.id === updatedDoc.id)
        if (index !== -1) {
          documents.value[index] = updatedDoc
        }
      })
      
      return approvedDocuments
    } catch (err) {
      error.value = 'Erreur lors de l\'approbation en masse'
      console.error('Bulk approve documents error:', err)
      throw err
    }
  }
  
  const bulkRejectDocuments = async (documentIds: string[], reason: string, notes?: string) => {
    try {
      const rejectedDocuments = await studentRecordsApi.bulkRejectDocuments(documentIds, reason, notes)
      
      // Mettre à jour les documents dans la liste
      rejectedDocuments.forEach(updatedDoc => {
        const index = documents.value.findIndex(doc => doc.id === updatedDoc.id)
        if (index !== -1) {
          documents.value[index] = updatedDoc
        }
      })
      
      return rejectedDocuments
    } catch (err) {
      error.value = 'Erreur lors du rejet en masse'
      console.error('Bulk reject documents error:', err)
      throw err
    }
  }
  
  // Actions - Reports & Statistics
  const generateStudentReport = async (studentRecordId: string, format: 'pdf' | 'docx' = 'pdf') => {
    try {
      const blob = await studentRecordsApi.generateStudentReport(studentRecordId, format)
      
      // Télécharger le rapport
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `rapport-eleve-${studentRecordId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors de la génération du rapport'
      console.error('Generate student report error:', err)
      throw err
    }
  }
  
  const generateClassReport = async (classId: string, format: 'pdf' | 'xlsx' = 'pdf') => {
    try {
      const blob = await studentRecordsApi.generateClassReport(classId, format)
      
      // Télécharger le rapport
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `rapport-classe-${classId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'Erreur lors de la génération du rapport de classe'
      console.error('Generate class report error:', err)
      throw err
    }
  }
  
  const getExpiringDocuments = async (days: number = 30) => {
    try {
      return await studentRecordsApi.getExpiringDocuments(days)
    } catch (err) {
      error.value = 'Erreur lors du chargement des documents qui expirent'
      console.error('Get expiring documents error:', err)
      throw err
    }
  }
  
  const getMissingDocuments = async (studentRecordId?: string) => {
    try {
      return await studentRecordsApi.getMissingDocuments(studentRecordId)
    } catch (err) {
      error.value = 'Erreur lors du chargement des documents manquants'
      console.error('Get missing documents error:', err)
      throw err
    }
  }
  
  // Actions - Utilitaires
  const clearCurrentStudentRecord = () => {
    currentStudentRecord.value = null
  }
  
  const clearDocuments = () => {
    documents.value = []
    documentsPagination.value = {
      count: 0,
      next: null,
      previous: null,
      current_page: 1
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  // Utilitaires
  const getStudentRecordById = (id: string) => {
    return studentRecords.value.find(sr => sr.id === id)
  }
  
  const getDocumentById = (id: string) => {
    return documents.value.find(doc => doc.id === id)
  }
  
  const getDocumentsByStudentRecord = (studentRecordId: string) => {
    return documents.value.filter(doc => doc.student_record === studentRecordId)
  }
  
  const getCategoryById = (id: string) => {
    return documentCategories.value.find(cat => cat.id === id)
  }
  
  const getDocumentStatusColor = (status: string) => {
    const colors = {
      pending: 'warning',
      approved: 'success',
      rejected: 'danger',
      expired: 'danger'
    }
    return colors[status as keyof typeof colors] || 'default'
  }
  
  const getDocumentStatusLabel = (status: string) => {
    const labels = {
      pending: 'En attente',
      approved: 'Approuvé',
      rejected: 'Rejeté',
      expired: 'Expiré'
    }
    return labels[status as keyof typeof labels] || status
  }
  
  return {
    // État
    studentRecords,
    currentStudentRecord,
    documents,
    documentCategories,
    documentTypes,
    transferHistory,
    loading,
    error,
    studentRecordsPagination,
    documentsPagination,
    
    // Computed
    activeStudentRecords,
    documentsByStatus,
    requiredDocuments,
    expiredDocuments,
    documentsByCategory,
    
    // Actions - Student Records
    fetchStudentRecords,
    fetchStudentRecord,
    createStudentRecord,
    updateStudentRecord,
    deleteStudentRecord,
    transferStudent,
    graduateStudent,
    fetchStudentHistory,
    
    // Actions - Documents
    fetchDocuments,
    uploadDocument,
    updateDocument,
    deleteDocument,
    downloadDocument,
    approveDocument,
    rejectDocument,
    requestDocument,
    
    // Actions - Categories & Types
    fetchDocumentCategories,
    fetchDocumentTypes,
    
    // Actions - Bulk Operations
    bulkUploadDocuments,
    bulkApproveDocuments,
    bulkRejectDocuments,
    
    // Actions - Reports & Statistics
    generateStudentReport,
    generateClassReport,
    getExpiringDocuments,
    getMissingDocuments,
    
    // Actions - Utilitaires
    clearCurrentStudentRecord,
    clearDocuments,
    clearError,
    
    // Utilitaires
    getStudentRecordById,
    getDocumentById,
    getDocumentsByStudentRecord,
    getCategoryById,
    getDocumentStatusColor,
    getDocumentStatusLabel
  }
})