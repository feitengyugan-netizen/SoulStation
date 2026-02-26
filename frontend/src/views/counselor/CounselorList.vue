<template>
  <div class="counselor-list-page">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>找咨询师</h1>
        <p>专业的心理咨询师，为您提供一对一服务</p>
      </div>

      <!-- 筛选卡片 -->
      <el-card class="filter-card">
        <div class="search-section">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索咨询师姓名、擅长领域..."
            prefix-icon="Search"
            clearable
            size="large"
            @keyup.enter="handleFilterChange"
          />
        </div>

        <div class="filter-section">
          <div class="filter-row">
            <span class="label">擅长领域:</span>
            <el-checkbox-group v-model="filters.specialties">
              <el-checkbox label="anxiety">焦虑</el-checkbox>
              <el-checkbox label="depression">抑郁</el-checkbox>
              <el-checkbox label="emotion">情感</el-checkbox>
              <el-checkbox label="career">职场</el-checkbox>
              <el-checkbox label="family">家庭</el-checkbox>
            </el-checkbox-group>
          </div>

          <div class="filter-row">
            <span class="label">咨询方式:</span>
            <el-checkbox-group v-model="filters.types">
              <el-checkbox label="video">视频</el-checkbox>
              <el-checkbox label="voice">语音</el-checkbox>
              <el-checkbox label="offline">线下</el-checkbox>
            </el-checkbox-group>
          </div>

          <div class="filter-row">
            <span class="label">价格范围:</span>
            <el-radio-group v-model="filters.priceRange">
              <el-radio label="">不限</el-radio>
              <el-radio label="0-200">¥0-200</el-radio>
              <el-radio label="200-500">¥200-500</el-radio>
              <el-radio label="500+">¥500+</el-radio>
            </el-radio-group>
          </div>

          <div class="filter-row">
            <span class="label">排序:</span>
            <el-select v-model="filters.sort" style="width: 120px">
              <el-option label="综合" value="default" />
              <el-option label="评分最高" value="rating" />
              <el-option label="销量最高" value="orders" />
              <el-option label="价格最低" value="price-asc" />
            </el-select>
          </div>
        </div>
      </el-card>

      <!-- 咨询师列表 -->
      <div v-loading="loading" class="counselor-grid">
        <el-skeleton v-if="loading && counselors.length === 0" :rows="3" animated />

        <el-empty v-else-if="!loading && counselors.length === 0" description="暂无咨询师" />

        <div
          v-for="counselor in counselors"
          :key="counselor.id"
          class="counselor-card"
        >
          <div class="counselor-avatar">
            <el-avatar :size="100" :src="counselor.avatar">
              <el-icon :size="50"><User /></el-icon>
            </el-avatar>
          </div>

          <div class="counselor-info">
            <h3>{{ counselor.name }}</h3>

            <div class="rating-row">
              <el-rate
                v-model="counselor.rating"
                disabled
                show-score
                text-color="#ff9900"
              />
              <span class="review-count">({{ counselor.reviewCount }}条评价)</span>
            </div>

            <div class="info-row">
              <span class="label">擅长:</span>
              <el-tag
                v-for="specialty in counselor.specialties"
                :key="specialty"
                size="small"
              >
                {{ specialty }}
              </el-tag>
            </div>

            <div class="info-row">
              <span class="label">方式:</span>
              <span class="types-text">
                <span v-if="counselor.types?.includes('video')">视频</span>
                <span v-if="counselor.types?.includes('voice')">语音</span>
                <span v-if="counselor.types?.includes('offline')">线下</span>
              </span>
            </div>

            <div class="price-row">
              <span class="price">¥{{ counselor.price }}</span>
              <span class="unit">/小时</span>
            </div>

            <div class="action-buttons">
              <el-button @click="viewDetail(counselor.id)">查看详情</el-button>
              <el-button type="primary" @click="goToAppointment(counselor.id)">预约</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[12, 24, 36]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, User } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorList } from '@/api/counselor'

const router = useRouter()

const loading = ref(false)
const counselors = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
  specialties: [],
  types: [],
  priceRange: '',
  sort: 'default'
})

const pagination = reactive({
  page: 1,
  pageSize: 12
})

const loadCounselors = async () => {
  try {
    loading.value = true
    const params = {
      ...filters,
      specialties: filters.specialties.join(','),
      types: filters.types.join(','),
      ...pagination
    }
    const res = await getCounselorList(params)
    counselors.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadCounselors()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadCounselors()
}

const handlePageChange = () => {
  loadCounselors()
}

const viewDetail = (id) => {
  router.push(`/counselor/${id}`)
}

const goToAppointment = (id) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push({ path: '/counselor/appointment', query: { counselorId: id } })
}

onMounted(() => {
  loadCounselors()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.counselor-list-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.page-header {
  text-align: center;
  margin-bottom: $spacing-xl;

  h1 {
    font-size: 36px;
    margin-bottom: $spacing-sm;
  }

  p {
    color: $text-secondary;
  }
}

.filter-card {
  margin-bottom: $spacing-lg;
}

.search-section {
  margin-bottom: $spacing-lg;
}

.filter-section {
  .filter-row {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-md;

    &:last-child {
      margin-bottom: 0;
    }

    .label {
      font-weight: 500;
      min-width: 80px;
    }
  }
}

.counselor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.counselor-card {
  background: $bg-white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $box-shadow-base;
  transition: $transition-base;

  &:hover {
    box-shadow: $box-shadow-dark;
    transform: translateY(-4px);
  }

  .counselor-avatar {
    text-align: center;
    margin-bottom: $spacing-md;
  }

  .counselor-info {
    h3 {
      text-align: center;
      margin: 0 0 $spacing-sm;
    }

    .rating-row {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: $spacing-sm;
      margin-bottom: $spacing-md;

      .review-count {
        font-size: $font-size-small;
        color: $text-secondary;
      }
    }

    .info-row {
      display: flex;
      align-items: center;
      gap: $spacing-xs;
      margin-bottom: $spacing-sm;

      .label {
        font-weight: 500;
      }
    }

    .price-row {
      text-align: center;
      margin: $spacing-md 0;

      .price {
        font-size: 28px;
        font-weight: 600;
        color: $primary-color;
      }

      .unit {
        color: $text-secondary;
      }
    }

    .action-buttons {
      display: flex;
      gap: $spacing-sm;

      .el-button {
        flex: 1;
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
}

@media (max-width: $breakpoint-md) {
  .counselor-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  .filter-section .filter-row {
    flex-wrap: wrap;
  }
}
</style>
