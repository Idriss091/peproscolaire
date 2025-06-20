<template>
  <div class="w-full h-full">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale)

interface Props {
  data: Record<string, number>
}

const props = defineProps<Props>()

const chartRef = ref<HTMLCanvasElement>()
let chartInstance: ChartJS | null = null

const colors = {
  very_low: '#10B981', // green-500
  low: '#84CC16',     // lime-500
  moderate: '#F59E0B', // amber-500
  high: '#EF4444',    // red-500
  critical: '#DC2626'  // red-600
}

const labels = {
  very_low: 'Très faible',
  low: 'Faible',
  moderate: 'Modéré',
  high: 'Élevé',
  critical: 'Critique'
}

const createChart = () => {
  if (!chartRef.value || !props.data) return

  const chartData = {
    labels: Object.keys(props.data).map(key => labels[key] || key),
    datasets: [{
      data: Object.values(props.data),
      backgroundColor: Object.keys(props.data).map(key => colors[key] || '#6B7280'),
      borderWidth: 2,
      borderColor: '#fff'
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = Math.round((context.parsed / total) * 100)
            return `${context.label}: ${context.parsed} (${percentage}%)`
          }
        }
      }
    },
    cutout: '60%'
  }

  chartInstance = new ChartJS(chartRef.value, {
    type: 'doughnut',
    data: chartData,
    options
  })
}

const updateChart = () => {
  if (!chartInstance || !props.data) return

  chartInstance.data.labels = Object.keys(props.data).map(key => labels[key] || key)
  chartInstance.data.datasets[0].data = Object.values(props.data)
  chartInstance.data.datasets[0].backgroundColor = Object.keys(props.data).map(key => colors[key] || '#6B7280')
  chartInstance.update()
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>