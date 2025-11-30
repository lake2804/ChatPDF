import { useState, useEffect, useRef, createContext, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import ChatWindow from './components/ChatWindow'
import FileUploader from './components/FileUploader'
import Login from './components/Login'
import Register from './components/Register'
import { Trash2, X, Plus, Sparkles, LogOut, User } from 'lucide-react'

// Use proxy in development, direct URL in production
const API_BASE = import.meta.env.VITE_API_BASE || (
  import.meta.env.DEV 
    ? '/api'  // Use Vite proxy in development
    : import.meta.env.PROD
    ? 'https://your-backend-url.railway.app'  // Production backend URL - UPDATE THIS
    : 'http://localhost:8000'  // Fallback for local production build
)

// Auth Context
const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// Auth Provider
function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user')
    return savedUser ? JSON.parse(savedUser) : null
  })

  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const register = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Protected Route Component
function ProtectedRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

// Main App Content
function AppContent() {
  const { user, logout } = useAuth()
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [activeTab, setActiveTab] = useState('chat')
  const [showChat, setShowChat] = useState(false)
  const [backendStatus, setBackendStatus] = useState(null)
  const messagesEndRef = useRef(null)
  const navigate = useNavigate()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log(`Checking backend health at: ${API_BASE}/health`)
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
        
        const response = await fetch(`${API_BASE}/health`, { 
          method: 'GET',
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
          }
        })
        
        clearTimeout(timeoutId)
        
        if (response.ok) {
          const data = await response.json()
          setBackendStatus({ connected: true, data })
          console.log('✅ Backend health check success:', data)
        } else {
          const errorText = await response.text()
          console.error('❌ Backend health check failed:', response.status, errorText)
          setBackendStatus({ connected: false, error: `HTTP ${response.status}: ${errorText}` })
        }
      } catch (error) {
        console.error('❌ Backend health check error:', error)
        let errorMsg = error.message || 'Cannot connect to backend'
        if (error.name === 'AbortError') {
          errorMsg = 'Request timeout - backend may be slow or not responding'
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMsg = `Cannot connect to ${API_BASE}. Is backend running?`
        }
        setBackendStatus({ 
          connected: false, 
          error: errorMsg
        })
      }
    }
    checkBackend()
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleLogout = () => {
    logout()
    setMessages([])
    setShowChat(false)
    navigate('/login')
  }

  const handleUpload = async (file) => {
    // Check backend connection first
    if (backendStatus && !backendStatus.connected) {
      setUploadStatus({ 
        type: 'error', 
        message: `❌ Không thể kết nối đến backend. Vui lòng kiểm tra server đang chạy tại ${API_BASE}` 
      })
      return
    }

    setUploadStatus({ type: 'uploading', message: 'Đang tải lên...' })
    setUploadProgress(0)
    
    const formData = new FormData()
    formData.append('file', file)

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded / e.total) * 100)
          setUploadProgress(percentComplete)
          setUploadStatus({ 
            type: 'uploading', 
            message: `Đang tải lên... ${percentComplete}%` 
          })
        }
      })

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText)
            console.log('Upload success:', data)
            setUploadProgress(100)
            setUploadStatus({ 
              type: 'success', 
              message: `✅ ${data.filename} đã được lập chỉ mục (${data.chunks_indexed} chunks)` 
            })
            
            // Auto-switch to chat after successful upload
            setShowChat(true)
            setActiveTab('chat')
            
            // Clear status after 5 seconds
            setTimeout(() => {
              setUploadStatus(null)
              setUploadProgress(0)
            }, 5000)
            resolve(data)
          } catch (e) {
            console.error('Error parsing response:', e)
            reject(new Error('Invalid response from server'))
          }
        } else {
          let errorMessage = 'Upload failed'
          try {
            const errorData = JSON.parse(xhr.responseText)
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (e) {
            errorMessage = xhr.responseText || `HTTP ${xhr.status}: ${xhr.statusText}`
          }
          reject(new Error(errorMessage))
        }
      })

      // Handle errors
      xhr.addEventListener('error', () => {
        reject(new Error('Network error occurred'))
      })

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload cancelled'))
      })

      // Open and send request
      xhr.open('POST', `${API_BASE}/upload`)
      xhr.send(formData)
    }).catch((error) => {
      console.error('Upload error:', error)
      let errorMessage = error.message || 'Upload failed'
      
      // Provide more helpful error messages
      if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError') || errorMessage.includes('fetch') || errorMessage.includes('Network error')) {
        errorMessage = `Không thể kết nối đến backend server.\n\nVui lòng kiểm tra:\n- Backend server đang chạy tại ${API_BASE}\n- CORS đã được cấu hình đúng\n- Không có firewall chặn kết nối`
      } else if (errorMessage.includes('pypdf')) {
        errorMessage = 'Lỗi xử lý PDF: pypdf chưa được cài đặt trong backend.\n\nChạy lệnh: pip install pypdf'
      } else if (errorMessage.includes('timeout')) {
        errorMessage = 'Request timeout. File có thể quá lớn hoặc backend đang xử lý chậm.'
      }
      
      setUploadStatus({ 
        type: 'error', 
        message: `❌ ${errorMessage}` 
      })
      setUploadProgress(0)
      setTimeout(() => {
        setUploadStatus(null)
      }, 8000)
    })
  }

  const handleAsk = async (question, stream = false) => {
    if (!question.trim()) return

    // Check backend connection first
    if (backendStatus && !backendStatus.connected) {
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ Không thể kết nối đến backend. Vui lòng kiểm tra server đang chạy tại ${API_BASE}`,
        isLoading: false,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])

    // Add placeholder for assistant response
    const assistantId = Date.now() + 1
    setMessages(prev => [...prev, {
      id: assistantId,
      role: 'assistant',
      content: '',
      sources: [],
      isLoading: true,
      timestamp: new Date(),
    }])

    setIsLoading(true)

    try {
      console.log(`Asking question to: ${API_BASE}/ask`)
      const response = await fetch(
        `${API_BASE}/ask`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: question,
            stream: stream,
            k: 5
          })
        }
      )

      console.log(`Ask response status: ${response.status}`)

      if (!response.ok) {
        let errorMessage = 'Failed to get response'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
          console.error('Ask error response:', errorData)
        } catch (e) {
          const text = await response.text()
          console.error('Ask error text:', text)
          errorMessage = text || `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      if (stream) {
        // Handle streaming response
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let fullAnswer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.trim()) {
              try {
                const jsonStr = line.trim()
                if (jsonStr.startsWith('{"answer": "')) {
                  const match = jsonStr.match(/"answer":\s*"([^"]*)"/)
                  if (match) {
                    fullAnswer = match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"')
                    setMessages(prev => prev.map(msg => 
                      msg.id === assistantId 
                        ? { ...msg, content: fullAnswer, isLoading: false }
                        : msg
                    ))
                  }
                }
              } catch (e) {
                // Continue parsing
              }
            }
          }
        }
      } else {
        // Handle non-streaming response
        const data = await response.json()
        setMessages(prev => prev.map(msg => 
          msg.id === assistantId 
            ? { 
                ...msg, 
                content: data.answer, 
                sources: data.sources || [],
                isLoading: false 
              }
            : msg
        ))
      }
    } catch (error) {
      console.error('Error asking question:', error)
      let errorMessage = error.message || 'Unknown error'
      
      // Provide more helpful error messages
      if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError') || errorMessage.includes('fetch')) {
        errorMessage = 'Không thể kết nối đến backend server. Vui lòng kiểm tra backend đang chạy tại http://localhost:8000'
      } else if (errorMessage.includes('quota') || errorMessage.includes('rate limit')) {
        errorMessage = 'Google API đã vượt quá quota hoặc bị rate limit. Vui lòng thử lại sau hoặc kiểm tra quota API key.'
      } else if (errorMessage.includes('get_relevant_documents')) {
        errorMessage = 'Lỗi tương thích LangChain. Vui lòng cập nhật langchain-community trong backend'
      } else if (errorMessage.includes('No documents') || errorMessage.includes('empty') || errorMessage.includes('No documents indexed')) {
        errorMessage = 'Chưa có tài liệu nào được tải lên. Vui lòng tải lên ít nhất một tài liệu trước.'
      } else if (errorMessage.includes('API key') || errorMessage.includes('GOOGLE_API_KEY') || errorMessage.includes('authentication')) {
        errorMessage = 'Lỗi Google API key. Vui lòng kiểm tra file .env trong backend'
      } else if (errorMessage.includes('Qdrant') || errorMessage.includes('connection') || errorMessage.includes('vector database')) {
        errorMessage = 'Không thể kết nối đến Qdrant. Vui lòng đảm bảo Qdrant đang chạy'
      } else if (errorMessage.includes('Failed to retrieve') || errorMessage.includes('retrieve documents')) {
        errorMessage = 'Không thể truy xuất tài liệu từ database. Vui lòng đảm bảo tài liệu đã được lập chỉ mục đúng cách.'
      }
      
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? { 
              ...msg, 
              content: `❌ Lỗi: ${errorMessage}\n\nVui lòng kiểm tra:\n- Backend server đang chạy (http://localhost:8000)\n- Bạn đã tải lên ít nhất một tài liệu\n- Google API key đã được cấu hình đúng\n- Qdrant đang chạy`, 
              isLoading: false 
            }
          : msg
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const handleSummarize = async (customPrompt) => {
    setUploadStatus({ type: 'uploading', message: 'Đang tóm tắt tài liệu...' })
    
    try {
      const response = await fetch(
        `${API_BASE}/summarize${customPrompt ? `?question=${encodeURIComponent(customPrompt)}` : ''}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(customPrompt ? { question: customPrompt } : {})
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || 'Summarize failed')
      }

      const data = await response.json()
      setShowChat(true)
      setActiveTab('chat')
      
      // Add summary as a message
      const summaryMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `📄 **Tóm tắt tài liệu:**\n\n${data.summary}\n\n*Dựa trên ${data.source_count} nguồn*`,
        sources: data.sources || [],
        timestamp: new Date(),
      }
      setMessages([summaryMessage])
      
      setUploadStatus({ 
        type: 'success', 
        message: '✅ Tóm tắt hoàn thành' 
      })
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (error) {
      setUploadStatus({ 
        type: 'error', 
        message: `❌ ${error.message}` 
      })
      setTimeout(() => setUploadStatus(null), 5000)
    }
  }

  const handleReset = async () => {
    if (!confirm('Bạn có chắc chắn muốn xóa tất cả tài liệu đã lập chỉ mục?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE}/reset`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Reset failed')
      }

      setMessages([])
      setUploadStatus({ 
        type: 'success', 
        message: '✅ Đã xóa tất cả dữ liệu thành công' 
      })
      setTimeout(() => setUploadStatus(null), 3000)
    } catch (error) {
      setUploadStatus({ 
        type: 'error', 
        message: `❌ ${error.message}` 
      })
      setTimeout(() => setUploadStatus(null), 5000)
    }
  }

  const tabs = [
    { id: 'chat', label: 'Chat' },
    { id: 'summarize', label: 'Tóm tắt' },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">ChatPDF</h1>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700">
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">{user?.name || user?.email || 'User'}</span>
              </div>
              <button 
                onClick={() => {
                  setShowChat(false)
                  setMessages([])
                  setUploadStatus(null)
                }}
                className="px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Mới</span>
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-gray-600 hover:text-gray-700 rounded-lg transition-colors flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Backend Status Indicator */}
        {backendStatus && !backendStatus.connected && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm">
            ⚠️ Không thể kết nối đến backend: {backendStatus.error || 'Unknown error'}
            <br />
            Vui lòng kiểm tra backend đang chạy tại {API_BASE}
          </div>
        )}
        
        {!showChat ? (
          /* Landing Page */
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-2 mb-6">
              <Sparkles className="w-6 h-6 text-primary-600" />
              <h2 className="text-4xl md:text-5xl font-bold text-primary-700">
                Công cụ AI cho sinh viên và nhà nghiên cứu
              </h2>
            </div>

            {/* Main Card */}
            <div className="max-w-4xl mx-auto bg-white rounded-2xl border-2 border-gray-200 shadow-xl p-8">
              {/* Tabs */}
              <div className="flex gap-2 mb-6 border-b border-gray-200 pb-4 overflow-x-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Upload Area */}
              <div className="mb-6">
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                  Chat với bất kỳ tệp, video hoặc website
                </h3>
                <FileUploader 
                  onUpload={handleUpload} 
                  uploadProgress={uploadProgress}
                  isUploading={uploadStatus?.type === 'uploading'}
                />
              </div>

              {/* Input Field */}
              <div className="mt-6">
                <input
                  type="text"
                  placeholder={
                    activeTab === 'chat' ? "Hoặc đặt câu hỏi, dán link YouTube hoặc link web" :
                    activeTab === 'summarize' ? "Tóm tắt tài liệu (hoặc để trống để tự động tóm tắt)" :
                    "Nhập nội dung hoặc câu hỏi..."
                  }
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.target.value.trim()) {
                      if (activeTab === 'summarize') {
                        handleSummarize(e.target.value || undefined)
                      } else if (activeTab === 'chat') {
                        setShowChat(true)
                        handleAsk(e.target.value)
                      }
                    }
                  }}
                />
              </div>

              {uploadStatus && uploadStatus.type !== 'uploading' && (
                <div className={`mt-4 p-3 rounded-lg text-sm ${
                  uploadStatus.type === 'success' 
                    ? 'bg-green-50 text-green-700 border border-green-200' 
                    : uploadStatus.type === 'error'
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-blue-50 text-blue-700 border border-blue-200'
                }`}>
                  {uploadStatus.message}
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Chat Interface */
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-xl overflow-hidden">
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setShowChat(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <X className="w-5 h-5" />
                  </button>
                  <h3 className="text-lg font-semibold text-gray-900">Chat</h3>
                </div>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Xóa dữ liệu
                </button>
              </div>
              <ChatWindow
                messages={messages}
                onAsk={handleAsk}
                isLoading={isLoading}
                messagesEndRef={messagesEndRef}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

// Login Page Component
function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()

  if (user) {
    return <Navigate to="/" replace />
  }

  return <Login onLogin={(userData) => { login(userData); navigate('/') }} />
}

// Register Page Component
function RegisterPage() {
  const { register, user } = useAuth()
  const navigate = useNavigate()

  if (user) {
    return <Navigate to="/" replace />
  }

  return <Register onRegister={(userData) => { register(userData); navigate('/') }} />
}

// Main App with Router
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <AppContent />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
