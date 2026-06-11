<template>
  <div class="sentiment-gauge">
    <div ref="chartRef" style="width: 100%; height: 420px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/filtered_summary', filters)
    const data = res.data.sentiment
    
    const positive = data.positive || 0
    const negative = data.negative || 0
    const total = positive + negative
    const positiveRate = (positive / total * 100).toFixed(1)
    const negativeRate = (negative / total * 100).toFixed(1)
    
    drawChart(positiveRate, negativeRate)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (positiveRate: string, negativeRate: string) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '🎯 整体情感倾向仪表盘',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.seriesName === '情感比例') {
          return `${params.name}: ${params.value}%`
        }
        return `${params.name}: ${params.value}`
      }
    },
    series: [
      {
        name: '情感仪表',
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '60%',
        min: 0,
        max: 100,
        startAngle: 210,
        endAngle: -30,
        splitNumber: 5,
        progress: {
          show: true,
          width: 14,
          roundCap: true,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: '#ff4d4f' },
                { offset: 0.5, color: '#faad14' },
                { offset: 1, color: '#52c41a' }
              ]
            }
          }
        },
        axisLine: { lineStyle: { width: 14, color: [[1, '#e8e8e8']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        detail: {
          show: true,
          offsetCenter: [0, 20],
          valueAnimation: true,
          fontSize: 26,
          fontWeight: 'bold',
          color: '#333',
          formatter: (value: number) => `${value.toFixed(1)}%`
        },
        title: {
          show: true,
          offsetCenter: [0, -25],
          fontSize: 12,
          color: '#666'
        },
        data: [{ value: parseFloat(positiveRate), name: '正面率' }]
      },
      {
        name: '情感比例',
        type: 'pie',
        center: ['50%', '50%'],
        radius: ['38%', '48%'],
        avoidLabelOverlap: false,
        silent: true,
        label: { show: false },
        data: [
          { value: parseFloat(positiveRate), name: '正面', itemStyle: { color: '#52c41a' } },
          { value: parseFloat(negativeRate), name: '负面', itemStyle: { color: '#ff4d4f' } }
        ]
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: 72,
        style: {
          text: `正面 ${positiveRate}%  |  负面 ${negativeRate}%`,
          fill: '#666',
          fontSize: 12
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const handleFilterChange = (filters: any) => {
  fetchDataAndDraw(filters)
}

onMounted(() => {
  emitter.on('filter-change', handleFilterChange)
  fetchDataAndDraw({ sentiment: 'all', category: 'all' })
})

onUnmounted(() => {
  emitter.off('filter-change', handleFilterChange)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.sentiment-gauge { width: 100%; min-height: 420px; }
.loading { text-align: center; padding: 50px; color: #999; }
</style>