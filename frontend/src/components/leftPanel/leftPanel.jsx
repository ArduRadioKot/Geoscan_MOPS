import './leftPanel.css'
import React, { useState, useEffect } from 'react';

const Sidebar = ({ onFetchAiImage, onStartFlight, onClearImage, isLoading }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

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