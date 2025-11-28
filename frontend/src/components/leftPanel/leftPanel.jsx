import './leftPanel.css'
import React, { useState, useEffect, useRef } from 'react';

const Sidebar = ({ 
  onFetchAiImage, 
  onStartFlight, 
  onUploadFolderForMetashape,
  onUploadSingleForAI,
  onClearImage,
  onDownloadImage,
  hasImage,
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

  const handleDownloadClick = () => {
    if (typeof onDownloadImage === 'function') {
      onDownloadImage();
    }
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
            {hasImage && (
              <button 
                className="download-btn" 
                onClick={handleDownloadClick}
                disabled={isLoading}
              >
                Скачать изображение
              </button>
            )}
            <button className="clear-btn" onClick={handleClearClick}>
              Очистить изображение
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

          <div className="sidebar__footer">
            <a 
              href="https://github.com/ArduRadioKot/Geoscan_MOPS" 
              target="_blank" 
              rel="noopener noreferrer"
              className="sidebar__github-link"
            >
              <svg 
                width="20" 
                height="20" 
                viewBox="0 0 24 24" 
                fill="currentColor"
                className="sidebar__github-icon"
              >
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <span className="sidebar__github-text">GitHub</span>
            </a>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;