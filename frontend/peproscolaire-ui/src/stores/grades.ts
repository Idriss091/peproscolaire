/**
 * Store Pinia pour la gestion des notes et évaluations
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { gradesApi } from '@/api/grades'
import type {
  EvaluationType,
  Evaluation,
  Grade,
  SubjectAverage,
  Competence,
  CompetenceGrade,
  Bulletin,
  PaginatedResponse,
  FilterOptions
} from '@/types'

export const useGradesStore = defineStore('grades', () => {
  // État
  const evaluationTypes = ref<EvaluationType[]>([])
  const evaluations = ref<Evaluation[]>([])
  const grades = ref<Grade[]>([])
  const subjectAverages = ref<SubjectAverage[]>([])
  const competences = ref<Competence[]>([])
  const competenceGrades = ref<CompetenceGrade[]>([])
  const bulletins = ref<Bulletin[]>([])
  
  const currentEvaluation = ref<Evaluation | null>(null)
  const currentBulletin = ref<Bulletin | null>(null)
  
  // États de chargement
  const loading = ref({
    evaluationTypes: false,
    evaluations: false,
    grades: false,
    subjectAverages: false,
    competences: false,
    competenceGrades: false,
    bulletins: false,
    saving: false
  })

  // Erreurs
  const errors = ref<Record<string, string>>({})

  // Pagination
  const pagination = ref({
    evaluations: { count: 0, next: null, previous: null },
    grades: { count: 0, next: null, previous: null },
    subjectAverages: { count: 0, next: null, previous: null },
    competenceGrades: { count: 0, next: null, previous: null },
    bulletins: { count: 0, next: null, previous: null }
  })

  // Getters calculés
  const getEvaluationById = computed(() => {
    return (id: string) => evaluations.value.find(evaluation => evaluation.id === id)
  })

  const getGradesByEvaluation = computed(() => {
    return (evaluationId: string) => grades.value.filter(grade => grade.evaluation === evaluationId)
  })

  const getStudentAverages = computed(() => {
    return (studentId: string) => subjectAverages.value.filter(avg => avg.student === studentId)
  })

  const getActiveEvaluationTypes = computed(() => {
    return evaluationTypes.value.filter(type => type.is_active)
  })

  const getPublishedEvaluations = computed(() => {
    return evaluations.value.filter(evaluation => evaluation.is_published)
  })

  const overallStats = computed(() => {
    const total = grades.value.length
    const validGrades = grades.value.filter(grade => grade.value != null && grade.value !== undefined)
    const sum = validGrades.reduce((acc, grade) => acc + (grade.value || 0), 0)
    const average = validGrades.length > 0 ? (sum / validGrades.length).toFixed(1) : '0.0'
    const excellent = validGrades.filter(grade => (grade.value || 0) >= 16).length
    const struggling = validGrades.filter(grade => (grade.value || 0) < 10).length

    return {
      total,
      average,
      excellent,
      struggling
    }
  })

  // Actions - Types d'évaluation
  const fetchEvaluationTypes = async (params?: FilterOptions) => {
    loading.value.evaluationTypes = true
    errors.value.evaluationTypes = ''
    
    try {
      const response = await gradesApi.getEvaluationTypes(params)
      evaluationTypes.value = response
    } catch (error: any) {
      errors.value.evaluationTypes = error.message || 'Erreur lors du chargement des types d\'évaluation'
      throw error
    } finally {
      loading.value.evaluationTypes = false
    }
  }

  const createEvaluationType = async (data: Partial<EvaluationType>) => {
    loading.value.saving = true
    errors.value.creating = ''

    try {
      const newType = await gradesApi.createEvaluationType(data)
      evaluationTypes.value.push(newType)
      return newType
    } catch (error: any) {
      errors.value.creating = error.message || 'Erreur lors de la création du type d\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const updateEvaluationType = async (id: string, data: Partial<EvaluationType>) => {
    loading.value.saving = true
    errors.value.updating = ''

    try {
      const updatedType = await gradesApi.updateEvaluationType(id, data)
      const index = evaluationTypes.value.findIndex(type => type.id === id)
      if (index !== -1) {
        evaluationTypes.value[index] = updatedType
      }
      return updatedType
    } catch (error: any) {
      errors.value.updating = error.message || 'Erreur lors de la mise à jour du type d\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const deleteEvaluationType = async (id: string) => {
    loading.value.saving = true
    errors.value.deleting = ''

    try {
      await gradesApi.deleteEvaluationType(id)
      const index = evaluationTypes.value.findIndex(type => type.id === id)
      if (index !== -1) {
        evaluationTypes.value.splice(index, 1)
      }
    } catch (error: any) {
      errors.value.deleting = error.message || 'Erreur lors de la suppression du type d\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  // Actions - Évaluations
  const fetchEvaluations = async (params?: FilterOptions) => {
    loading.value.evaluations = true
    errors.value.evaluations = ''

    try {
      const response = await gradesApi.getEvaluations(params)
      evaluations.value = response.results
      pagination.value.evaluations = {
        count: response.count,
        next: response.next,
        previous: response.previous
      }
    } catch (error: any) {
      errors.value.evaluations = error.message || 'Erreur lors du chargement des évaluations'
      throw error
    } finally {
      loading.value.evaluations = false
    }
  }

  const fetchEvaluation = async (id: string) => {
    loading.value.evaluations = true
    errors.value.evaluation = ''

    try {
      const evaluation = await gradesApi.getEvaluation(id)
      currentEvaluation.value = evaluation
      
      // Mettre à jour dans la liste si elle existe
      const index = evaluations.value.findIndex(evaluation => evaluation.id === id)
      if (index !== -1) {
        evaluations.value[index] = evaluation
      } else {
        evaluations.value.push(evaluation)
      }
      
      return evaluation
    } catch (error: any) {
      errors.value.evaluation = error.message || 'Erreur lors du chargement de l\'évaluation'
      throw error
    } finally {
      loading.value.evaluations = false
    }
  }

  const createEvaluation = async (data: Partial<Evaluation>) => {
    loading.value.saving = true
    errors.value.creating = ''

    try {
      const newEvaluation = await gradesApi.createEvaluation(data)
      evaluations.value.unshift(newEvaluation)
      return newEvaluation
    } catch (error: any) {
      errors.value.creating = error.message || 'Erreur lors de la création de l\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const updateEvaluation = async (id: string, data: Partial<Evaluation>) => {
    loading.value.saving = true
    errors.value.updating = ''

    try {
      const updatedEvaluation = await gradesApi.updateEvaluation(id, data)
      const index = evaluations.value.findIndex(evaluation => evaluation.id === id)
      if (index !== -1) {
        evaluations.value[index] = updatedEvaluation
      }
      if (currentEvaluation.value?.id === id) {
        currentEvaluation.value = updatedEvaluation
      }
      return updatedEvaluation
    } catch (error: any) {
      errors.value.updating = error.message || 'Erreur lors de la mise à jour de l\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const deleteEvaluation = async (id: string) => {
    loading.value.saving = true
    errors.value.deleting = ''

    try {
      await gradesApi.deleteEvaluation(id)
      const index = evaluations.value.findIndex(evaluation => evaluation.id === id)
      if (index !== -1) {
        evaluations.value.splice(index, 1)
      }
      if (currentEvaluation.value?.id === id) {
        currentEvaluation.value = null
      }
    } catch (error: any) {
      errors.value.deleting = error.message || 'Erreur lors de la suppression de l\'évaluation'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  // Actions - Notes
  const fetchGrades = async (params?: FilterOptions) => {
    loading.value.grades = true
    errors.value.grades = ''

    try {
      const response = await gradesApi.getGrades(params)
      grades.value = response.results || []
      pagination.value.grades = {
        count: response.results?.length || 0,
        next: null,
        previous: null
      }
    } catch (error: any) {
      errors.value.grades = error.message || 'Erreur lors du chargement des notes'
      throw error
    } finally {
      loading.value.grades = false
    }
  }

  const fetchEvaluationGrades = async (evaluationId: string) => {
    loading.value.grades = true
    errors.value.grades = ''

    try {
      const evaluationGrades = await gradesApi.getEvaluationGrades(evaluationId)
      
      // Mettre à jour les notes pour cette évaluation
      grades.value = grades.value.filter(grade => grade.evaluation !== evaluationId)
      grades.value.push(...evaluationGrades)
      
      return evaluationGrades
    } catch (error: any) {
      errors.value.grades = error.message || 'Erreur lors du chargement des notes de l\'évaluation'
      throw error
    } finally {
      loading.value.grades = false
    }
  }

  const createGrade = async (data: Partial<Grade>) => {
    loading.value.saving = true
    errors.value.creating = ''

    try {
      const newGrade = await gradesApi.createGrade(data)
      grades.value.push(newGrade)
      return newGrade
    } catch (error: any) {
      errors.value.creating = error.message || 'Erreur lors de la création de la note'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const updateGrade = async (id: string, data: Partial<Grade>) => {
    loading.value.saving = true
    errors.value.updating = ''

    try {
      const updatedGrade = await gradesApi.updateGrade(id, data)
      const index = grades.value.findIndex(grade => grade.id === id)
      if (index !== -1) {
        grades.value[index] = updatedGrade
      }
      return updatedGrade
    } catch (error: any) {
      errors.value.updating = error.message || 'Erreur lors de la mise à jour de la note'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  const bulkUpdateGrades = async (evaluationId: string, gradeUpdates: Partial<Grade>[]) => {
    loading.value.saving = true
    errors.value.bulkUpdate = ''

    try {
      const updatedGrades = await gradesApi.bulkUpdateGrades(evaluationId, gradeUpdates)
      
      // Mettre à jour les notes dans le store
      updatedGrades.forEach(updatedGrade => {
        const index = grades.value.findIndex(grade => grade.id === updatedGrade.id)
        if (index !== -1) {
          grades.value[index] = updatedGrade
        } else {
          grades.value.push(updatedGrade)
        }
      })
      
      return updatedGrades
    } catch (error: any) {
      errors.value.bulkUpdate = error.message || 'Erreur lors de la mise à jour en lot des notes'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  // Actions - Moyennes
  const fetchSubjectAverages = async (params?: FilterOptions) => {
    loading.value.subjectAverages = true
    errors.value.subjectAverages = ''

    try {
      const response = await gradesApi.getSubjectAverages(params)
      subjectAverages.value = response.results
      pagination.value.subjectAverages = {
        count: response.count,
        next: response.next,
        previous: response.previous
      }
    } catch (error: any) {
      errors.value.subjectAverages = error.message || 'Erreur lors du chargement des moyennes'
      throw error
    } finally {
      loading.value.subjectAverages = false
    }
  }

  const fetchStudentAverages = async (studentId: string, period?: string) => {
    loading.value.subjectAverages = true
    errors.value.studentAverages = ''

    try {
      const studentAvgs = await gradesApi.getStudentAverages(studentId, period)
      
      // Mettre à jour les moyennes pour cet élève
      subjectAverages.value = subjectAverages.value.filter(avg => avg.student !== studentId)
      subjectAverages.value.push(...studentAvgs)
      
      return studentAvgs
    } catch (error: any) {
      errors.value.studentAverages = error.message || 'Erreur lors du chargement des moyennes de l\'élève'
      throw error
    } finally {
      loading.value.subjectAverages = false
    }
  }

  // Actions - Bulletins
  const fetchBulletins = async (params?: FilterOptions) => {
    loading.value.bulletins = true
    errors.value.bulletins = ''

    try {
      const response = await gradesApi.getBulletins(params)
      bulletins.value = response.results
      pagination.value.bulletins = {
        count: response.count,
        next: response.next,
        previous: response.previous
      }
    } catch (error: any) {
      errors.value.bulletins = error.message || 'Erreur lors du chargement des bulletins'
      throw error
    } finally {
      loading.value.bulletins = false
    }
  }

  const fetchBulletin = async (id: string) => {
    loading.value.bulletins = true
    errors.value.bulletin = ''

    try {
      const bulletin = await gradesApi.getBulletin(id)
      currentBulletin.value = bulletin
      
      // Mettre à jour dans la liste si elle existe
      const index = bulletins.value.findIndex(b => b.id === id)
      if (index !== -1) {
        bulletins.value[index] = bulletin
      } else {
        bulletins.value.push(bulletin)
      }
      
      return bulletin
    } catch (error: any) {
      errors.value.bulletin = error.message || 'Erreur lors du chargement du bulletin'
      throw error
    } finally {
      loading.value.bulletins = false
    }
  }

  const generateBulletin = async (studentId: string, period: string) => {
    loading.value.saving = true
    errors.value.generating = ''

    try {
      const bulletin = await gradesApi.generateBulletin(studentId, period)
      bulletins.value.unshift(bulletin)
      return bulletin
    } catch (error: any) {
      errors.value.generating = error.message || 'Erreur lors de la génération du bulletin'
      throw error
    } finally {
      loading.value.saving = false
    }
  }

  // Actions - Statistiques
  const fetchGradeStatistics = async (params?: FilterOptions) => {
    loading.value.statistics = true
    errors.value.statistics = ''

    try {
      return await gradesApi.getGradeStatistics(params)
    } catch (error: any) {
      errors.value.statistics = error.message || 'Erreur lors du chargement des statistiques'
      throw error
    } finally {
      loading.value.statistics = false
    }
  }

  const fetchClassPerformance = async (classId: string, subject?: string) => {
    loading.value.statistics = true
    errors.value.classPerformance = ''

    try {
      return await gradesApi.getClassPerformance(classId, subject)
    } catch (error: any) {
      errors.value.classPerformance = error.message || 'Erreur lors du chargement des performances de classe'
      throw error
    } finally {
      loading.value.statistics = false
    }
  }

  const fetchStudentProgress = async (studentId: string) => {
    loading.value.statistics = true
    errors.value.studentProgress = ''

    try {
      return await gradesApi.getStudentProgress(studentId)
    } catch (error: any) {
      errors.value.studentProgress = error.message || 'Erreur lors du chargement des progrès de l\'élève'
      throw error
    } finally {
      loading.value.statistics = false
    }
  }

  // Actions - Export et autres
  const exportGrades = async (options: { format: string; includeStats: boolean }) => {
    try {
      // Implementation placeholder - would call API to export grades
      const params = new URLSearchParams()
      params.append('format', options.format)
      if (options.includeStats) {
        params.append('include_stats', 'true')
      }
      
      // Mock export for now
      console.log('Exporting grades with options:', options)
      
      // In real implementation, this would call the API and download file
      // const response = await gradesApi.exportGrades(options)
      // return response
    } catch (error: any) {
      errors.value.export = error.message || 'Erreur lors de l\'export'
      throw error
    }
  }

  const fetchSubjects = async () => {
    // Placeholder for fetching subjects - would normally be in a separate store
    try {
      // Mock implementation
      return []
    } catch (error: any) {
      errors.value.subjects = error.message || 'Erreur lors du chargement des matières'
      throw error
    }
  }

  const fetchClasses = async () => {
    // Placeholder for fetching classes - would normally be in a separate store
    try {
      // Mock implementation
      return []
    } catch (error: any) {
      errors.value.classes = error.message || 'Erreur lors du chargement des classes'
      throw error
    }
  }

  // Actions utilitaires
  const clearErrors = () => {
    errors.value = {}
  }

  const resetCurrentEvaluation = () => {
    currentEvaluation.value = null
  }

  const resetCurrentBulletin = () => {
    currentBulletin.value = null
  }

  const clearStore = () => {
    evaluationTypes.value = []
    evaluations.value = []
    grades.value = []
    subjectAverages.value = []
    competences.value = []
    competenceGrades.value = []
    bulletins.value = []
    currentEvaluation.value = null
    currentBulletin.value = null
    clearErrors()
  }

  return {
    // État
    evaluationTypes,
    evaluations,
    grades,
    subjectAverages,
    competences,
    competenceGrades,
    bulletins,
    currentEvaluation,
    currentBulletin,
    loading,
    errors,
    pagination,

    // Getters
    getEvaluationById,
    getGradesByEvaluation,
    getStudentAverages,
    getActiveEvaluationTypes,
    getPublishedEvaluations,
    overallStats,

    // Actions - Types d'évaluation
    fetchEvaluationTypes,
    createEvaluationType,
    updateEvaluationType,
    deleteEvaluationType,

    // Actions - Évaluations
    fetchEvaluations,
    fetchEvaluation,
    createEvaluation,
    updateEvaluation,
    deleteEvaluation,

    // Actions - Notes
    fetchGrades,
    fetchEvaluationGrades,
    createGrade,
    updateGrade,
    bulkUpdateGrades,

    // Actions - Moyennes
    fetchSubjectAverages,
    fetchStudentAverages,

    // Actions - Bulletins
    fetchBulletins,
    fetchBulletin,
    generateBulletin,

    // Actions - Statistiques
    fetchGradeStatistics,
    fetchClassPerformance,
    fetchStudentProgress,

    // Actions - Export et autres
    exportGrades,
    fetchSubjects,
    fetchClasses,

    // Actions utilitaires
    clearErrors,
    resetCurrentEvaluation,
    resetCurrentBulletin,
    clearStore
  }
})