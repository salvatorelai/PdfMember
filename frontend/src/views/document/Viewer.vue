<template>
  <div class="pdf-viewer">
    <div class="toolbar">
      <el-button @click="$router.back()">Back</el-button>
      <div class="controls">
        <el-button @click="prevPage" :disabled="pageNum <= 1">Previous</el-button>
        <span>Page {{ pageNum }} / {{ numPages }}</span>
        <el-button @click="nextPage" :disabled="pageNum >= numPages">Next</el-button>
        <el-divider direction="vertical" />
        <el-button @click="zoomOut" icon="Minus" circle />
        <span>{{ Math.round(scale * 100) }}%</span>
        <el-button @click="zoomIn" icon="Plus" circle />
      </div>
    </div>
    
    <div class="debug-info" v-if="errorMsg" style="color: red; padding: 20px; background: white;">
      Error: {{ errorMsg }}
    </div>

    <div class="pdf-container" v-loading="loading" ref="containerRef">
      <canvas ref="pdfCanvas"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue'
import { useRoute } from 'vue-router'
import { getDocument as getApiDocument } from '../../api/document'
import { ElMessage } from 'element-plus'
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist'
import { Plus, Minus } from '@element-plus/icons-vue'

// Set worker source to static file in public folder
GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs'

const route = useRoute()
const pdfCanvas = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const loading = ref(false)
const errorMsg = ref('')

// Use shallowRef for non-reactive complex objects to improve performance and avoid proxy issues
const pdfDoc = shallowRef<any>(null)
const pageNum = ref(1)
const numPages = ref(0)
const scale = ref(1.0)
const isRendering = ref(false)
const pageNumPending = ref<number | null>(null)

const fetchAndLoadPdf = async () => {
  const id = parseInt(route.params.id as string)
  if (!id) return
  
  loading.value = true
  errorMsg.value = ''
  try {
    const res: any = await getApiDocument(id)
    const doc = res
    
    // Construct URL
    let url = doc.file_path
    if (!url) {
      throw new Error('No file path provided')
    }

    // Normalize URL
    if (url.startsWith('/static')) {
       // Keep as is, it's relative to domain root
    } else if (url.startsWith('http')) {
       // Keep as is
    } else {
       // Assume it's a relative path that needs /static prefix
       url = url.startsWith('/') ? `/static${url}` : `/static/${url}`
    }

    console.log('Loading PDF from URL:', url)
    
    // Load PDF
    const loadingTask = getDocument({
      url: url,
      cMapUrl: '/cmaps/',
      cMapPacked: true,
    })
    pdfDoc.value = await loadingTask.promise
    numPages.value = pdfDoc.value.numPages
    
    // Auto-scale to fit container width
    const firstPage = await pdfDoc.value.getPage(1)
    const unscaledViewport = firstPage.getViewport({ scale: 1.0 })
    
    if (containerRef.value) {
      // Subtract some padding (e.g. 40px)
      const containerWidth = containerRef.value.clientWidth - 40
      if (containerWidth > 0 && unscaledViewport.width > containerWidth) {
        scale.value = containerWidth / unscaledViewport.width
        console.log('Auto-scaled to:', scale.value)
      }
    }

    // Render first page
    renderPage(pageNum.value)
    
  } catch (error: any) {
    const msg = `Failed to load PDF: ${error.message || error}`
    console.error(msg)
    errorMsg.value = msg
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const renderPage = async (num: number) => {
  isRendering.value = true
  
  try {
    if (!pdfDoc.value) return

    const page = await pdfDoc.value.getPage(num)
    
    const viewport = page.getViewport({ scale: scale.value })
    const canvas = pdfCanvas.value
    if (!canvas) {
        console.error('Canvas element not found')
        return
    }
    
    const context = canvas.getContext('2d')
    if (!context) {
        console.error('Canvas context could not be obtained')
        return
    }

    canvas.height = viewport.height
    canvas.width = viewport.width

    console.log('Rendering page:', num, 'Scale:', scale.value, 'Viewport:', viewport.width, 'x', viewport.height)
    
    const renderContext = {
      canvasContext: context!,
      viewport: viewport
    }
    
    const renderTask = page.render(renderContext)
    
    // Wait for render to finish
    await renderTask.promise
    isRendering.value = false
    
    if (pageNumPending.value !== null) {
      renderPage(pageNumPending.value)
      pageNumPending.value = null
    }
  } catch (error: any) {
    console.error('Render Error:', error)
    errorMsg.value = `Render Error: ${error.message}`
    isRendering.value = false
  }
}

const queueRenderPage = (num: number) => {
  if (isRendering.value) {
    pageNumPending.value = num
  } else {
    renderPage(num)
  }
}

const prevPage = () => {
  if (pageNum.value <= 1) return
  pageNum.value--
  queueRenderPage(pageNum.value)
}

const nextPage = () => {
  if (pageNum.value >= numPages.value) return
  pageNum.value++
  queueRenderPage(pageNum.value)
}

const zoomIn = () => {
  scale.value += 0.2
  queueRenderPage(pageNum.value)
}

const zoomOut = () => {
  if (scale.value <= 0.4) return
  scale.value -= 0.2
  queueRenderPage(pageNum.value)
}

onMounted(() => {
  fetchAndLoadPdf()
})
</script>

<style scoped>
.pdf-viewer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #525659;
}
.toolbar {
  background-color: #323639;
  color: #fff;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  z-index: 10;
}
.controls {
  display: flex;
  align-items: center;
  gap: 15px;
}
.controls span {
  font-size: 14px;
}
.pdf-container {
  flex: 1;
  overflow: auto;
  display: flex;
  justify-content: center;
  padding: 20px;
}
canvas {
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
</style>
