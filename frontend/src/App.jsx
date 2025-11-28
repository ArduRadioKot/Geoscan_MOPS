import { useCallback, useEffect, useState } from 'react'
import './App.css'
import Header from './components/header/header'
import Sidebar from './components/leftPanel/leftPanel'
import ImageViewer from './components/imageViewer/imageViewer'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [imageUrl, setImageUrl] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [loadingMessage, setLoadingMessage] = useState(null)
  const [infoMessage, setInfoMessage] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl)
      }
    }
  }, [imageUrl])

  const resolveSessionId = useCallback(async () => {
    if (sessionId) {
      return sessionId
    }

    const response = await fetch(`${API_BASE_URL}/session/current`)
    const payload = await response.json().catch(() => null)

    if (!response.ok) {
      throw new Error(payload?.detail ?? 'Сессия не найдена')
    }

    if (!payload?.session_id) {
      throw new Error('Бэкенд не вернул идентификатор сессии')
    }

    setSessionId(payload.session_id)
    return payload.session_id
  }, [sessionId])

  const handleFetchAiImage = useCallback(async () => {
    setError(null)
    setInfoMessage(null)
    setLoadingMessage('Загружаем изображение…')
    try {
      const currentSessionId = await resolveSessionId()
      const response = await fetch(
        `${API_BASE_URL}/ai/run?session_id=${currentSessionId}`,
      )

      if (!response.ok) {
        let errorMessage = 'AI не вернул изображение'
        try {
          const payload = await response.json()
          errorMessage = payload?.detail ?? errorMessage
        } catch {
          if (response.status === 503) {
            errorMessage = 'Модель AI недоступна. Убедитесь, что файл best.pt находится в папке backend/'
          } else if (response.status === 500) {
            errorMessage = 'Ошибка сервера при обработке изображения'
          }
        }
        throw new Error(errorMessage)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setImageUrl((prev) => {
        if (prev) {
          URL.revokeObjectURL(prev)
        }
        return url
      })
    } catch (fetchError) {
      setError(fetchError.message ?? 'Не удалось загрузить изображение')
    } finally {
      setLoadingMessage(null)
    }
  }, [resolveSessionId])

  const handleStartFlight = useCallback(async () => {
    setError(null)
    setInfoMessage(null)
    setLoadingMessage('Стартуем полёт и сбор данных…')
    try {
      const response = await fetch(`${API_BASE_URL}/start/fly`, {
        method: 'POST',
      })

      const payload = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(payload?.detail ?? 'Не удалось запустить полёт')
      }

      if (payload?.session_id) {
        setSessionId(payload.session_id)
      }

      setInfoMessage('Пайплайн съёмки запущен')
    } catch (startError) {
      setError(startError.message ?? 'Сбой запуска полёта')
    } finally {
      setLoadingMessage(null)
    }
  }, [])

  const handleUploadFolderForMetashape = useCallback(async (files) => {
    setError(null)
    setInfoMessage(null)
    setLoadingMessage('Загружаем фотографии и обрабатываем Metashape…')
    try {
      const formData = new FormData()
      Array.from(files).forEach((file) => {
        formData.append('files', file)
      })

      const response = await fetch(`${API_BASE_URL}/data/upload-and-process-metashape`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.detail ?? 'Не удалось обработать фотографии')
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setImageUrl((prev) => {
        if (prev) {
          URL.revokeObjectURL(prev)
        }
        return url
      })

      setInfoMessage('Metashape обработка завершена')
    } catch (uploadError) {
      setError(uploadError.message ?? 'Не удалось загрузить и обработать фотографии')
    } finally {
      setLoadingMessage(null)
    }
  }, [])

  const handleUploadSingleForAI = useCallback(async (file) => {
    setError(null)
    setInfoMessage(null)
    setLoadingMessage('Загружаем фото и обрабатываем AI…')
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/data/upload-and-process-ai`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let errorMessage = 'Не удалось обработать фото'
        try {
          const payload = await response.json()
          errorMessage = payload?.detail ?? errorMessage
        } catch {
          // Если не удалось распарсить JSON, используем статус
          if (response.status === 503) {
            errorMessage = 'Модель AI недоступна. Убедитесь, что файл best.pt находится в папке backend/'
          } else if (response.status === 500) {
            errorMessage = 'Ошибка сервера при обработке изображения'
          }
        }
        throw new Error(errorMessage)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setImageUrl((prev) => {
        if (prev) {
          URL.revokeObjectURL(prev)
        }
        return url
      })

      setInfoMessage('AI обработка завершена')
    } catch (uploadError) {
      setError(uploadError.message ?? 'Не удалось загрузить и обработать фото')
    } finally {
      setLoadingMessage(null)
    }
  }, [])

  const handleClearImage = () => {
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl)
    }
    setImageUrl(null)
    setInfoMessage(null)
  }

  return (
    <div className="app">
      <Header name="Name" />
      <Sidebar
        onFetchAiImage={handleFetchAiImage}
        onStartFlight={handleStartFlight}
        onUploadFolderForMetashape={handleUploadFolderForMetashape}
        onUploadSingleForAI={handleUploadSingleForAI}
        onClearImage={handleClearImage}
        isLoading={Boolean(loadingMessage)}
      />
      <div className="app-status-panel">
        {loadingMessage && <span className="app-status">{loadingMessage}</span>}
        {infoMessage && (
          <span className="app-status app-status--info">{infoMessage}</span>
        )}
        {error && <span className="app-status app-status--error">{error}</span>}
      </div>
      <ImageViewer imageSrc={imageUrl} />
    </div>
  )
}

export default App