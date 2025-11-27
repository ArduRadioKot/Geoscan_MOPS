import React, { useState, useRef, useCallback } from 'react';
import './imageViewer.css';

const ImageViewer = ({ image }) => {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const imageRef = useRef(null);
  const containerRef = useRef(null);

  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const zoomSpeed = 0.1;
    const newScale = e.deltaY > 0 
      ? Math.max(0.1, scale - zoomSpeed)
      : Math.min(5, scale + zoomSpeed);
    
    setScale(newScale);
  }, [scale]);

  const handleMouseDown = useCallback((e) => {
    if (scale <= 1) return;
    
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  }, [scale, position]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || scale <= 1) return;

    e.preventDefault(); 

    const newX = e.clientX - dragStart.x;
    const newY = e.clientY - dragStart.y;

    // Ограничение перемещения за пределы изображения
    const containerRect = containerRef.current.getBoundingClientRect();
    const imageRect = imageRef.current.getBoundingClientRect();
    
    const maxX = Math.max(0, (imageRect.width * scale - containerRect.width) / 2);
    const maxY = Math.max(0, (imageRect.height * scale - containerRect.height) / 2);

    setPosition({
      x: Math.max(-maxX, Math.min(maxX, newX)),
      y: Math.max(-maxY, Math.min(maxY, newY))
    });
  }, [isDragging, dragStart, scale]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const zoomIn = () => {
    setScale(prev => Math.min(5, prev + 0.2));
  };

  const zoomOut = () => {
    setScale(prev => Math.max(0.1, prev - 0.2));
  };

  const resetView = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  // Если изображение не загружено, не рендерим компонент
  if (!image) return null;

  const imageUrl = URL.createObjectURL(image);

  return (
    <div 
      className="image-viewer"
      onWheel={handleWheel}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div className="image-viewer__container" ref={containerRef}>
        <img
          ref={imageRef}
          src={imageUrl}
          alt="Просмотр"
          className="image-viewer__img"
          style={{
            transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
            cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default'
          }}
          onMouseDown={handleMouseDown}
        />
        
        <div className="image-viewer__zoom-info">
          {Math.round(scale * 100)}%
        </div>

        <div className="image-viewer__controls">
          <button className="image-viewer__btn" onClick={zoomOut} title="Уменьшить">
            −
          </button>
          <button className="image-viewer__btn" onClick={resetView} title="Сбросить">
            ↺
          </button>
          <button className="image-viewer__btn" onClick={zoomIn} title="Увеличить">
            +
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;