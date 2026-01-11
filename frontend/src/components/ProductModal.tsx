import React, { useState, useEffect } from 'react';
import { Product, ProductCreateUpdate } from '@/types';
import './ProductModal.css';

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProductCreateUpdate) => Promise<void>;
  product?: Product | null;
  mode: 'create' | 'edit';
  remainingSlots: number;
}

const ProductModal: React.FC<ProductModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  product,
  mode,
  remainingSlots,
}) => {
  const [productDescription, setProductDescription] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [totalSize, setTotalSize] = useState(0);

  useEffect(() => {
    if (isOpen && product && mode === 'edit') {
      setProductDescription(product.product_description);
      // Set existing images for preview
      const existingPreviews = product.images.map(
        (img) => `data:${img.image_content_type};base64,${img.image_base64}`
      );
      setImagePreviews(existingPreviews);
      setImages(existingPreviews);
    } else if (isOpen && mode === 'create') {
      // Reset form for new product
      setProductDescription('');
      setImages([]);
      setImagePreviews([]);
      setTotalSize(0);
    }
  }, [isOpen, product, mode]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    // Validate file count
    const currentCount = images.length;
    const newCount = files.length;
    if (currentCount + newCount > 4) {
      setError(`Maximum 4 images allowed. You already have ${currentCount} image(s).`);
      return;
    }

    const newImages: string[] = [];
    const newPreviews: string[] = [];
    let newTotalSize = totalSize;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError(`File "${file.name}" is not an image.`);
        continue;
      }

      // Read file as base64
      try {
        const base64 = await fileToBase64(file);
        const dataUrl = `data:${file.type};base64,${base64}`;
        
        // Calculate size
        const fileSize = Math.ceil((base64.length * 3) / 4); // Approximate decoded size
        newTotalSize += fileSize;

        newImages.push(dataUrl);
        newPreviews.push(dataUrl);
      } catch (err) {
        setError(`Failed to read file "${file.name}".`);
        console.error(err);
      }
    }

    // Validate total size (1MB = 1048576 bytes)
    const maxSize = 1048576;
    if (newTotalSize > maxSize) {
      const sizeMB = (newTotalSize / 1048576).toFixed(2);
      setError(`Total size of all images must be less than 1MB. Current: ${sizeMB}MB. Please compress your images.`);
      return;
    }

    setImages([...images, ...newImages]);
    setImagePreviews([...imagePreviews, ...newPreviews]);
    setTotalSize(newTotalSize);
    setError('');
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix to get pure base64
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);
    
    // Recalculate total size
    let newTotalSize = 0;
    newImages.forEach((img) => {
      const base64 = img.split(',')[1];
      newTotalSize += Math.ceil((base64.length * 3) / 4);
    });
    
    setImages(newImages);
    setImagePreviews(newPreviews);
    setTotalSize(newTotalSize);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate description
    if (!productDescription.trim()) {
      setError('Product description is required.');
      return;
    }

    const lines = productDescription.trim().split('\n');
    if (lines.length > 10) {
      setError(`Product description must not exceed 10 lines. Current: ${lines.length} lines.`);
      return;
    }

    // Validate images
    if (images.length === 0) {
      setError('At least 1 image is required.');
      return;
    }

    if (images.length > 4) {
      setError(`Maximum 4 images allowed. You have ${images.length} images.`);
      return;
    }

    // Validate total size
    const maxSize = 1048576; // 1MB
    if (totalSize > maxSize) {
      const sizeMB = (totalSize / 1048576).toFixed(2);
      setError(`Total size of all images must be less than 1MB. Current: ${sizeMB}MB.`);
      return;
    }

    setLoading(true);
    try {
      await onSubmit({
        product_description: productDescription.trim(),
        images: images,
      });
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to save product.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const sizeMB = (totalSize / 1048576).toFixed(2);
  const sizePercent = ((totalSize / 1048576) * 100).toFixed(0);

  return (
    <div className="product-modal-overlay" onClick={onClose}>
      <div className="product-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="product-modal-header">
          <h2>{mode === 'create' ? 'Add New Product' : 'Edit Product'}</h2>
          <button className="product-modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        {mode === 'create' && (
          <div className="product-modal-info">
            <p>You can add up to {remainingSlots} more product(s).</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="product-modal-form">
          {error && <div className="product-modal-error">{error}</div>}

          <div className="product-form-group">
            <label htmlFor="product-description">
              Product Description *
              <span className="product-helper-text">
                (Include product name, price, and specifications - max 10 lines)
              </span>
            </label>
            <textarea
              id="product-description"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              placeholder="Product Name: iPhone 15 Pro&#10;Price: $999&#10;Specifications:&#10;- 6.1-inch display&#10;- A17 Pro chip&#10;- 256GB storage&#10;- Pro camera system"
              rows={10}
              maxLength={2000}
              required
            />
            <div className="product-char-count">
              {productDescription.split('\n').length} / 10 lines
            </div>
          </div>

          <div className="product-form-group">
            <label>
              Product Images *
              <span className="product-helper-text">
                (Min: 1, Max: 4 images | Total size: max 1MB)
              </span>
            </label>
            
            <div className="product-image-upload">
              <input
                type="file"
                id="product-images"
                accept="image/*"
                multiple
                onChange={handleFileChange}
                disabled={images.length >= 4}
              />
              <label htmlFor="product-images" className={`product-upload-btn ${images.length >= 4 ? 'disabled' : ''}`}>
                {images.length >= 4 ? 'Maximum 4 Images' : 'Choose Images'}
              </label>
            </div>

            {/* Size indicator */}
            {totalSize > 0 && (
              <div className="product-size-indicator">
                <div className="product-size-bar">
                  <div 
                    className={`product-size-fill ${Number(sizePercent) > 90 ? 'warning' : ''}`}
                    style={{ width: `${Math.min(Number(sizePercent), 100)}%` }}
                  ></div>
                </div>
                <div className="product-size-text">
                  {sizeMB} MB / 1.00 MB ({sizePercent}%)
                </div>
              </div>
            )}

            {/* Image previews */}
            {imagePreviews.length > 0 && (
              <div className="product-image-previews">
                {imagePreviews.map((preview, index) => (
                  <div key={index} className="product-image-preview">
                    <img src={preview} alt={`Preview ${index + 1}`} />
                    <button
                      type="button"
                      className="product-image-remove"
                      onClick={() => removeImage(index)}
                      title="Remove image"
                    >
                      &times;
                    </button>
                    <div className="product-image-number">{index + 1}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="product-modal-actions">
            <button
              type="button"
              className="product-btn product-btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="product-btn product-btn-primary"
              disabled={loading}
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Add Product' : 'Update Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductModal;
