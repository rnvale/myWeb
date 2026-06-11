<template>
  <div class="filter-bar">
    <div class="filter-group">
      <label>情感筛选：</label>
      <el-select v-model="selectedSentiment" placeholder="全部" @change="onFilterChange" clearable>
        <el-option label="全部" value="all"></el-option>
        <el-option label="正面" value="positive"></el-option>
        <el-option label="负面" value="negative"></el-option>
      </el-select>
    </div>
    
    <div class="filter-group">
      <label>方面类别：</label>
      <el-select v-model="selectedCategory" placeholder="全部" @change="onFilterChange" clearable filterable>
        <el-option label="全部" value="all"></el-option>
        <el-option v-for="cat in categoryOptions" :key="cat.value" :label="cat.label" :value="cat.value"></el-option>
      </el-select>
    </div>
    
    <div class="filter-info" v-if="totalCount > 0">
      当前筛选结果：<strong>{{ totalCount }}</strong> 条评论
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import http from '../http'
import emitter from '../utils/eventBus'
import { categoryMap } from '../utils/chineseMap'

const selectedSentiment = ref('all')
const selectedCategory = ref('all')
const totalCount = ref(0)

const categoryOptions = computed(() => {
  return Object.entries(categoryMap).map(([value, label]) => ({ value, label }))
})

onMounted(async () => {
  const res = await http.get('/aspect_sentiment')
})

const onFilterChange = () => {
  const filters = {
    sentiment: selectedSentiment.value,
    category: selectedCategory.value
  }
  
  emitter.emit('filter-change', filters)
  
  http.post('/filtered_summary', filters).then(res => {
    totalCount.value = res.data.total
  })
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
}

.filter-info {
  font-size: 13px;
  color: var(--primary, #1890ff);
  background: rgba(24, 144, 255, 0.1);
  padding: 6px 16px;
  border-radius: 20px;
  white-space: nowrap;
}
</style>