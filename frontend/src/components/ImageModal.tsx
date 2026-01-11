import { useState, useEffect, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { ProductImage } from '@/types';
import './ImageModal.css';

interface ImageModalProps {
  images: ProductImage[];
  initialIndex: number;
  isOpen: boolean;
  onClose: () => void;
  productName: string;
}

const ImageModal = ({ images, initialIndex, isOpen, onClose, productName }: ImageModalProps) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentIndex(initialIndex);
    }
  }, [isOpen, initialIndex]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (!isOpen) return;
    
    switch (e.key) {
      case 'Escape':
        onClose();
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        setCurrentIndex(prev => prev === 0 ? images.length - 1 : prev - 1);
        break;
      case 'ArrowRight':
      case 'ArrowDown':
        setCurrentIndex(prev => prev === images.length - 1 ? 0 : prev + 1);
        break;
    }
  }, [isOpen, images.length, onClose]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen || images.length === 0) return null;

  const currentImage = images[currentIndex];

  // Format base64 image data with proper data URI prefix
  const getImageSrc = (imageBase64: string, contentType: string) => {
    if (imageBase64.startsWith('data:')) {
      return imageBase64;
    }
    return `data:${contentType};base64,${imageBase64}`;
  };

  const handlePrev = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentIndex(prev => prev === 0 ? images.length - 1 : prev - 1);
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCurrentIndex(prev => prev === images.length - 1 ? 0 : prev + 1);
  };

  return (
    <div className="image-modal-overlay">
      {/* Close button - always visible */}
      <button className="image-modal-close" onClick={onClose} aria-label="Close">
        <X size={28} />
        <span>Close</span>
      </button>

      {/* Navigation for multiple images */}
      {images.length > 1 && (
        <>
          <button className="image-modal-nav prev" onClick={handlePrev} aria-label="Previous">
            <ChevronLeft size={40} />
          </button>
          <button className="image-modal-nav next" onClick={handleNext} aria-label="Next">
            <ChevronRight size={40} />
          </button>
          
          {/* Image counter */}
          <div className="image-modal-counter">
            {currentIndex + 1} / {images.length}
          </div>
        </>
      )}

      {/* Expanded Image - 5x larger */}
      <div className="image-modal-content">
        <img
          src={getImageSrc(currentImage.image_base64, currentImage.image_content_type)}
          alt={`${productName} - Image ${currentIndex + 1}`}
          className="image-modal-expanded"
          draggable={false}
        />
      </div>
    </div>
  );
};

export default ImageModal;
