import { useState, useRef } from 'react'
import { Upload, X, FileText, Image as ImageIcon, FileType } from 'lucide-react'

export default function FileUploader({ onUpload, uploadProgress = 0, isUploading = false }) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    // Validate file type
    const validExtensions = ['.pdf', '.docx', '.pptx', '.txt', '.md', '.markdown', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    const fileExt = '.' + file.name.split('.').pop().toLowerCase()
    
    if (!validExtensions.includes(fileExt)) {
      alert(`Unsupported file type: ${fileExt}\nSupported: ${validExtensions.join(', ')}`)
      return
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      alert('File size exceeds 50MB limit')
      return
    }

    setSelectedFile(file)
    onUpload(file)
  }

  const handleRemove = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getFileIcon = (fileName) => {
    const ext = '.' + fileName.split('.').pop().toLowerCase()
    if (ext === '.pdf') {
      return <FileText className="w-12 h-12 text-red-500" />
    } else if (['.docx', '.pptx', '.txt', '.md'].includes(ext)) {
      return <FileType className="w-12 h-12 text-blue-500" />
    } else {
      return <ImageIcon className="w-12 h-12 text-green-500" />
    }
  }

  return (
    <div className="space-y-4">
      <div
        className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
          dragActive
            ? 'border-primary-500 bg-primary-50 scale-[1.02]'
            : 'border-gray-300 hover:border-primary-400 bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleChange}
          className="hidden"
          accept=".pdf,.docx,.pptx,.txt,.md,.markdown,.png,.jpg,.jpeg,.gif,.bmp,.webp"
        />
        
        {selectedFile ? (
          <div className="w-full">
            <div className="flex items-center justify-center gap-4 mb-4">
              {getFileIcon(selectedFile.name)}
              <div className="flex-1 text-left">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  {!isUploading && (
                    <button
                      onClick={handleRemove}
                      className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                    >
                      <X className="w-5 h-5 text-gray-500" />
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            {/* Progress Bar */}
            {isUploading && (
              <div className="w-full">
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-primary-600 h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2 text-center">
                  {uploadProgress < 100 ? `Đang tải lên... ${uploadProgress}%` : 'Đang xử lý file...'}
                </p>
              </div>
            )}
          </div>
        ) : (
          <>
            <div className="flex items-center justify-center gap-6 mb-4">
              <FileText className="w-16 h-16 text-red-500" />
              <FileType className="w-16 h-16 text-blue-500" />
              <ImageIcon className="w-16 h-16 text-green-500" />
            </div>
            <div className="mb-4">
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            </div>
            <p className="text-lg text-gray-700 mb-2">
              Thả tệp hoặc{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-primary-600 hover:text-primary-700 font-semibold underline"
              >
                tải lên
              </button>
            </p>
            <p className="text-sm text-gray-500">
              PDF, DOCX, PPTX, TXT, MD, Images
            </p>
          </>
        )}
      </div>
    </div>
  )
}
