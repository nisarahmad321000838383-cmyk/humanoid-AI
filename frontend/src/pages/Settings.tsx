import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import type { HuggingFaceToken, HuggingFaceTokenCreate, HuggingFaceTokenStats } from '@/types';
import './Settings.css';

const Settings = () => {
  const { user } = useAuthStore();
  const [tokens, setTokens] = useState<HuggingFaceToken[]>([]);
  const [stats, setStats] = useState<HuggingFaceTokenStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingToken, setEditingToken] = useState<HuggingFaceToken | null>(null);
  const [formData, setFormData] = useState<HuggingFaceTokenCreate>({
    token: '',
    name: '',
    is_active: true,
  });

  useEffect(() => {
    loadTokens();
    loadStats();
  }, []);

  const loadTokens = async () => {
    try {
      setLoading(true);
      const data = await apiService.getHFTokens();
      setTokens(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tokens');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await apiService.getHFTokenStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (editingToken) {
        await apiService.updateHFToken(editingToken.id, formData);
      } else {
        await apiService.createHFToken(formData);
      }
      setShowAddModal(false);
      setEditingToken(null);
      setFormData({ token: '', name: '', is_active: true });
      loadTokens();
      loadStats();
    } catch (err: any) {
      setError(err.response?.data?.token?.[0] || err.response?.data?.name?.[0] || 'Failed to save token');
    }
  };

  const handleEdit = (token: HuggingFaceToken) => {
    setEditingToken(token);
    setFormData({
      token: token.token || '',
      name: token.name,
      is_active: token.is_active,
    });
    setShowAddModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this token?')) return;

    try {
      await apiService.deleteHFToken(id);
      loadTokens();
      loadStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete token');
    }
  };

  const handleToggleActive = async (id: number) => {
    try {
      await apiService.toggleHFTokenActive(id);
      loadTokens();
      loadStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle token status');
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingToken(null);
    setFormData({ token: '', name: '', is_active: true });
    setError(null);
  };

  // Check if user is admin (either by is_admin property or role)
  const isAdmin = user?.is_admin || user?.role === 'admin';
  
  if (!isAdmin) {
    return (
      <div className="settings-container">
        <div className="access-denied">
          <h2>Access Denied</h2>
          <p>Only admin users can access settings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>HuggingFace Token Management</h1>
        <button className="btn-primary" onClick={() => setShowAddModal(true)}>
          + Add Token
        </button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_tokens}</div>
            <div className="stat-label">Total Tokens</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.active_tokens}</div>
            <div className="stat-label">Active Tokens</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.inactive_tokens}</div>
            <div className="stat-label">Inactive Tokens</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.active_assignments}</div>
            <div className="stat-label">Active User Sessions</div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>&times;</button>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading tokens...</div>
      ) : (
        <div className="tokens-list">
          {tokens.length === 0 ? (
            <div className="empty-state">
              <p>No tokens added yet. Add your first HuggingFace token to get started.</p>
              <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                Get your token from <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>HuggingFace Settings</a>
              </p>
            </div>
          ) : (
            tokens.map((token) => (
              <div key={token.id} className={`token-card ${!token.is_active ? 'inactive' : ''}`}>
                <div className="token-info">
                  <div className="token-header">
                    <h3>{token.name}</h3>
                    <span className={`status-badge ${token.is_active ? 'active' : 'inactive'}`}>
                      {token.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="token-preview">
                    <code>{token.token_preview || token.token}</code>
                  </div>
                  <div className="token-meta">
                    <span>Created by: {token.created_by_username}</span>
                    <span>Used by {token.assignment_count || 0} active session{(token.assignment_count || 0) !== 1 ? 's' : ''}</span>
                    <span>Created: {new Date(token.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="token-actions">
                  <button className="btn-secondary" onClick={() => handleEdit(token)}>
                    Edit
                  </button>
                  <button 
                    className={`btn-toggle ${token.is_active ? 'deactivate' : 'activate'}`}
                    onClick={() => handleToggleActive(token.id)}
                  >
                    {token.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button className="btn-danger" onClick={() => handleDelete(token.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {showAddModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingToken ? 'Edit Token' : 'Add New Token'}</h2>
              <button className="close-btn" onClick={closeModal}>
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">Token Name *</label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Production Token 1"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="token">HuggingFace Access Token *</label>
                <textarea
                  id="token"
                  value={formData.token}
                  onChange={(e) => setFormData({ ...formData, token: e.target.value })}
                  placeholder="hf_..."
                  rows={3}
                  required
                />
                <small>
                  Enter your HuggingFace API token (starts with hf_). 
                  Get one from <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer">HuggingFace</a>. 
                  Keep it secure!
                </small>
              </div>
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  <span>Active (available for assignment)</span>
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingToken ? 'Update Token' : 'Add Token'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
