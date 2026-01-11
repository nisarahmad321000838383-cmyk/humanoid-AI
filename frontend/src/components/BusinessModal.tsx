import { useState, useEffect, useRef } from 'react';
import { apiService } from '@/services/api';
import type { Business, BusinessCreateUpdate, Product, ProductCreateUpdate, ProductStats } from '@/types';
import ProductModal from './ProductModal';
import './BusinessModal.css';

interface BusinessModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const BusinessModal = ({ isOpen, onClose }: BusinessModalProps) => {
  const [activeTab, setActiveTab] = useState<'business' | 'products'>('business');
  const [business, setBusiness] = useState<Business | null>(null);
  const [hasBusiness, setHasBusiness] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  const [formData, setFormData] = useState<BusinessCreateUpdate>({
    business_info: '',
    logo: ''
  });
  
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [logoError, setLogoError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Product state
  const [products, setProducts] = useState<Product[]>([]);
  const [productStats, setProductStats] = useState<ProductStats | null>(null);
  const [productsLoading, setProductsLoading] = useState(false);
  const [productModalOpen, setProductModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [productMode, setProductMode] = useState<'create' | 'edit'>('create');

  useEffect(() => {
    if (isOpen) {
      loadBusiness();
      loadProducts();
    }
  }, [isOpen]);

  useEffect(() => {
    if (activeTab === 'products' && hasBusiness) {
      loadProducts();
    }
  }, [activeTab, hasBusiness]);

  const loadBusiness = async () => {
    try {
      setLoading(true);
      const response = await apiService.getMyBusiness();
      
      if (response.has_business && response.business) {
        setBusiness(response.business);
        setHasBusiness(true);
        setFormData({
          business_info: response.business.business_info,
          logo: ''
        });
        
        if (response.business.logo_base64) {
          setLogoPreview(`data:${response.business.logo_content_type || 'image/jpeg'};base64,${response.business.logo_base64}`);
        }
      } else {
        setHasBusiness(false);
        setIsEditing(true);
      }
      
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setHasBusiness(false);
        setIsEditing(true);
      } else {
        setError(err.response?.data?.detail || err.response?.data?.error || 'Failed to load business information');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setLogoError('Please select an image file (PNG, JPG, JPEG, GIF, etc.)');
      return;
    }

    if (file.size > 204800) {
      const sizeKB = (file.size / 1024).toFixed(2);
      setLogoError(`Image size must be less than 200KB. Current size: ${sizeKB}KB. Please compress your image or choose a smaller one.`);
      return;
    }

    setLogoError(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      setFormData({ ...formData, logo: base64String });
      setLogoPreview(base64String);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveLogo = () => {
    setFormData({ ...formData, logo: '' });
    setLogoPreview(null);
    setLogoError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLogoError(null);

    const lines = formData.business_info.trim().split('\n');
    if (lines.length > 10) {
      setError(`Business info must not exceed 10 lines. Current: ${lines.length} lines.`);
      return;
    }

    if (!formData.business_info.trim()) {
      setError('Please provide your business information.');
      return;
    }

    try {
      setSubmitting(true);
      
      if (hasBusiness) {
        const response = await apiService.updateBusiness(formData);
        setBusiness(response.business);
        setSuccess(response.message);
        setIsEditing(false);
      } else {
        const response = await apiService.registerBusiness(formData);
        setBusiness(response.business);
        setHasBusiness(true);
        setSuccess(response.message);
        setIsEditing(false);
      }
      
      await loadBusiness();
    } catch (err: any) {
      const errorData = err.response?.data;
      
      if (errorData?.business_info) {
        setError(Array.isArray(errorData.business_info) ? errorData.business_info[0] : errorData.business_info);
      } else if (errorData?.logo) {
        setLogoError(Array.isArray(errorData.logo) ? errorData.logo[0] : errorData.logo);
      } else if (errorData?.error) {
        setError(errorData.error);
      } else {
        setError('Failed to save business information. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your business registration? This action cannot be undone.')) {
      return;
    }

    try {
      setSubmitting(true);
      const response = await apiService.deleteBusiness();
      setSuccess(response.message);
      setBusiness(null);
      setHasBusiness(false);
      setIsEditing(true);
      setFormData({ business_info: '', logo: '' });
      setLogoPreview(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete business');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelEdit = () => {
    if (hasBusiness && business) {
      setFormData({
        business_info: business.business_info,
        logo: ''
      });
      if (business.logo_base64) {
        setLogoPreview(`data:${business.logo_content_type || 'image/jpeg'};base64,${business.logo_base64}`);
      }
      setIsEditing(false);
      setError(null);
      setLogoError(null);
    }
  };

  const loadProducts = async () => {
    if (!hasBusiness) return;
    
    try {
      setProductsLoading(true);
      const [productsData, statsData] = await Promise.all([
        apiService.getProducts(),
        apiService.getProductStats(),
      ]);
      
      setProducts(productsData || []);
      setProductStats(statsData);
    } catch (err: any) {
      console.error('Failed to load products:', err);
      setProducts([]); // Set empty array on error
      // Don't show error for 404 (no business yet)
      if (err.response?.status !== 404) {
        setError('Failed to load products. Please try again.');
      }
    } finally {
      setProductsLoading(false);
    }
  };

  const handleCreateProduct = () => {
    setSelectedProduct(null);
    setProductMode('create');
    setProductModalOpen(true);
  };

  const handleEditProduct = (product: Product) => {
    setSelectedProduct(product);
    setProductMode('edit');
    setProductModalOpen(true);
  };

  const handleDeleteProduct = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      return;
    }

    try {
      await apiService.deleteProduct(productId);
      setSuccess('Product deleted successfully!');
      await loadProducts();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete product');
    }
  };

  const handleProductSubmit = async (data: ProductCreateUpdate) => {
    try {
      if (productMode === 'create') {
        await apiService.createProduct(data);
        setSuccess('Product created successfully!');
      } else if (selectedProduct) {
        await apiService.updateProduct(selectedProduct.id, data);
        setSuccess('Product updated successfully!');
      }
      await loadProducts();
      setProductModalOpen(false);
    } catch (err: any) {
      throw err; // Let ProductModal handle the error display
    }
  };

  const handleClose = () => {
    setError(null);
    setSuccess(null);
    setLogoError(null);
    setActiveTab('business');
    onClose();
  };

  const lineCount = formData.business_info.trim().split('\n').length;
  const isOverLimit = lineCount > 10;

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content business-modal-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Your Business</h2>
          <button className="modal-close" onClick={handleClose}>&times;</button>
        </div>

        {/* Tabs */}
        {hasBusiness && (
          <div className="modal-tabs">
            <button
              className={`tab-button ${activeTab === 'business' ? 'active' : ''}`}
              onClick={() => setActiveTab('business')}
            >
              Business Info
            </button>
            <button
              className={`tab-button ${activeTab === 'products' ? 'active' : ''}`}
              onClick={() => setActiveTab('products')}
            >
              Your Products {productStats && `(${productStats.total_products}/10)`}
            </button>
          </div>
        )}

        {loading ? (
          <div className="modal-body">
            <div className="loading">Loading business information...</div>
          </div>
        ) : (
          <div className="modal-body">
            {success && (
              <div className="success-message">
                {success}
                <button onClick={() => setSuccess(null)}>&times;</button>
              </div>
            )}

            {error && (
              <div className="error-message">
                {error}
                <button onClick={() => setError(null)}>&times;</button>
              </div>
            )}

            {activeTab === 'business' && !isEditing && hasBusiness && business ? (
              <div className="business-view">
                {logoPreview && (
                  <div className="business-logo-display">
                    <img src={logoPreview} alt="Business Logo" />
                  </div>
                )}
                
                <div className="business-info-display">
                  <h3>Business Information</h3>
                  <div className="business-text">
                    {business.business_info.split('\n').map((line, idx) => (
                      <p key={idx}>{line}</p>
                    ))}
                  </div>
                </div>

                <div className="business-actions">
                  <button 
                    className="btn-primary" 
                    onClick={() => setIsEditing(true)}
                    disabled={submitting}
                  >
                    Edit Business
                  </button>
                  <button 
                    className="btn-danger" 
                    onClick={handleDelete}
                    disabled={submitting}
                  >
                    Delete Business
                  </button>
                </div>
              </div>
            ) : activeTab === 'business' ? (
              <form onSubmit={handleSubmit} className="business-form">
                <div className="form-help-header">
                  Write about your business name, owner, address, and industry (what you produce/buy/sell) in up to 10 lines.
                </div>

                <div className="form-section">
                  <label htmlFor="business_info">
                    Business Information *
                    <span className={`line-counter ${isOverLimit ? 'over-limit' : ''}`}>
                      {lineCount} / 10 lines
                    </span>
                  </label>
                  <textarea
                    id="business_info"
                    value={formData.business_info}
                    onChange={(e) => setFormData({ ...formData, business_info: e.target.value })}
                    placeholder="Example:&#10;Business Name: Tech Solutions Inc.&#10;Owner: John Doe&#10;Address: 123 Main Street, New York, NY 10001&#10;Industry: We provide IT consulting and software development services..."
                    rows={10}
                    required
                    className={isOverLimit ? 'error-input' : ''}
                  />
                  {isOverLimit && (
                    <div className="field-error">
                      Business info exceeds 10 lines. Please reduce the content.
                    </div>
                  )}
                </div>

                <div className="form-section">
                  <label htmlFor="logo">Business Logo (Optional)</label>
                  <div className="form-help">
                    Upload your business logo. Maximum size: 200KB. Supported formats: PNG, JPG, JPEG, GIF.
                  </div>
                  
                  {logoPreview ? (
                    <div className="logo-preview">
                      <img src={logoPreview} alt="Logo Preview" />
                      <button 
                        type="button" 
                        className="btn-remove-logo" 
                        onClick={handleRemoveLogo}
                      >
                        Remove Logo
                      </button>
                    </div>
                  ) : (
                    <div className="file-upload">
                      <input
                        ref={fileInputRef}
                        type="file"
                        id="logo"
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                      <label htmlFor="logo" className="file-upload-label">
                        Choose Logo Image
                      </label>
                    </div>
                  )}
                  
                  {logoError && (
                    <div className="field-error">{logoError}</div>
                  )}
                </div>

                <div className="form-actions">
                  {hasBusiness && (
                    <button 
                      type="button" 
                      className="btn-secondary" 
                      onClick={handleCancelEdit}
                      disabled={submitting}
                    >
                      Cancel
                    </button>
                  )}
                  <button 
                    type="submit" 
                    className="btn-primary" 
                    disabled={submitting || isOverLimit}
                  >
                    {submitting ? 'Saving...' : hasBusiness ? 'Update Business' : 'Register Business'}
                  </button>
                </div>
              </form>
            ) : activeTab === 'products' ? (
              <div className="products-section">
                {productsLoading ? (
                  <div className="loading">Loading products...</div>
                ) : (
                  <>
                    <div className="products-header">
                      <div className="products-stats">
                        {productStats && (
                          <>
                            <span className="stat-item">
                              <strong>{productStats.total_products}</strong> / {productStats.max_products} products
                            </span>
                            {productStats.remaining_slots > 0 && (
                              <span className="stat-item stat-positive">
                                {productStats.remaining_slots} slot{productStats.remaining_slots !== 1 ? 's' : ''} available
                              </span>
                            )}
                          </>
                        )}
                      </div>
                      <button
                        className="btn-primary"
                        onClick={handleCreateProduct}
                        disabled={!productStats?.can_add_more}
                      >
                        {productStats?.can_add_more ? '+ Add Product' : 'Maximum Products Reached'}
                      </button>
                    </div>

                    {products.length === 0 ? (
                      <div className="no-products">
                        <p>No products yet. Add your first product to get started!</p>
                      </div>
                    ) : (
                      <div className="products-grid">
                        {products.map((product) => (
                          <div key={product.id} className="product-card">
                            <div className="product-images">
                              {product.images.length > 0 ? (
                                <img
                                  src={`data:${product.images[0].image_content_type};base64,${product.images[0].image_base64}`}
                                  alt="Product"
                                  className="product-main-image"
                                />
                              ) : (
                                <div className="product-no-image">No Image</div>
                              )}
                              {product.images.length > 1 && (
                                <div className="product-image-count">
                                  +{product.images.length - 1} more
                                </div>
                              )}
                            </div>
                            <div className="product-info">
                              <div className="product-description">
                                {product.product_description.split('\n').slice(0, 3).map((line, idx) => (
                                  <p key={idx}>{line}</p>
                                ))}
                                {product.product_description.split('\n').length > 3 && (
                                  <p className="product-more">...</p>
                                )}
                              </div>
                              <div className="product-actions">
                                <button
                                  className="btn-secondary btn-small"
                                  onClick={() => handleEditProduct(product)}
                                >
                                  Edit
                                </button>
                                <button
                                  className="btn-danger btn-small"
                                  onClick={() => handleDeleteProduct(product.id)}
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : null}
          </div>
        )}

        {/* Product Modal */}
        <ProductModal
          isOpen={productModalOpen}
          onClose={() => setProductModalOpen(false)}
          onSubmit={handleProductSubmit}
          product={selectedProduct}
          mode={productMode}
          remainingSlots={productStats?.remaining_slots || 0}
        />
      </div>
    </div>
  );
};

export default BusinessModal;
