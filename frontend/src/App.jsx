import { useState } from 'react'
import './App.css'
import Header from './components/header/header'
import Sidebar from './components/leftPanel/leftPanel'
import ImageViewer from './components/imageViewer/imageViewer'

function App() {
  const [image, setImage] = useState(null)

  const handleImageUpload = (file) => {
    setImage(file)
  }

  const handleClearImage = () => {
    setImage(null)
  }

  return (
   <div className="app">
      <Header name="Name" />
      <Sidebar onImageUpload={handleImageUpload} onClearImage={handleClearImage} />
      <ImageViewer image={image} />
   </div>
  )
}

export default App