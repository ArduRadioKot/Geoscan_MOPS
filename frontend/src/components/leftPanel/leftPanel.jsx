import './leftPanel.css'
import React, { useState, useEffect, useRef } from 'react';

const Sidebar = ({ 
  onFetchAiImage, 
  onStartFlight, 
  onUploadFolderForMetashape,
  onUploadSingleForAI,
  onClearImage, 
  isLoading 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const folderInputRef = useRef(null);
  const singleFileInputRef = useRef(null);

  const toggleSidebar = () => {
    if (!isOpen) {
      setIsVisible(true);
      setTimeout(() => setIsOpen(true), 10);
    } else {
      setIsOpen(false);
      setTimeout(() => setIsVisible(false), 300);
    }
  };

  const handleStartFlight = async () => {
    if (typeof onStartFlight === 'function') {
      await onStartFlight();
    }
    closeSidebar();
  };

  const closeSidebar = () => {
    setIsOpen(false);
    setTimeout(() => setIsVisible(false), 300);
  };

  const handleRequestAiImage = async () => {
    if (typeof onFetchAiImage === 'function') {
      await onFetchAiImage();
    }
    closeSidebar();
  };

  const handleUploadFolderClick = () => {
    folderInputRef.current?.click();
  };

  const handleFolderChange = async (event) => {
    const files = event.target.files;
    if (files && files.length > 0 && typeof onUploadFolderForMetashape === 'function') {
      await onUploadFolderForMetashape(files);
    }
    // Сброс input для возможности повторной загрузки тех же файлов
    if (folderInputRef.current) {
      folderInputRef.current.value = '';
    }
    closeSidebar();
  };

  const handleUploadSingleClick = () => {
    singleFileInputRef.current?.click();
  };

  const handleSingleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (file && typeof onUploadSingleForAI === 'function') {
      await onUploadSingleForAI(file);
    }
    // Сброс input для возможности повторной загрузки того же файла
    if (singleFileInputRef.current) {
      singleFileInputRef.current.value = '';
    }
    closeSidebar();
  };

  const handleClearClick = () => {
    onClearImage();
    closeSidebar();
  };

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.keyCode === 27 && isOpen) {
        closeSidebar();
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen]);

  return (
    <>
      <button 
        className="sidebar-toggle"
        onClick={toggleSidebar}
        aria-label="Открыть меню"
      >
        <span className="sidebar-toggle__line"></span>
        <span className="sidebar-toggle__line"></span>
        <span className="sidebar-toggle__line"></span>
      </button>

      {isVisible && (
        <div 
          className={`sidebar-overlay ${isOpen ? 'sidebar-overlay--active' : ''}`}
          onClick={closeSidebar}
        />
      )}

      <aside 
        className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}
        aria-hidden={!isOpen}
      >
        <div className="sidebar__content">
          <div className="sidebar__header">
            <h2 className="sidebar__title">Навигация</h2>
            <button 
              className="sidebar__close"
              onClick={closeSidebar}
              aria-label="Закрыть меню"
            >
              <span></span>
              <span></span>
            </button>
          </div>

          <nav className="sidebar__nav">
            <ul className="sidebar__menu">
              <li className="sidebar__item">
                <button 
                  className="sidebar__link sidebar__link--button" 
                  onClick={handleStartFlight}
                  disabled={isLoading}
                >
                  <span className="sidebar__icon"></span>
                  <span className="sidebar__text">Старт полёта</span>
                </button>
              </li>
            </ul>
          </nav>

          <div className="image-upload">
            <input
              type="file"
              ref={folderInputRef}
              onChange={handleFolderChange}
              accept="image/*"
              multiple
              style={{ display: 'none' }}
            />
            <input
              type="file"
              ref={singleFileInputRef}
              onChange={handleSingleFileChange}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <button 
              className="upload-btn upload-btn--folder" 
              onClick={handleUploadFolderClick}
              disabled={isLoading}
            >
              {isLoading ? 'Обрабатываем…' : 'Загрузить папку (Metashape)'}
            </button>
            <button 
              className="upload-btn upload-btn--single" 
              onClick={handleUploadSingleClick}
              disabled={isLoading}
            >
              {isLoading ? 'Обрабатываем…' : 'Загрузить фото (AI)'}
            </button>
            <button 
              className="upload-btn" 
              onClick={handleRequestAiImage}
              disabled={isLoading}
            >
              {isLoading ? 'Загружаем…' : 'Загрузить изображение'}
            </button>
            <button className="clear-btn" onClick={handleClearClick}>
              Очистить изображение
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;