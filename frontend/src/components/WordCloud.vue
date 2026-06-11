<template>
  <div class="word-cloud">
    <div class="cloud-tabs">
      <button 
        :class="{ active: activeTab === 'positive' }" 
        @click="activeTab = 'positive'; drawCurrentCloud()">
        👍 正面评论词云
      </button>
      <button 
        :class="{ active: activeTab === 'negative' }" 
        @click="activeTab = 'negative'; drawCurrentCloud()">
        👎 负面评论词云
      </button>
    </div>
    <div ref="chartRef" style="width: 100%; height: 450px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import http from '../http'
import emitter from '../utils/eventBus'
import { categoryMap } from '../utils/chineseMap'

interface WordData {
  name: string
  value: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
const activeTab = ref('positive')
let chartInstance: any = null
let positiveWords: WordData[] = []
let negativeWords: WordData[] = []

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/filtered_wordcloud', filters)
    positiveWords = res.data.positive || []
    negativeWords = res.data.negative || []
    drawCurrentCloud()
  } catch (error) {
    console.error('获取词云数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawCurrentCloud = () => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const words = activeTab.value === 'positive' ? positiveWords : negativeWords
  
  if (!words || words.length === 0) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center' }
    })
    return
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: activeTab.value === 'positive' ? '👍 正面评论高频词云' : '👎 负面评论高频词云',
      subtext: '字体越大 = 出现频率越高',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `<strong>${params.name}</strong><br/>出现次数: ${params.value} 次`
      },
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: '#333',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: { color: '#fff', fontSize: 12 }
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      width: '100%',
      height: '90%',
      gridSize: 12,
      sizeRange: [14, 54],
      rotationRange: [-45, 45],
      rotationStep: 15,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: 'Inter, sans-serif',
        fontWeight: 'bold',
        color: (params: any) => {
          const colors = activeTab.value === 'positive' 
            ? ['#52c41a', '#73d13d', '#95de64', '#b7eb8f', '#d9f5be']
            : ['#ff4d4f', '#ff7875', '#ffa39e', '#ffccc7', '#fff1f0']
          return colors[params.dataIndex % colors.length]
        }
      },
      emphasis: {
        focus: 'self',
        textStyle: { shadowBlur: 10, shadowColor: '#333' }
      },
      data: words.slice(0, 60)
    }]
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
.word-cloud { 
  width: 100%; 
  min-height: 500px;
  background: #fff;
  border-radius: 16px;
}
.cloud-tabs {
  display: flex;
  gap: 12px;
  padding: 16px 20px 0;
  border-bottom: 1px solid #e8edf2;
}
.cloud-tabs button {
  padding: 8px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  border-radius: 20px;
  transition: all 0.2s;
}
.cloud-tabs button:hover {
  background: #f0f2f5;
}
.cloud-tabs button.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
}
.loading { text-align: center; padding: 50px; color: #999; }
</style>