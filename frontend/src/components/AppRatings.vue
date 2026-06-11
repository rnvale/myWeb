<template>
  <div class="app-ratings">
    <div ref="chartRef" style="width: 100%; height: 450px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

interface AppRating {
  app: string
  avg_rating: number
  total: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

// 完整的中文映射
const appNameMap: Record<string, string> = {
  'notability': '笔记大师',
  'evernote': '印象笔记',
  'evernote-notes-organizer': '印象笔记',
  'things-3': '事情3',
  'todoist': '任务大师',
  'microsoft-to-do': '微软待办',
  'microsoft-word': '微软 Word',
  'gmail': '谷歌邮箱',
  'gmail-email-by-google': '谷歌邮箱',
  'discord': '迪斯科',
  'whatsapp': 'WhatsApp',
  'whatsapp-messenger': 'WhatsApp',
  'monopoly': '大富翁',
  'among-us': '我们之中',
  'among-us-': '我们之中',
  'homescapes': '梦幻家园',
  'free-tone-calling-texting': '免费通话',
  'google-keep': '谷歌Keep',
  'onenote': 'OneNote',
  'bear': '小熊笔记',
  'notion': 'Notion'
}

const getChineseAppName = (appName: string): string => {
  if (!appName) return '未知'
  if (appNameMap[appName]) return appNameMap[appName]
  const firstWord = appName.split('-')[0]
  if (firstWord && appNameMap[firstWord]) return appNameMap[firstWord]
  if (appName.length > 12) return appName.slice(0, 10) + '..'
  return appName
}

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    // 调用筛选后的接口
    const res = await http.post('/filtered_app_ratings', filters)
    const data = res.data as AppRating[]
    if (data && data.length > 0) {
      drawChart(data, filters)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: AppRating[], filters: any) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const top12 = data.slice(0, 12)
  const appNames = top12.map(item => getChineseAppName(item.app))
  const ratings = top12.map(item => item.avg_rating)
  
  // 生成副标题
  let subtitle = ''
  if (filters.sentiment === 'positive') subtitle = '（仅正面评论）'
  else if (filters.sentiment === 'negative') subtitle = '（仅负面评论）'
  else subtitle = '（全部评论）'
  
  const getBarColor = (rating: number) => {
    if (rating >= 4.5) return '#52c41a'
    if (rating >= 4.0) return '#1890ff'
    if (rating >= 3.5) return '#faad14'
    return '#ff4d4f'
  }
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: `⭐ App 评分排行榜 ${subtitle}`,
      subtext: '绿色优秀 | 蓝色良好 | 黄色中等 | 红色待改进',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const item = top12[idx]
        if (!item) return ''
        return `<strong>${appNames[idx]}</strong><br/>⭐ 评分: ${item.avg_rating} 星<br/>📝 评论: ${item.total} 条`
      }
    },
    grid: { 
      left: '15%', 
      right: '8%', 
      top: '15%', 
      bottom: '8%', 
      containLabel: true 
    },
    xAxis: { 
      type: 'value', 
      name: '平均评分（星）', 
      min: 1, 
      max: 5, 
      axisLabel: { formatter: '{value}星' },
      splitLine: { lineStyle: { color: '#ddd', type: 'dashed' } }
    },
    yAxis: { 
      type: 'category', 
      data: appNames, 
      name: '应用名称',
      nameLocation: 'middle',
      nameGap: 55,
      axisLabel: { fontSize: 11, fontWeight: 'bold' },
      axisLine: { show: false }
    },
    series: [{
      name: '平均评分',
      type: 'bar',
      data: ratings,
      itemStyle: { 
        color: (params: any) => getBarColor(params.data), 
        borderRadius: [0, 8, 8, 0] 
      },
      label: { 
        show: true, 
        position: 'right', 
        formatter: '{c}星', 
        fontWeight: 'bold',
        fontSize: 11
      },
      barWidth: '50%'
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
.app-ratings { width: 100%; min-height: 450px; }
.loading { text-align: center; padding: 50px; color: #999; }
</style>