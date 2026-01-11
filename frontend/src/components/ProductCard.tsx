import { Product } from '@/types';
import { Package, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import './ProductCard.css';

interface ProductCardProps {
  product: Product;
}

const ProductCard = ({ product }: ProductCardProps) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
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
              className="product-image"
            />
            {product.images.length > 1 && (
              <>
                <button 
                  className="image-nav prev" 
                  onClick={prevImage}
                  aria-label="Previous image"
                >
                  <ChevronLeft size={20} />
                </button>
                <button 
                  className="image-nav next" 
                  onClick={nextImage}
                  aria-label="Next image"
                >
                  <ChevronRight size={20} />
                </button>
                <div className="image-indicators">
                  {product.images.map((_, index) => (
                    <span 
                      key={index}
                      className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                      onClick={() => setCurrentImageIndex(index)}
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
    </div>
  );
};

export default ProductCard;
