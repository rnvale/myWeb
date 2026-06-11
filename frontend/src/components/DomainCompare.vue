<template>
  <div class="domain-compare">
    <div ref="chartRef" style="width: 100%; height: 420px;"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import http from '../http'
import emitter from '../utils/eventBus'

interface DomainData {
  domain: string
  positive: number
  negative: number
  positive_rate: number
  total: number
}

const chartRef = ref<HTMLElement | null>(null)
const loading = ref(true)
let chartInstance: any = null

const domainMap: Record<string, string> = {
  'productivity': '生产力工具',
  'games': '游戏',
  'social networking': '社交网络'
}

const fetchDataAndDraw = async (filters: any = { sentiment: 'all', category: 'all' }) => {
  if (!chartRef.value) return
  
  loading.value = true
  
  try {
    // 使用筛选后的领域对比接口
    const res = await http.post('/filtered_domain_compare', filters)
    const data = res.data as DomainData[]
    if (data && data.length > 0) {
      drawChart(data)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const drawChart = (data: DomainData[]) => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  const domains = data.map((item: DomainData) => domainMap[item.domain] || item.domain)
  
  const maxTotal = Math.max(...data.map((item: DomainData) => item.total))
  
  const positiveRates = data.map((item: DomainData) => item.positive_rate)
  const totalNormalized = data.map((item: DomainData) => (item.total / maxTotal) * 100)
  const diffRates = data.map((item: DomainData) => ((item.positive - item.negative) / item.total) * 100)
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: '📡 不同领域 App 多维雷达对比',
      subtext: filtersTip.value ? `筛选条件: ${filtersTip.value}` : '',
      left: 'center',
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const idx = params.dataIndex
        if (idx === undefined || !domains[idx]) return ''
        const domain = domains[idx]
        if (params.seriesName === '正面率 (%)') {
          const rate = positiveRates[idx] || 0
          return `${domain}<br/>正面率: ${rate.toFixed(1)}%`
        } else if (params.seriesName === '评论总数 (归一化)') {
          const total = data[idx]?.total || 0
          return `${domain}<br/>评论总数: ${total} 条`
        } else {
          const diff = diffRates[idx] || 0
          return `${domain}<br/>正负面差异: ${diff.toFixed(1)}%`
        }
      }
    },
    legend: {
      data: ['正面率 (%)', '评论总数 (归一化)', '正负面差异 (%)'],
      left: 'left',
      top: 30,
      textStyle: { fontSize: 11 }
    },
    radar: {
      indicator: domains.map((domain: string) => ({ name: domain, max: 100 })),
      shape: 'circle',
      center: ['50%', '52%'],
      radius: '60%',
      name: { textStyle: { fontSize: 10, fontWeight: 'bold' } },
      splitArea: {
        areaStyle: {
          color: ['rgba(82, 196, 26, 0.05)', 'rgba(255, 77, 79, 0.05)']
        }
      }
    },
    series: [
      {
        name: '正面率 (%)',
        type: 'radar',
        data: [{ value: positiveRates, name: '正面率' }],
        areaStyle: { color: 'rgba(82, 196, 26, 0.3)' },
        lineStyle: { color: '#52c41a', width: 2 },
        itemStyle: { color: '#52c41a' },
        symbolSize: 6
      },
      {
        name: '评论总数 (归一化)',
        type: 'radar',
        data: [{ value: totalNormalized, name: '评论总数' }],
        areaStyle: { color: 'rgba(84, 112, 198, 0.2)' },
        lineStyle: { color: '#5470c6', width: 2, type: 'dashed' },
        itemStyle: { color: '#5470c6' },
        symbolSize: 6
      },
      {
        name: '正负面差异 (%)',
        type: 'radar',
        data: [{ value: diffRates, name: '差异' }],
        areaStyle: { color: 'rgba(250, 173, 20, 0.15)' },
        lineStyle: { color: '#faad14', width: 2 },
        itemStyle: { color: '#faad14' },
        symbolSize: 6
      }
    ]
  }
  
  chartInstance.setOption(option)
}

let filtersTip = ref('')

const handleFilterChange = (filters: any) => {
  // 生成筛选提示文字
  let tip = ''
  if (filters.sentiment === 'positive') tip = '仅正面评论'
  else if (filters.sentiment === 'negative') tip = '仅负面评论'
  else tip = '全部评论'
  if (filters.category && filters.category !== 'all') tip += `, 类别: ${filters.category}`
  filtersTip.value = tip
  
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
.domain-compare { width: 100%; min-height: 420px; }
.loading { text-align: center; padding: 50px; color: #999; }
</style>