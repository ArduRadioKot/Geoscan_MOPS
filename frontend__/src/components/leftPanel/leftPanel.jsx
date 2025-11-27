import './leftPanel.css'
import React, { useState, useEffect, useRef } from 'react';

const Sidebar = ({ onImageUpload, onClearImage }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const fileInputRef = useRef(null);

  const toggleSidebar = () => {
    if (!isOpen) {
      setIsVisible(true);
      setTimeout(() => setIsOpen(true), 10);
    } else {
      setIsOpen(false);
      setTimeout(() => setIsVisible(false), 300);
    }
  };

  const closeSidebar = () => {
    setIsOpen(false);
    setTimeout(() => setIsVisible(false), 300);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      onImageUpload(file);
      closeSidebar();
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
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
                <a href="#home" className="sidebar__link" onClick={closeSidebar}>
                  <span className="sidebar__icon"></span>
                  <span className="sidebar__text">Главная</span>
                </a>
              </li>
            </ul>
          </nav>

          <div className="image-upload">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <button className="upload-btn" onClick={handleUploadClick}>
              Загрузить изображение
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