import { useState } from 'react'
import { User, Bot, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false)
  const [showSources, setShowSources] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-3xl">
          <div className="bg-primary-600 text-white rounded-2xl px-5 py-3 shadow-md">
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {formatTimestamp(message.timestamp)}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-3xl w-full">
        <div className="bg-white border-2 border-gray-200 rounded-2xl px-5 py-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              {message.isLoading ? (
                <div className="flex items-center gap-2 text-gray-500">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-sm">Thinking...</span>
                </div>
              ) : (
                <>
                  <div className="prose prose-sm max-w-none markdown-content">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="mb-3 text-gray-800 leading-relaxed">{children}</p>,
                        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                        em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
                        ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 text-gray-800">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-800">{children}</ol>,
                        li: ({ children }) => <li className="ml-4">{children}</li>,
                        h1: ({ children }) => <h1 className="text-xl font-bold mb-2 mt-4 text-gray-900">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-lg font-semibold mb-2 mt-3 text-gray-900">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-base font-semibold mb-2 mt-2 text-gray-900">{children}</h3>,
                        code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800">{children}</code>,
                        pre: ({ children }) => <pre className="bg-gray-100 p-3 rounded mb-3 overflow-x-auto">{children}</pre>,
                        blockquote: ({ children }) => <blockquote className="border-l-4 border-primary-300 pl-4 italic text-gray-700 mb-3">{children}</blockquote>,
                        hr: () => <hr className="my-4 border-gray-300" />,
                      }}
                    >
                      {message.content || 'No response generated.'}
                    </ReactMarkdown>
                  </div>
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button
                        onClick={() => setShowSources(!showSources)}
                        className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
                      >
                        {showSources ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                        <span>Sources ({message.sources.length})</span>
                      </button>
                      
                      {showSources && (
                        <div className="mt-3 space-y-2">
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="p-3 bg-gray-50 rounded-lg text-xs border border-gray-200"
                            >
                              <div className="font-semibold text-gray-700 mb-1">
                                Source {source.index}: {source.source_file}
                                {source.page && ` (Page ${source.page})`}
                                {source.slide_number && ` (Slide ${source.slide_number})`}
                                {source.content_type && (
                                  <span className="ml-2 px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs">
                                    {source.content_type}
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-600 line-clamp-2">
                                {source.preview}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
            {!message.isLoading && message.content && (
              <button
                onClick={handleCopy}
                className="flex-shrink-0 p-1.5 hover:bg-gray-100 rounded transition-colors"
                title="Copy"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4 text-gray-400" />
                )}
              </button>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {formatTimestamp(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
