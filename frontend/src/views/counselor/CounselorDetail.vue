<template>
  <div class="counselor-detail">
    <PageHeader />
    <div class="container">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>

      <el-card v-loading="loading">
        <div class="counselor-header">
          <el-avatar :size="120" :src="counselor?.avatar" />
          <div class="header-info">
            <h1>{{ counselor?.name }}</h1>
            <el-rate v-model="counselor.rating" disabled show-score />
          </div>
          <el-button type="primary" @click="goToAppointment">立即预约</el-button>
        </div>

        <el-divider />

        <div class="info-section">
          <h3>擅长领域</h3>
          <p>{{ counselor?.specialties?.join('、') }}</p>
        </div>

        <div class="info-section">
          <h3>收费标准</h3>
          <p>视频: ¥{{ counselor?.price }}/小时</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorDetail } from '@/api/counselor'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const counselor = ref({})

const loadDetail = async () => {
  const res = await getCounselorDetail(route.params.id)
  counselor.value = res.data
  loading.value = false
}

const goBack = () => router.push('/counselor')
const goToAppointment = () => {
  router.push({ path: '/counselor/appointment', query: { counselorId: route.params.id } })
}

onMounted(() => loadDetail())
</script>

<style scoped>
@import '@/styles/variables.scss';
.counselor-detail { min-height: 100vh; background: $bg-color; }
.container { max-width: 900px; margin: 0 auto; padding: $spacing-lg; }
.counselor-header { display: flex; align-items: center; gap: $spacing-lg; margin-bottom: $spacing-xl; }
.info-section { margin: $spacing-xl 0; }
.info-section h3 { margin-bottom: $spacing-md; }
</style>
