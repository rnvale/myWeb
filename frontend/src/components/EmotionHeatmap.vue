<template>
  <div class="emotion-heatmap">
    <div ref="chartRef" style="width: 100%; height: 480px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'
import { categoryMap } from '../utils/chineseMap'

interface HeatmapData {
  rating: number
  category: string
  positive_rate: number
  total: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    // 调用筛选后的接口
    const res = await http.post('/filtered_emotion_heatmap', filters)
    const data = res.data as HeatmapData[]
    if (data && data.length > 0) {
      drawChart(data, filters)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: HeatmapData[], filters: any) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const ratings = [1, 2, 3, 4, 5]
  const categories = [...new Set(data.map(d => d.category))]
  const categoriesCn = categories.map(c => categoryMap[c] || c)
  
  const heatData: [number, number, number][] = []
  data.forEach(item => {
    const xIdx = ratings.indexOf(item.rating)
    const yIdx = categories.indexOf(item.category)
    if (xIdx !== -1 && yIdx !== -1) {
      heatData.push([xIdx, yIdx, item.positive_rate])
    }
  })
  
  // 生成副标题
  let subtitle = ''
  if (filters.sentiment === 'positive') subtitle = '（仅正面评论）'
  else if (filters.sentiment === 'negative') subtitle = '（仅负面评论）'
  else subtitle = '（全部评论）'
  if (filters.category && filters.category !== 'all') {
    const catCn = categoryMap[filters.category] || filters.category
    subtitle += ` | 方面: ${catCn}`
  }
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: `🔥 评分-方面情感热力图 ${subtitle}`,
      subtext: '颜色越绿 = 正面率越高',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const rating = ratings[params.value[0]]
        const category = categoriesCn[params.value[1]]
        const rate = params.value[2]
        return `<strong>${category}</strong><br/>评分: ${rating}星<br/>正面率: ${rate}%`
      }
    },
    xAxis: { 
      type: 'category', 
      data: ['1星', '2星', '3星', '4星', '5星'], 
      name: '用户评分',
      nameLocation: 'middle',
      nameGap: 38
    },
    yAxis: { 
      type: 'category', 
      data: categoriesCn, 
      name: '方面类别',
      nameLocation: 'middle',
      nameGap: 55,
      axisLabel: { fontSize: 10 }
    },
    visualMap: {
      min: 0, max: 100, calculable: true, orient: 'vertical', left: 'right', top: 'center',
      inRange: { color: ['#ff4d4f', '#faad14', '#52c41a'] },
      formatter: (value: number) => `${value}%`
    },
    series: [{
      type: 'heatmap',
      data: heatData,
      label: { show: true, formatter: (params: any) => `${params.data[2]}%`, fontSize: 10 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
      itemStyle: { borderRadius: 4, borderWidth: 1, borderColor: '#fff' }
    }]
  }
  
  chart.setOption(option)
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
.emotion-heatmap { width: 100%; min-height: 480px; }
.loading { text-align: center; padding: 50px; color: #999; }
</style>