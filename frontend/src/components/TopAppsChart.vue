<template>
  <div class="top-apps-chart">
    <div ref="chartRef" style="width: 100%; height: 500px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

interface AppData {
  app: string
  positive: number
  negative: number
  total: number
  positive_rate: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const appNameMap: Record<string, string> = {
  'notability': '笔记大师',
  'evernote': '印象笔记',
  'evernote-notes-organizer': '印象笔记',
  'bear': '小熊笔记',
  'onenote': 'OneNote',
  'notion': 'Notion',
  'google-keep': '谷歌 Keep',
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
  'free-tone-calling-texting': '免费通话'
}

const getChineseAppName = (appName: string): string => {
  if (!appName) return '未知'
  if (appNameMap[appName]) return appNameMap[appName]
  const firstWord = appName.split('-')[0]
  if (firstWord && appNameMap[firstWord]) return appNameMap[firstWord]
  if (appName.length > 15) return appName.slice(0, 12) + '...'
  return appName
}

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/filtered_top_apps', filters)
    const data = res.data as AppData[]
    if (data && data.length > 0) {
      await nextTick()
      drawChart(data, filters)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: AppData[], filters: any) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const top8 = data.slice(0, 8)
  const appNames = top8.map(item => getChineseAppName(item.app))
  const positiveData = top8.map(item => item.positive)
  const negativeData = top8.map(item => item.negative)
  const positiveRates = top8.map(item => item.positive_rate)
  
  let subtitle = ''
  if (filters.sentiment === 'positive') subtitle = '（仅正面评论）'
  else if (filters.sentiment === 'negative') subtitle = '（仅负面评论）'
  else subtitle = '（全部评论）'
  if (filters.category && filters.category !== 'all') subtitle += ` | 类别: ${filters.category}`
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: `🏆 热门 App 情感河流图 ${subtitle}`,
      subtext: '绿色区域=正面评论 | 红色区域=负面评论 | 折线=正面率',
      left: 'center',
      top: 5,
      textStyle: { fontSize: 16, fontWeight: 'bold', color: '#2c3e50' },
      subtextStyle: { fontSize: 11, color: '#7f8c8d' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0,0,0,0.85)',
      borderColor: '#333',
      borderWidth: 1,
      borderRadius: 8,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const app = top8[idx]
        if (!app) return ''
        return `<strong style="color: #fff">${appNames[idx]}</strong><br/>
                <span style="color: #52c41a">👍 正面: ${app.positive} 条 (${app.positive_rate}%)</span><br/>
                <span style="color: #ff4d4f">👎 负面: ${app.negative} 条</span><br/>
                📊 总计: ${app.total} 条`
      }
    },
    legend: {
      data: ['正面评论', '负面评论', '正面率'],
      left: 'left',
      top: 35,
      itemWidth: 25,
      itemHeight: 12,
      textStyle: { fontSize: 12, fontWeight: 'bold' }
    },
    grid: {
      left: '12%',
      right: '8%',
      top: '18%',
      bottom: '10%',
      containLabel: true,
      backgroundColor: '#f5f7fa',
      borderWidth: 0,
      borderRadius: 8
    },
    xAxis: {
      type: 'category',
      data: appNames,
      name: 'App 名称',
      nameLocation: 'middle',
      nameGap: 45,
      nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
      axisLabel: { fontSize: 11, fontWeight: 'bold', color: '#2c3e50', rotate: 25, interval: 0 },
      axisLine: { lineStyle: { color: '#ccc', width: 1 } },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: '评论数量',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#555' },
        axisLabel: { fontSize: 11, color: '#666', formatter: '{value}条' },
        splitLine: { lineStyle: { color: '#ddd', type: 'dashed' } }
      },
      {
        type: 'value',
        name: '正面率',
        nameLocation: 'middle',
        nameGap: 45,
        nameTextStyle: { fontSize: 12, fontWeight: 'bold', color: '#faad14' },
        min: 0,
        max: 80,
        axisLabel: { fontSize: 11, color: '#faad14', formatter: '{value}%' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '正面评论',
        type: 'line',
        data: positiveData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#52c41a', width: 2, shadowBlur: 10 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(82, 196, 26, 0.5)' },
              { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
            ]
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}条',
          fontSize: 10,
          fontWeight: 'bold',
          color: '#52c41a',
          backgroundColor: 'rgba(255,255,255,0.7)',
          padding: [2, 6, 2, 6],
          borderRadius: 12
        }
      },
      {
        name: '负面评论',
        type: 'line',
        data: negativeData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#ff4d4f', width: 2, shadowBlur: 10 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 77, 79, 0.5)' },
              { offset: 1, color: 'rgba(255, 77, 79, 0.05)' }
            ]
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}条',
          fontSize: 10,
          fontWeight: 'bold',
          color: '#ff4d4f',
          backgroundColor: 'rgba(255,255,255,0.7)',
          padding: [2, 6, 2, 6],
          borderRadius: 12
        }
      },
      {
        name: '正面率',
        type: 'line',
        data: positiveRates,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 10,
        lineStyle: { color: '#faad14', width: 3, type: 'solid', shadowBlur: 8 },
        yAxisIndex: 1,
        label: {
          show: true,
          formatter: '{c}%',
          position: 'top',
          fontSize: 11,
          fontWeight: 'bold',
          color: '#faad14',
          backgroundColor: 'rgba(255,255,255,0.8)',
          padding: [2, 8, 2, 8],
          borderRadius: 16,
          borderColor: '#faad14',
          borderWidth: 1
        }
      }
    ],
    backgroundColor: '#fff'
  }
  
  chartInstance.setOption(option)
  chartInstance.resize()
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

const handleFilterChange = (filters: any) => {
  fetchDataAndDraw(filters)
}

onMounted(() => {
  emitter.on('filter-change', handleFilterChange)
  window.addEventListener('resize', handleResize)
  fetchDataAndDraw({ sentiment: 'all', category: 'all' })
})

onUnmounted(() => {
  emitter.off('filter-change', handleFilterChange)
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.top-apps-chart { 
  width: 100%; 
  min-height: 500px;
  background: linear-gradient(135deg, #fff 0%, #f5f7fa 100%);
  border-radius: 12px;
}
.loading { 
  text-align: center; 
  padding: 50px; 
  color: #999;
  font-size: 14px;
}
</style>