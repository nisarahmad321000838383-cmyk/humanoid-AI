import { Product } from '@/types';
import { Package, ChevronLeft, ChevronRight, Building2, MapPin, User, Expand } from 'lucide-react';
import { useState } from 'react';
import ImageModal from './ImageModal';
import './ProductCard.css';

interface ProductCardProps {
  product: Product;
}

const ProductCard = ({ product }: ProductCardProps) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const nextImage = () => {
    setCurrentImageIndex((prev) => 
      prev === product.images.length - 1 ? 0 : prev + 1
    );
  };
  
  const prevImage = () => {
    setCurrentImageIndex((prev) => 
      prev === 0 ? product.images.length - 1 : prev - 1
    );
  };

  // Format base64 image data with proper data URI prefix
  const getImageSrc = (imageBase64: string, contentType: string) => {
    // If already has data: prefix, return as is
    if (imageBase64.startsWith('data:')) {
      return imageBase64;
    }
    // Otherwise, add the prefix
    return `data:${contentType};base64,${imageBase64}`;
  };

  // Parse product description to extract name, price, and details
  const lines = product.product_description.split('\n').filter(line => line.trim());
  const productName = lines[0]?.replace(/^Product Name:\s*/i, '').trim() || 'Product';
  const productPrice = lines.find(line => line.toLowerCase().includes('price'))
    ?.replace(/^Price:\s*/i, '').trim();
  const specifications = lines.slice(2).join('\n');

  // Get business info
  const businessInfo = product.business_info;

  const openModal = () => {
    if (product.images.length > 0) {
      setIsModalOpen(true);
    }
  };

  return (
    <div className="product-card">
      <div className="product-image-container">
        {product.images.length > 0 ? (
          <>
            <img 
              src={getImageSrc(
                product.images[currentImageIndex].image_base64,
                product.images[currentImageIndex].image_content_type
              )} 
              alt={productName}
              className="product-image clickable"
              onClick={openModal}
            />
            {/* Expand button */}
            <button 
              className="image-expand-btn"
              onClick={openModal}
              aria-label="Expand image"
            >
              <Expand size={18} />
            </button>
            {product.images.length > 1 && (
              <>
                <button 
                  className="image-nav prev" 
                  onClick={(e) => { e.stopPropagation(); prevImage(); }}
                  aria-label="Previous image"
                >
                  <ChevronLeft size={20} />
                </button>
                <button 
                  className="image-nav next" 
                  onClick={(e) => { e.stopPropagation(); nextImage(); }}
                  aria-label="Next image"
                >
                  <ChevronRight size={20} />
                </button>
                <div className="image-indicators">
                  {product.images.map((_, index) => (
                    <span 
                      key={index}
                      className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                      onClick={(e) => { e.stopPropagation(); setCurrentImageIndex(index); }}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="no-image">
            <Package size={48} />
            <span>No image available</span>
          </div>
        )}
      </div>
      
      <div className="product-details">
        <h3 className="product-name">{productName}</h3>
        {productPrice && (
          <div className="product-price">{productPrice}</div>
        )}
        
        {/* Business Information Section */}
        {businessInfo && (
          <div className="product-business-info">
            <div className="business-header">
              {businessInfo.logo_base64 && businessInfo.logo_content_type ? (
                <img 
                  src={getImageSrc(businessInfo.logo_base64, businessInfo.logo_content_type)}
                  alt={businessInfo.company_name}
                  className="business-logo"
                />
              ) : (
                <div className="business-logo-placeholder">
                  <Building2 size={20} />
                </div>
              )}
              <div className="business-name-container">
                <span className="business-name">{businessInfo.company_name}</span>
                <span className="business-owner">
                  <User size={12} />
                  {businessInfo.owner_username}
                </span>
              </div>
            </div>
            {businessInfo.address && (
              <div className="business-address">
                <MapPin size={14} />
                <span>{businessInfo.address}</span>
              </div>
            )}
          </div>
        )}
        
        {specifications && (
          <div className="product-specs">
            <pre>{specifications}</pre>
          </div>
        )}
        <div className="product-meta">
          <span className="product-id">ID: {product.id}</span>
          <span className="product-images-count">
            {product.images_count} {product.images_count === 1 ? 'image' : 'images'}
          </span>
        </div>
      </div>

      {/* Image Modal for expanded view */}
      <ImageModal
        images={product.images}
        initialIndex={currentImageIndex}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        productName={productName}
      />
    </div>
  );
};

export default ProductCard;
