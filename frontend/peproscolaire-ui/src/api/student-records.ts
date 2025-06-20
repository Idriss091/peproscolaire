import { apiClient } from './client'
import type { 
  StudentRecord,
  Document,
  DocumentCategory,
  APIResponse,
  PaginatedResponse 
} from '@/types'

export const studentRecordsApi = {
  // Student Records
  async getStudentRecords(params?: {
    student?: string
    academic_year?: string
    search?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<StudentRecord>> {
    const response = await apiClient.get('/student-records/', { params })
    return response.data
  },

  async getStudentRecord(id: string): Promise<StudentRecord> {
    const response = await apiClient.get(`/student-records/${id}/`)
    return response.data
  },

  async createStudentRecord(data: {
    student: string
    academic_year: string
    class_group: string
    enrollment_date: string
    status?: 'active' | 'inactive' | 'transferred' | 'graduated'
    notes?: string
  }): Promise<StudentRecord> {
    const response = await apiClient.post('/student-records/', data)
    return response.data
  },

  async updateStudentRecord(id: string, data: Partial<StudentRecord>): Promise<StudentRecord> {
    const response = await apiClient.patch(`/student-records/${id}/`, data)
    return response.data
  },

  async deleteStudentRecord(id: string): Promise<void> {
    await apiClient.delete(`/student-records/${id}/`)
  },

  async transferStudent(id: string, data: {
    new_class: string
    transfer_date: string
    reason: string
    notes?: string
  }): Promise<StudentRecord> {
    const response = await apiClient.post(`/student-records/${id}/transfer/`, data)
    return response.data
  },

  async graduateStudent(id: string, data: {
    graduation_date: string
    next_level?: string
    notes?: string
  }): Promise<StudentRecord> {
    const response = await apiClient.post(`/student-records/${id}/graduate/`, data)
    return response.data
  },

  async getStudentHistory(studentId: string): Promise<StudentRecord[]> {
    const response = await apiClient.get(`/student-records/history/`, {
      params: { student: studentId }
    })
    return response.data
  },

  // Documents
  async getDocuments(params?: {
    student_record?: string
    category?: string
    document_type?: string
    is_required?: boolean
    status?: 'pending' | 'approved' | 'rejected' | 'expired'
    search?: string
    limit?: number
    offset?: number
  }): Promise<PaginatedResponse<Document>> {
    const response = await apiClient.get('/student-records/documents/', { params })
    return response.data
  },

  async getDocument(id: string): Promise<Document> {
    const response = await apiClient.get(`/student-records/documents/${id}/`)
    return response.data
  },

  async uploadDocument(data: {
    student_record: string
    category: string
    document_type: string
    title: string
    file: File
    description?: string
    expiry_date?: string
    is_required?: boolean
  }): Promise<Document> {
    const formData = new FormData()
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        if (key === 'file') {
          formData.append(key, value as File)
        } else {
          formData.append(key, value.toString())
        }
      }
    })

    const response = await apiClient.post('/student-records/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateDocument(id: string, data: Partial<Document>): Promise<Document> {
    const response = await apiClient.patch(`/student-records/documents/${id}/`, data)
    return response.data
  },

  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/student-records/documents/${id}/`)
  },

  async downloadDocument(id: string): Promise<Blob> {
    const response = await apiClient.get(`/student-records/documents/${id}/download/`, {
      responseType: 'blob'
    })
    return response.data
  },

  async approveDocument(id: string, data?: {
    notes?: string
  }): Promise<Document> {
    const response = await apiClient.post(`/student-records/documents/${id}/approve/`, data)
    return response.data
  },

  async rejectDocument(id: string, data: {
    reason: string
    notes?: string
  }): Promise<Document> {
    const response = await apiClient.post(`/student-records/documents/${id}/reject/`, data)
    return response.data
  },

  async requestDocument(studentRecordId: string, data: {
    category: string
    document_type: string
    title: string
    description?: string
    due_date?: string
  }): Promise<Document> {
    const response = await apiClient.post(`/student-records/${studentRecordId}/request-document/`, data)
    return response.data
  },

  // Document Categories
  async getDocumentCategories(): Promise<DocumentCategory[]> {
    const response = await apiClient.get('/student-records/document-categories/')
    return response.data
  },

  async getDocumentTypes(categoryId?: string): Promise<{
    id: string
    name: string
    description?: string
    is_required: boolean
    category: string
  }[]> {
    const params = categoryId ? { category: categoryId } : {}
    const response = await apiClient.get('/student-records/document-types/', { params })
    return response.data
  },

  // Bulk Operations
  async bulkUploadDocuments(files: {
    file: File
    student_record: string
    category: string
    document_type: string
    title: string
  }[]): Promise<Document[]> {
    const formData = new FormData()
    
    files.forEach((fileData, index) => {
      Object.entries(fileData).forEach(([key, value]) => {
        if (key === 'file') {
          formData.append(`files[${index}][${key}]`, value as File)
        } else {
          formData.append(`files[${index}][${key}]`, value.toString())
        }
      })
    })

    const response = await apiClient.post('/student-records/documents/bulk-upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async bulkApproveDocuments(documentIds: string[], notes?: string): Promise<Document[]> {
    const response = await apiClient.post('/student-records/documents/bulk-approve/', {
      document_ids: documentIds,
      notes
    })
    return response.data
  },

  async bulkRejectDocuments(documentIds: string[], reason: string, notes?: string): Promise<Document[]> {
    const response = await apiClient.post('/student-records/documents/bulk-reject/', {
      document_ids: documentIds,
      reason,
      notes
    })
    return response.data
  },

  // Statistics
  async getStudentRecordsStats(params?: {
    academic_year?: string
    class_group?: string
  }): Promise<{
    total_students: number
    active_students: number
    transferred_students: number
    graduated_students: number
    total_documents: number
    pending_documents: number
    expired_documents: number
    completion_rate: number
  }> {
    const response = await apiClient.get('/student-records/stats/', { params })
    return response.data
  },

  async getDocumentStats(params?: {
    student_record?: string
    category?: string
  }): Promise<{
    total_documents: number
    approved_documents: number
    pending_documents: number
    rejected_documents: number
    expired_documents: number
    missing_required: number
  }> {
    const response = await apiClient.get('/student-records/document-stats/', { params })
    return response.data
  },

  // Reports
  async generateStudentReport(studentRecordId: string, format: 'pdf' | 'docx' = 'pdf'): Promise<Blob> {
    const response = await apiClient.get(`/student-records/${studentRecordId}/report/`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  },

  async generateClassReport(classId: string, format: 'pdf' | 'xlsx' = 'pdf'): Promise<Blob> {
    const response = await apiClient.get('/student-records/class-report/', {
      params: { class_group: classId, format },
      responseType: 'blob'
    })
    return response.data
  },

  async exportDocuments(params?: {
    student_record?: string
    category?: string
    format?: 'zip' | 'pdf'
  }): Promise<Blob> {
    const response = await apiClient.get('/student-records/documents/export/', {
      params,
      responseType: 'blob'
    })
    return response.data
  },

  // Notifications
  async getExpiringDocuments(days: number = 30): Promise<Document[]> {
    const response = await apiClient.get('/student-records/documents/expiring/', {
      params: { days }
    })
    return response.data
  },

  async getMissingDocuments(studentRecordId?: string): Promise<{
    student_record: string
    student_name: string
    missing_documents: {
      category: string
      document_type: string
      title: string
      is_required: boolean
    }[]
  }[]> {
    const params = studentRecordId ? { student_record: studentRecordId } : {}
    const response = await apiClient.get('/student-records/missing-documents/', { params })
    return response.data
  }
}