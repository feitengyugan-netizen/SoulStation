<template>
  <div class="empty-state">
    <div class="empty-state-content">
      <!-- 图标 -->
      <div class="empty-icon">
        <el-icon :size="iconSize" :color="iconColor">
          <component :is="iconComponent" />
        </el-icon>
      </div>

      <!-- 标题 -->
      <h3 class="empty-title">{{ title }}</h3>

      <!-- 描述 -->
      <p v-if="description" class="empty-description">
        {{ description }}
      </p>

      <!-- 操作按钮 -->
      <div v-if="showAction" class="empty-action">
        <el-button type="primary" @click="handleAction">
          {{ actionText }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Document,
  Box,
  Warning,
  CircleCheck,
  ShoppingCart,
  ChatDotSquare,
  DataAnalysis
} from '@element-plus/icons-vue'

const props = defineProps({
  // 空状态类型
  type: {
    type: String,
    default: 'default',
    validator: (value) => {
      return ['default', 'nodata', 'success', 'error', 'search', 'cart', 'chat', 'analysis'].includes(value)
    }
  },
  // 自定义标题
  title: {
    type: String,
    default: '暂无数据'
  },
  // 自定义描述
  description: {
    type: String,
    default: ''
  },
  // 是否显示操作按钮
  showAction: {
    type: Boolean,
    default: false
  },
  // 操作按钮文字
  actionText: {
    type: String,
    default: '立即操作'
  },
  // 图标大小
  iconSize: {
    type: Number,
    default: 80
  }
})

const emit = defineEmits(['action'])

// 根据类型选择图标
const iconComponent = computed(() => {
  const iconMap = {
    default: Document,
    nodata: Box,
    success: CircleCheck,
    error: Warning,
    search: Document,
    cart: ShoppingCart,
    chat: ChatDotSquare,
    analysis: DataAnalysis
  }
  return iconMap[props.type] || Document
})

// 根据类型选择颜色
const iconColor = computed(() => {
  const colorMap = {
    default: '#909399',
    nodata: '#C0C4CC',
    success: '#67C23A',
    error: '#F56C6C',
    search: '#409EFF',
    cart: '#E6A23C',
    chat: '#409EFF',
    analysis: '#67C23A'
  }
  return colorMap[props.type] || '#909399'
})

// 处理操作按钮点击
const handleAction = () => {
  emit('action')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl;
  min-height: 400px;
}

.empty-state-content {
  text-align: center;
}

.empty-icon {
  margin-bottom: $spacing-lg;
  opacity: 0.6;
}

.empty-title {
  font-size: $font-size-large;
  color: $text-primary;
  margin-bottom: $spacing-sm;
  font-weight: 500;
}

.empty-description {
  font-size: $font-size-base;
  color: $text-secondary;
  margin-bottom: $spacing-lg;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.empty-action {
  margin-top: $spacing-lg;
}
</style>
