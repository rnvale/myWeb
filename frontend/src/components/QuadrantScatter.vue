<template>
  <div class="quadrant-scatter">
    <div ref="chartRef" style="width: 100%; height: 600px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'

interface AppData {
  app: string
  avg_rating: number
  total_reviews: number
  positive_rate: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)

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
  'notion': 'Notion',
  'facebook': '脸书',
  'teamspeak-3': 'TeamSpeak',
  'threema': 'Threema',
  'freeforest': 'FreeForest',
  'subway-surfers': '地铁跑酷',
  'minecraft': '我的世界',
  'heads-up': '猜词游戏'
}

const getChineseAppName = (appName: string): string => {
  if (!appName) return '未知'
  if (appNameMap[appName]) return appNameMap[appName]
  const firstWord = appName.split('-')[0]
  if (firstWord && appNameMap[firstWord]) return appNameMap[firstWord]
  if (appName.length > 12) return appName.slice(0, 10) + '..'
  return appName
}

onMounted(async () => {
  try {
    const res = await http.get('/quadrant_scatter')
    const data = res.data as AppData[]
    if (data && data.length > 0) {
      drawChart(data)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
})

const drawChart = (data: AppData[]) => {
  if (!chartRef.value) return
  
  const validData = data.filter(d => d.avg_rating > 0 && d.total_reviews > 0)
  
  if (validData.length === 0) return
  
  const ratings = validData.map(d => d.avg_rating)
  const reviews = validData.map(d => d.total_reviews)
  
  const minRating = Math.max(1, Math.floor(Math.min(...ratings) * 10) / 10 - 0.2)
  const maxRating = Math.min(5, Math.ceil(Math.max(...ratings) * 10) / 10 + 0.2)
  
  const sortedReviews = [...reviews].sort((a, b) => a - b)
  const len = sortedReviews.length
  const p10Index = Math.floor(len * 0.1)
  const p90Index = Math.floor(len * 0.9)
  const yMin = Math.max(0, (sortedReviews[p10Index] || 0) - 30)
  const yMax = (sortedReviews[p90Index] || 500) + 50
  
  const midRating = 3.8
  const midReviews = sortedReviews[Math.floor(len / 2)] || 200
  
  // 分类
  const starProducts: AppData[] = []
  const problemProducts: AppData[] = []
  const potentialProducts: AppData[] = []
  const edgeProducts: AppData[] = []
  
  validData.forEach(item => {
    if (item.avg_rating >= midRating && item.total_reviews >= midReviews) {
      starProducts.push(item)
    } else if (item.avg_rating < midRating && item.total_reviews >= midReviews) {
      problemProducts.push(item)
    } else if (item.avg_rating >= midRating && item.total_reviews < midReviews) {
      potentialProducts.push(item)
    } else {
      edgeProducts.push(item)
    }
  })
  
  const getTop5 = (arr: AppData[]) => [...arr].sort((a, b) => b.total_reviews - a.total_reviews).slice(0, 5)
  const topStar = getTop5(starProducts)
  const topPotential = getTop5(potentialProducts)
  const topProblem = getTop5(problemProducts)
  const topEdge = getTop5(edgeProducts)
  
  const seriesData = validData.map(item => ({
    name: getChineseAppName(item.app),
    value: [item.avg_rating, item.total_reviews],
    symbolSize: Math.min(40, 12 + Math.log10(item.total_reviews) * 6),
    rating: item.avg_rating,
    reviews: item.total_reviews,
    positiveRate: item.positive_rate
  }))
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '🎯 App 四象限分析图',
      subtext: '🏆明星产品(高评高热度) | ✨潜力股(高评低热度) | ⚠️问题产品(低评高热度) | 📌边缘产品(低评低热度)',
      left: 'center',
      top: 0,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#2c3e50' },
      subtextStyle: { fontSize: 11, color: '#7f8c8d' }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,0,0,0.85)',
      borderRadius: 8,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: (params: any) => {
        const d = params.data
        if (!d) return ''
        let quadrant = ''
        if (d.rating >= midRating && d.reviews >= midReviews) quadrant = '🏆 明星产品'
        else if (d.rating < midRating && d.reviews >= midReviews) quadrant = '⚠️ 问题产品'
        else if (d.rating >= midRating && d.reviews < midReviews) quadrant = '✨ 潜力股'
        else quadrant = '📌 边缘产品'
        return `<b>${d.name}</b><br/>${quadrant}<br/>⭐ ${d.rating}星<br/>📝 ${d.reviews}条<br/>👍 ${d.positiveRate}%`
      }
    },
    xAxis: {
      name: '平均评分 →',
      nameLocation: 'middle',
      nameGap: 35,
      min: minRating,
      max: maxRating,
      interval: 0.5,
      splitLine: { lineStyle: { type: 'dashed', color: '#ddd' } },
      axisLabel: { fontSize: 11, formatter: '{value}⭐' }
    },
    yAxis: {
      name: '评论数量 ↑',
      nameLocation: 'middle',
      nameGap: 45,
      min: yMin,
      max: yMax,
      splitLine: { lineStyle: { type: 'dashed', color: '#ddd' } },
      axisLabel: { fontSize: 11, formatter: (value: number) => {
        if (value >= 1000) return `${(value/1000).toFixed(0)}k`
        return `${value}`
      } }
    },
    series: [
      {
        type: 'scatter',
        data: seriesData,
        symbolSize: (params: any) => params.symbolSize || 18,
        itemStyle: {
          color: (params: any) => {
            const rating = params.data.rating
            const reviewsCount = params.data.reviews
            if (rating >= midRating && reviewsCount >= midReviews) return '#52c41a'
            if (rating < midRating && reviewsCount >= midReviews) return '#ff4d4f'
            if (rating >= midRating && reviewsCount < midReviews) return '#1890ff'
            return '#8c8c8c'
          },
          opacity: 0.5,
          borderWidth: 1,
          borderColor: '#fff'
        },
        label: { show: false },
        emphasis: { scale: 1.2 }
      },
      {
        type: 'scatter',
        data: topStar.map(item => ({
          name: getChineseAppName(item.app),
          value: [item.avg_rating, item.total_reviews],
          rating: item.avg_rating,
          reviews: item.total_reviews,
          positiveRate: item.positive_rate
        })),
        symbolSize: 38,
        itemStyle: { color: '#52c41a', shadowBlur: 10, borderWidth: 2, borderColor: '#fff' },
        label: { show: true, formatter: (params: any) => params.data.name, position: 'top', offset: [0, 14], fontSize: 11, fontWeight: 'bold', color: '#52c41a', backgroundColor: 'rgba(255,255,255,0.95)', padding: [2, 8, 2, 8], borderRadius: 14, borderColor: '#52c41a', borderWidth: 1 },
        emphasis: { scale: 1.3 }
      },
      {
        type: 'scatter',
        data: topPotential.map(item => ({
          name: getChineseAppName(item.app),
          value: [item.avg_rating, item.total_reviews],
          rating: item.avg_rating,
          reviews: item.total_reviews,
          positiveRate: item.positive_rate
        })),
        symbolSize: 32,
        itemStyle: { color: '#1890ff', shadowBlur: 10, borderWidth: 2, borderColor: '#fff' },
        label: { show: true, formatter: (params: any) => params.data.name, position: 'top', offset: [0, 12], fontSize: 11, fontWeight: 'bold', color: '#1890ff', backgroundColor: 'rgba(255,255,255,0.95)', padding: [2, 8, 2, 8], borderRadius: 14, borderColor: '#1890ff', borderWidth: 1 },
        emphasis: { scale: 1.3 }
      },
      {
        type: 'scatter',
        data: topProblem.map(item => ({
          name: getChineseAppName(item.app),
          value: [item.avg_rating, item.total_reviews],
          rating: item.avg_rating,
          reviews: item.total_reviews,
          positiveRate: item.positive_rate
        })),
        symbolSize: 32,
        itemStyle: { color: '#ff4d4f', shadowBlur: 10, borderWidth: 2, borderColor: '#fff' },
        label: { show: true, formatter: (params: any) => params.data.name, position: 'top', offset: [0, 12], fontSize: 11, fontWeight: 'bold', color: '#ff4d4f', backgroundColor: 'rgba(255,255,255,0.95)', padding: [2, 8, 2, 8], borderRadius: 14, borderColor: '#ff4d4f', borderWidth: 1 },
        emphasis: { scale: 1.3 }
      },
      {
        type: 'scatter',
        data: topEdge.map(item => ({
          name: getChineseAppName(item.app),
          value: [item.avg_rating, item.total_reviews],
          rating: item.avg_rating,
          reviews: item.total_reviews,
          positiveRate: item.positive_rate
        })),
        symbolSize: 28,
        itemStyle: { color: '#8c8c8c', shadowBlur: 8, borderWidth: 2, borderColor: '#fff' },
        label: { show: true, formatter: (params: any) => params.data.name, position: 'top', offset: [0, 12], fontSize: 11, fontWeight: 'bold', color: '#666', backgroundColor: 'rgba(255,255,255,0.95)', padding: [2, 8, 2, 8], borderRadius: 14, borderColor: '#ccc', borderWidth: 1 },
        emphasis: { scale: 1.3 }
      }
    ],
    // 只保留象限标注，中线描述统一放到右上角
    graphic: [
      { type: 'text', left: '68%', top: '8%', style: { text: '🏆 明星产品', fill: '#52c41a', fontSize: 12, fontWeight: 'bold' } },
      { type: 'text', left: '15%', top: '8%', style: { text: '⚠️ 问题产品', fill: '#ff4d4f', fontSize: 12, fontWeight: 'bold' } },
      { type: 'text', left: '68%', top: '75%', style: { text: '✨ 潜力股', fill: '#1890ff', fontSize: 12, fontWeight: 'bold' } },
      { type: 'text', left: '15%', top: '75%', style: { text: '📌 边缘产品', fill: '#8c8c8c', fontSize: 12, fontWeight: 'bold' } },
      // 中线描述统一放在右上角
      { type: 'text', left: '72%', top: '18%', style: { text: `📊 评分中线: ${midRating}⭐`, fill: '#e67e22', fontSize: 11, fontWeight: 'bold', backgroundColor: 'rgba(255,255,255,0.8)', padding: [2, 6, 2, 6], borderRadius: 4 } },
      { type: 'text', left: '72%', top: '24%', style: { text: `🔥 热度中线: ${midReviews}条`, fill: '#e67e22', fontSize: 11, fontWeight: 'bold', backgroundColor: 'rgba(255,255,255,0.8)', padding: [2, 6, 2, 6], borderRadius: 4 } }
    ],
    backgroundColor: '#fff'
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
</script>

<style scoped>
.quadrant-scatter { 
  width: 100%; 
  min-height: 600px;
  background: #fff;
  border-radius: 16px;
}
.loading { text-align: center; padding: 50px; color: #999; }
</style>